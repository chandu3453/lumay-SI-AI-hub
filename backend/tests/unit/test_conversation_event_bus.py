"""ConversationEventBus unit tests (Sprint 28 Phase 3 — real-time sync)."""

import asyncio

import pytest

from domains.conversation.event_bus import (
    ConversationEventBus,
    ConversationRealtimeEvent,
    publish_conversation_event,
)


@pytest.fixture(autouse=True)
def _reset_bus():
    ConversationEventBus._subscribers = []
    ConversationEventBus.clear()
    yield
    ConversationEventBus._subscribers = []
    ConversationEventBus.clear()


class TestConversationEventBus:
    def test_subscribe_returns_a_queue(self) -> None:
        q = ConversationEventBus.subscribe()
        assert isinstance(q, asyncio.Queue)
        assert q in ConversationEventBus._subscribers

    def test_unsubscribe_removes_the_queue(self) -> None:
        q = ConversationEventBus.subscribe()
        ConversationEventBus.unsubscribe(q)
        assert q not in ConversationEventBus._subscribers

    def test_unsubscribe_unknown_queue_is_a_noop(self) -> None:
        ConversationEventBus.unsubscribe(asyncio.Queue())  # must not raise

    @pytest.mark.asyncio
    async def test_publish_delivers_to_subscriber(self) -> None:
        q = ConversationEventBus.subscribe()
        event = ConversationRealtimeEvent("conv-1", "message", {"content": "hi"})
        ConversationEventBus.publish(event)

        received = q.get_nowait()
        assert received is event
        assert received.conversation_id == "conv-1"
        assert received.event_type == "message"
        assert received.data == {"content": "hi"}

    @pytest.mark.asyncio
    async def test_publish_fans_out_to_all_subscribers(self) -> None:
        q1 = ConversationEventBus.subscribe()
        q2 = ConversationEventBus.subscribe()
        ConversationEventBus.publish(ConversationRealtimeEvent("conv-1", "status_changed"))

        assert q1.get_nowait().conversation_id == "conv-1"
        assert q2.get_nowait().conversation_id == "conv-1"

    def test_get_recent_filters_by_conversation_id(self) -> None:
        ConversationEventBus.publish(ConversationRealtimeEvent("conv-1", "message"))
        ConversationEventBus.publish(ConversationRealtimeEvent("conv-2", "message"))
        ConversationEventBus.publish(ConversationRealtimeEvent("conv-1", "status_changed"))

        recent = ConversationEventBus.get_recent("conv-1")
        assert len(recent) == 2
        assert all(e["conversation_id"] == "conv-1" for e in recent)

    def test_get_recent_unfiltered_returns_everything(self) -> None:
        ConversationEventBus.publish(ConversationRealtimeEvent("conv-1", "message"))
        ConversationEventBus.publish(ConversationRealtimeEvent("conv-2", "message"))

        assert len(ConversationEventBus.get_recent()) == 2

    def test_history_ring_buffer_caps_at_max_all_events(self) -> None:
        ConversationEventBus._max_all_events = 5
        try:
            for i in range(10):
                ConversationEventBus.publish(ConversationRealtimeEvent(f"conv-{i}", "message"))
            assert len(ConversationEventBus._all_events) == 5
            # Keeps the most recent, drops the oldest.
            assert ConversationEventBus._all_events[0].conversation_id == "conv-5"
        finally:
            ConversationEventBus._max_all_events = 1000

    def test_history_ring_buffer_caps_per_conversation(self) -> None:
        ConversationEventBus._max_events_per_conversation = 3
        try:
            for i in range(6):
                ConversationEventBus.publish(ConversationRealtimeEvent("conv-1", "message", {"i": i}))
            recent = ConversationEventBus.get_recent("conv-1", limit=10)
            assert len(recent) == 3
            assert [e["data"]["i"] for e in recent] == [3, 4, 5]
        finally:
            ConversationEventBus._max_events_per_conversation = 200

    def test_chatty_conversation_does_not_evict_another_conversations_history(self) -> None:
        # The bug this guards against: a global ring buffer let a busy
        # conversation push a quiet one's catch-up history out entirely.
        ConversationEventBus.publish(ConversationRealtimeEvent("conv-quiet", "message"))
        for _ in range(50):
            ConversationEventBus.publish(ConversationRealtimeEvent("conv-busy", "message"))

        recent = ConversationEventBus.get_recent("conv-quiet")
        assert len(recent) == 1
        assert recent[0]["conversation_id"] == "conv-quiet"

    def test_publish_conversation_event_helper_never_raises(self, mocker) -> None:
        mocker.patch.object(
            ConversationEventBus, "publish", side_effect=RuntimeError("boom")
        )
        publish_conversation_event("conv-1", "message", {"x": 1})  # must not raise

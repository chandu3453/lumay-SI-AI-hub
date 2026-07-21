"""Conversation Event Bus — broadcasts live conversation updates to SSE
subscribers (Sprint 28 Phase 3). Structurally identical to `DemoEventBus`
(`app/demo/event_bus.py`) — same in-process `asyncio.Queue` fan-out, same
ring-buffer history for reconnect catch-up. This is the backend half of
"reuse existing WebSocket infrastructure": there is no WebSocket server
anywhere in this codebase (confirmed), so real-time here follows the one
push-based pattern that already exists (SSE + asyncio.Queue), not a new
transport.
"""

import asyncio
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from app.platform.logging import get_logger

logger = get_logger(__name__)


class ConversationRealtimeEvent:
    def __init__(
        self,
        conversation_id: str,
        event_type: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        self.id: str = uuid4().hex[:12]
        self.conversation_id: str = conversation_id
        self.event_type: str = event_type
        self.data: dict[str, Any] = data or {}
        self.timestamp: str = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp,
        }


class ConversationEventBus:
    _subscribers: list[asyncio.Queue] = []
    # Per-conversation ring buffers so one chatty conversation's events can't
    # crowd out another conversation's reconnect catch-up history (each
    # conversation keeps its own history independent of total demo traffic).
    _events_by_conversation: dict[str, list[ConversationRealtimeEvent]] = {}
    _all_events: list[ConversationRealtimeEvent] = []
    _max_events_per_conversation: int = 200
    _max_all_events: int = 1000

    @classmethod
    def subscribe(cls) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        cls._subscribers.append(q)
        return q

    @classmethod
    def unsubscribe(cls, q: asyncio.Queue) -> None:
        if q in cls._subscribers:
            cls._subscribers.remove(q)

    @classmethod
    def publish(cls, event: ConversationRealtimeEvent) -> None:
        cls._all_events.append(event)
        if len(cls._all_events) > cls._max_all_events:
            cls._all_events = cls._all_events[-cls._max_all_events :]

        bucket = cls._events_by_conversation.setdefault(event.conversation_id, [])
        bucket.append(event)
        if len(bucket) > cls._max_events_per_conversation:
            del bucket[: len(bucket) - cls._max_events_per_conversation]

        for q in cls._subscribers[:]:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass
        logger.debug(
            "conversation_realtime_event_published",
            conversation_id=event.conversation_id,
            event_type=event.event_type,
        )

    @classmethod
    def get_recent(cls, conversation_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if conversation_id is not None:
            events = cls._events_by_conversation.get(conversation_id, [])
        else:
            events = cls._all_events
        return [e.to_dict() for e in events[-limit:]]

    @classmethod
    def clear(cls) -> None:
        cls._events_by_conversation.clear()
        cls._all_events.clear()


def publish_conversation_event(
    conversation_id: str, event_type: str, data: dict[str, Any] | None = None
) -> None:
    """Fire-and-forget publish — never raises, so a live-update failure can
    never break the mutation that triggered it (same fail-open philosophy as
    every `integration_hooks.py` function)."""
    try:
        ConversationEventBus.publish(
            ConversationRealtimeEvent(conversation_id=conversation_id, event_type=event_type, data=data)
        )
    except Exception as exc:
        logger.warning("conversation_realtime_publish_failed", error=str(exc), event_type=event_type)

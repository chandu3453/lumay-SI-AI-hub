"""PresenceRegistry unit tests (Sprint 28 Phase 4)."""

import uuid

import pytest

from domains.conversation.presence import PresenceRegistry


@pytest.fixture
def registry() -> PresenceRegistry:
    return PresenceRegistry()


@pytest.mark.asyncio
class TestPresenceRegistry:
    async def test_set_and_get_presence(self, registry: PresenceRegistry) -> None:
        conversation_id = str(uuid.uuid4())
        await registry.set_presence(conversation_id, "employee", "emp-1", "online")

        snapshot = registry.get_snapshot(conversation_id)
        assert snapshot["presence"]["employee"]["emp-1"] == "online"

    async def test_offline_status_is_reported_even_when_fresh(
        self, registry: PresenceRegistry,
    ) -> None:
        conversation_id = str(uuid.uuid4())
        await registry.set_presence(conversation_id, "customer", "cust-1", "online")
        await registry.set_presence(conversation_id, "customer", "cust-1", "offline")

        snapshot = registry.get_snapshot(conversation_id)
        assert snapshot["presence"]["customer"]["cust-1"] == "offline"

    async def test_unknown_conversation_returns_empty_snapshot(
        self, registry: PresenceRegistry,
    ) -> None:
        snapshot = registry.get_snapshot(str(uuid.uuid4()))
        assert snapshot == {"presence": {}, "typing": {}}

    async def test_set_and_get_typing(self, registry: PresenceRegistry) -> None:
        conversation_id = str(uuid.uuid4())
        await registry.set_typing(conversation_id, "ai", True)

        snapshot = registry.get_snapshot(conversation_id)
        assert snapshot["typing"]["ai"] is True

    async def test_typing_false_is_reported(self, registry: PresenceRegistry) -> None:
        conversation_id = str(uuid.uuid4())
        await registry.set_typing(conversation_id, "employee", True)
        await registry.set_typing(conversation_id, "employee", False)

        snapshot = registry.get_snapshot(conversation_id)
        assert snapshot["typing"]["employee"] is False

    async def test_clear_conversation_removes_all_state(
        self, registry: PresenceRegistry,
    ) -> None:
        conversation_id = str(uuid.uuid4())
        await registry.set_presence(conversation_id, "employee", "emp-1", "online")
        await registry.set_typing(conversation_id, "employee", True)

        await registry.clear_conversation(conversation_id)

        snapshot = registry.get_snapshot(conversation_id)
        assert snapshot == {"presence": {}, "typing": {}}

    async def test_conversations_are_isolated(self, registry: PresenceRegistry) -> None:
        conv_a, conv_b = str(uuid.uuid4()), str(uuid.uuid4())
        await registry.set_presence(conv_a, "employee", "emp-1", "online")

        assert registry.get_snapshot(conv_b) == {"presence": {}, "typing": {}}

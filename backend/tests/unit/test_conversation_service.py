"""Conversation service unit tests."""

import uuid

import pytest

from domains.conversation.constants.conversation_constants import (
    ConversationChannel,
    ConversationStatus,
)
from domains.conversation.events.conversation_events import (
    ConversationAssignedEvent,
    ConversationClosedEvent,
    ConversationCreatedEvent,
    ConversationStatusChangedEvent,
)
from domains.conversation.exceptions.conversation_exceptions import (
    ConversationNotFoundError,
    InvalidConversationTransitionError,
)
from domains.conversation.schemas.conversation_schemas import ConversationCreate
from domains.conversation.services.conversation_service import ConversationService


@pytest.fixture
async def service(mocker) -> ConversationService:
    mock_repo = mocker.AsyncMock()
    mock_repo.create.return_value = mocker.Mock(
        id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        policy_id=None,
        complaint_id=None,
        current_status=ConversationStatus.NEW,
        current_channel=ConversationChannel.WEB_CHAT,
        assigned_employee_id=None,
        ai_handling=True,
        human_handling=False,
    )
    mock_repo.get_by_id.return_value = mocker.Mock(
        id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        current_status=ConversationStatus.ACTIVE,
        current_channel=ConversationChannel.WEB_CHAT,
        assigned_employee_id=None,
        complaint_id=None,
        ai_handling=True,
        human_handling=False,
    )
    mock_repo.update.return_value = mocker.Mock(
        id=uuid.uuid4(),
        customer_id=uuid.uuid4(),
        current_status=ConversationStatus.AI_HANDLING,
        current_channel=ConversationChannel.WEB_CHAT,
        assigned_employee_id=None,
        complaint_id=None,
        ai_handling=True,
        human_handling=False,
    )
    return ConversationService(repository=mock_repo)


@pytest.mark.asyncio
class TestConversationService:
    async def test_create_conversation_returns_entity_and_event(
        self, service: ConversationService,
    ) -> None:
        data = ConversationCreate(current_channel=ConversationChannel.WEB_CHAT)
        conversation, events = await service.create_conversation(data)
        assert conversation is not None
        assert len(events) == 1
        assert isinstance(events[0], ConversationCreatedEvent)

    async def test_get_conversation_found(self, service: ConversationService) -> None:
        conversation = await service.get_conversation(uuid.uuid4())
        assert conversation is not None

    async def test_get_conversation_not_found_raises(
        self, service: ConversationService,
    ) -> None:
        service._repository.get_by_id.return_value = None
        with pytest.raises(ConversationNotFoundError):
            await service.get_conversation(uuid.uuid4())

    async def test_update_status_valid_transition(
        self, service: ConversationService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            id=uuid.uuid4(), current_status=ConversationStatus.NEW,
        )
        conversation, events = await service.update_status(
            uuid.uuid4(), ConversationStatus.AI_HANDLING
        )
        assert conversation is not None
        assert len(events) == 1
        assert isinstance(events[0], ConversationStatusChangedEvent)
        # Entering AI_HANDLING auto-sets the handling flags.
        assert service._repository.update.call_args.kwargs["ai_handling"] is True
        assert service._repository.update.call_args.kwargs["human_handling"] is False

    async def test_update_status_invalid_transition_raises(
        self, service: ConversationService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            id=uuid.uuid4(), current_status=ConversationStatus.CLOSED,
        )
        # CLOSED's only reachable target is ACTIVE (Phase 3 "Reopen" action) —
        # anything else must still be rejected.
        with pytest.raises(InvalidConversationTransitionError):
            await service.update_status(uuid.uuid4(), ConversationStatus.ESCALATED)

    async def test_reopen_closed_conversation_via_active(
        self, service: ConversationService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            id=uuid.uuid4(), current_status=ConversationStatus.CLOSED,
        )
        conversation, events = await service.update_status(uuid.uuid4(), ConversationStatus.ACTIVE)
        assert conversation is not None
        assert len(events) == 1

    async def test_assign_employee_returns_entity_and_event(
        self, service: ConversationService,
    ) -> None:
        employee_id = uuid.uuid4()
        conversation, events = await service.assign_employee(uuid.uuid4(), employee_id)
        assert conversation is not None
        assert len(events) == 1
        assert isinstance(events[0], ConversationAssignedEvent)

    async def test_close_conversation_returns_entity_and_event(
        self, service: ConversationService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            id=uuid.uuid4(), current_status=ConversationStatus.ACTIVE,
        )
        conversation, events = await service.close_conversation(uuid.uuid4())
        assert conversation is not None
        assert len(events) == 1
        assert isinstance(events[0], ConversationClosedEvent)

    async def test_close_conversation_invalid_transition_raises(
        self, service: ConversationService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            id=uuid.uuid4(), current_status=ConversationStatus.CLOSED,
        )
        with pytest.raises(InvalidConversationTransitionError):
            await service.close_conversation(uuid.uuid4())

    async def test_list_conversations(self, service: ConversationService) -> None:
        service._repository.list.return_value = ([], 0)
        items, total = await service.list_conversations()
        assert items == []
        assert total == 0

    async def test_take_over_transition_new_to_human_handling(
        self, service: ConversationService, mocker,
    ) -> None:
        # A brand-new conversation (no AI turn yet) must still be directly
        # take-over-able — this is the exact transition take_over_conversation
        # exercises when an employee grabs a conversation immediately.
        service._repository.get_by_id.return_value = mocker.Mock(
            id=uuid.uuid4(), current_status=ConversationStatus.NEW,
        )
        conversation, events = await service.update_status(
            uuid.uuid4(), ConversationStatus.HUMAN_HANDLING
        )
        assert conversation is not None
        assert len(events) == 1
        assert service._repository.update.call_args.kwargs["human_handling"] is True

    async def test_release_transition_human_handling_to_ai_handling(
        self, service: ConversationService, mocker,
    ) -> None:
        # release_conversation always calls this from HUMAN_HANDLING — must
        # be a legal transition or every release call 422s.
        service._repository.get_by_id.return_value = mocker.Mock(
            id=uuid.uuid4(), current_status=ConversationStatus.HUMAN_HANDLING,
        )
        conversation, events = await service.update_status(
            uuid.uuid4(), ConversationStatus.AI_HANDLING
        )
        assert conversation is not None
        assert len(events) == 1
        assert service._repository.update.call_args.kwargs["ai_handling"] is True

    async def test_release_employee_clears_assignment(
        self, service: ConversationService, mocker,
    ) -> None:
        conversation_id = uuid.uuid4()
        service._repository.clear_assigned_employee.return_value = mocker.Mock(
            id=conversation_id, assigned_employee_id=None,
        )
        conversation = await service.release_employee(conversation_id)
        assert conversation.assigned_employee_id is None
        service._repository.clear_assigned_employee.assert_awaited_once_with(conversation_id)

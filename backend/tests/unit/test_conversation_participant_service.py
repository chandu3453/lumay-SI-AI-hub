"""ConversationParticipantService unit tests — the de-duplication guarantee."""

import uuid

import pytest

from domains.conversation.constants.conversation_constants import ConversationParticipantType
from domains.conversation.services.participant_service import ConversationParticipantService


@pytest.fixture
async def service(mocker) -> ConversationParticipantService:
    mock_repo = mocker.AsyncMock()
    return ConversationParticipantService(repository=mock_repo)


@pytest.mark.asyncio
class TestConversationParticipantService:
    async def test_ensure_participant_creates_when_absent(
        self, service: ConversationParticipantService, mocker,
    ) -> None:
        service._repository.get_by_conversation_and_ref.return_value = None
        created = mocker.Mock(id=uuid.uuid4())
        service._repository.create.return_value = created

        conversation_id = uuid.uuid4()
        result = await service.ensure_participant(
            conversation_id, ConversationParticipantType.EMPLOYEE, "agent-1"
        )

        assert result is created
        service._repository.create.assert_awaited_once()
        kwargs = service._repository.create.call_args.kwargs
        assert kwargs["conversation_id"] == conversation_id
        assert kwargs["participant_type"] == ConversationParticipantType.EMPLOYEE
        assert kwargs["participant_ref"] == "agent-1"

    async def test_ensure_participant_is_a_noop_when_already_present(
        self, service: ConversationParticipantService, mocker,
    ) -> None:
        existing = mocker.Mock(id=uuid.uuid4())
        service._repository.get_by_conversation_and_ref.return_value = existing

        result = await service.ensure_participant(
            uuid.uuid4(), ConversationParticipantType.EMPLOYEE, "agent-1"
        )

        assert result is existing
        service._repository.create.assert_not_awaited()

    async def test_ensure_participant_dedup_key_is_type_and_ref(
        self, service: ConversationParticipantService, mocker,
    ) -> None:
        service._repository.get_by_conversation_and_ref.return_value = None
        service._repository.create.return_value = mocker.Mock(id=uuid.uuid4())
        conversation_id = uuid.uuid4()

        await service.ensure_participant(
            conversation_id, ConversationParticipantType.EMPLOYEE, "agent-2", role="assignee"
        )

        service._repository.get_by_conversation_and_ref.assert_awaited_once_with(
            conversation_id, ConversationParticipantType.EMPLOYEE, "agent-2"
        )

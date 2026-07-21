"""ConversationMessage service unit tests."""

import uuid

import pytest

from domains.conversation.constants.conversation_constants import (
    ConversationChannel,
    ConversationMessageType,
    ConversationParticipantType,
)
from domains.conversation.exceptions.conversation_exceptions import (
    MessageNotEditableError,
    MessageNotFoundError,
)
from domains.conversation.services.message_service import MessageService


@pytest.fixture
async def service(mocker) -> MessageService:
    mock_repo = mocker.AsyncMock()
    mock_repo.create.return_value = mocker.Mock(
        id=uuid.uuid4(),
        conversation_id=uuid.uuid4(),
        sender_type=ConversationParticipantType.CUSTOMER,
        channel=ConversationChannel.WEB_CHAT,
        message_type=ConversationMessageType.TEXT,
        content="Hello",
        message_metadata=None,
    )
    return MessageService(repository=mock_repo)


@pytest.mark.asyncio
class TestMessageService:
    async def test_add_message_defaults_to_text(self, service: MessageService) -> None:
        conversation_id = uuid.uuid4()
        message = await service.add_message(
            conversation_id,
            ConversationParticipantType.CUSTOMER,
            ConversationChannel.WEB_CHAT,
            "Hello",
        )
        assert message is not None
        kwargs = service._repository.create.call_args.kwargs
        assert kwargs["conversation_id"] == conversation_id
        assert kwargs["message_type"] == ConversationMessageType.TEXT

    async def test_add_message_transcript_type(self, service: MessageService) -> None:
        conversation_id = uuid.uuid4()
        await service.add_message(
            conversation_id,
            ConversationParticipantType.AI,
            ConversationChannel.VOICE,
            "Segment text",
            message_type=ConversationMessageType.TRANSCRIPT,
        )
        kwargs = service._repository.create.call_args.kwargs
        assert kwargs["message_type"] == ConversationMessageType.TRANSCRIPT
        assert kwargs["sender_type"] == ConversationParticipantType.AI

    async def test_list_messages(self, service: MessageService) -> None:
        service._repository.list_by_conversation.return_value = ([], 0)
        items, total = await service.list_messages(uuid.uuid4())
        assert items == []
        assert total == 0

    async def test_update_message_not_found_raises(
        self, service: MessageService,
    ) -> None:
        service._repository.get_by_id.return_value = None
        with pytest.raises(MessageNotFoundError):
            await service.update_message(uuid.uuid4(), "edited")

    async def test_update_message_rejects_customer_visible_message(
        self, service: MessageService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            id=uuid.uuid4(), message_metadata=None,
        )
        with pytest.raises(MessageNotEditableError):
            await service.update_message(uuid.uuid4(), "edited")
        service._repository.update.assert_not_awaited()

    async def test_update_message_allows_internal_note(
        self, service: MessageService, mocker,
    ) -> None:
        message_id = uuid.uuid4()
        service._repository.get_by_id.return_value = mocker.Mock(
            id=message_id, message_metadata={"internal": True},
        )
        service._repository.update.return_value = mocker.Mock(
            id=message_id, content="edited", message_metadata={"internal": True},
        )
        updated = await service.update_message(message_id, "edited")
        assert updated.content == "edited"
        service._repository.update.assert_awaited_once_with(message_id, content="edited")

    async def test_delete_message_rejects_customer_visible_message(
        self, service: MessageService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            id=uuid.uuid4(), message_metadata={"internal": False},
        )
        with pytest.raises(MessageNotEditableError):
            await service.delete_message(uuid.uuid4())
        service._repository.update.assert_not_awaited()

    async def test_delete_message_soft_deletes_internal_note(
        self, service: MessageService, mocker,
    ) -> None:
        message_id = uuid.uuid4()
        service._repository.get_by_id.return_value = mocker.Mock(
            id=message_id, message_metadata={"internal": True},
        )
        service._repository.update.return_value = mocker.Mock(
            id=message_id, message_metadata={"internal": True, "deleted": True},
        )
        updated = await service.delete_message(message_id)
        assert updated.message_metadata["deleted"] is True
        kwargs = service._repository.update.call_args.kwargs
        assert kwargs["message_metadata"] == {"internal": True, "deleted": True}

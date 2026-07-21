"""ConversationMessage domain service."""

import uuid
from collections.abc import Sequence
from typing import Any

from domains.conversation.constants.conversation_constants import (
    ConversationChannel,
    ConversationMessageType,
    ConversationParticipantType,
)
from domains.conversation.exceptions.conversation_exceptions import (
    MessageNotEditableError,
    MessageNotFoundError,
)
from domains.conversation.models.conversation_message import ConversationMessage
from domains.conversation.repositories.message_repository import ConversationMessageRepository
from app.platform.logging import get_logger
from shared.base_service import BaseService


class MessageService(BaseService):
    def __init__(self, repository: ConversationMessageRepository) -> None:
        self._repository = repository
        self._logger = get_logger(__name__)

    async def add_message(
        self,
        conversation_id: uuid.UUID,
        sender_type: ConversationParticipantType,
        channel: ConversationChannel,
        content: str,
        *,
        message_type: ConversationMessageType = ConversationMessageType.TEXT,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationMessage:
        message = await self._repository.create(
            conversation_id=conversation_id,
            sender_type=sender_type,
            channel=channel,
            message_type=message_type,
            content=content,
            message_metadata=metadata,
        )
        self._logger.debug(
            "conversation_message_added",
            conversation_id=str(conversation_id),
            sender_type=sender_type,
            message_type=message_type,
        )
        return message

    async def list_messages(
        self,
        conversation_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[Sequence[ConversationMessage], int]:
        return await self._repository.list_by_conversation(
            conversation_id, page=page, page_size=page_size
        )

    @staticmethod
    def _assert_is_internal_note(message: ConversationMessage) -> None:
        """Only internal notes (metadata.internal=true) can be edited/deleted —
        customer-visible messages are an immutable record once sent."""
        if not (message.message_metadata or {}).get("internal"):
            raise MessageNotEditableError(context={"message_id": str(message.id)})

    async def _get_message(self, message_id: uuid.UUID) -> ConversationMessage:
        message = await self._repository.get_by_id(message_id)
        if message is None:
            raise MessageNotFoundError(context={"message_id": str(message_id)})
        return message

    async def update_message(self, message_id: uuid.UUID, content: str) -> ConversationMessage:
        message = await self._get_message(message_id)
        self._assert_is_internal_note(message)
        updated = await self._repository.update(message_id, content=content)
        self._logger.debug("conversation_message_edited", message_id=str(message_id))
        return updated

    async def delete_message(self, message_id: uuid.UUID) -> ConversationMessage:
        """Soft delete — keeps the row (audit trail: author/timestamp survive)
        but marks it deleted in the same `message_metadata` JSON field the
        internal-note flag already lives in, rather than a new column."""
        message = await self._get_message(message_id)
        self._assert_is_internal_note(message)
        new_metadata = {**(message.message_metadata or {}), "deleted": True}
        updated = await self._repository.update(message_id, message_metadata=new_metadata)
        self._logger.debug("conversation_message_deleted", message_id=str(message_id))
        return updated

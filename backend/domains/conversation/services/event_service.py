"""ConversationEvent domain service — records complaint/workflow/notification/system
events onto a conversation's audit trail."""

import uuid
from typing import Any

from domains.conversation.models.conversation_event import ConversationEvent
from domains.conversation.repositories.event_repository import ConversationEventRepository
from app.platform.logging import get_logger
from shared.base_service import BaseService


class ConversationEventService(BaseService):
    def __init__(self, repository: ConversationEventRepository) -> None:
        self._repository = repository
        self._logger = get_logger(__name__)

    async def record_event(
        self,
        conversation_id: uuid.UUID,
        event_type: str,
        source_domain: str,
        payload: dict[str, Any] | None = None,
    ) -> ConversationEvent:
        event = await self._repository.create(
            conversation_id=conversation_id,
            event_type=event_type,
            source_domain=source_domain,
            payload=payload,
        )
        self._logger.debug(
            "conversation_event_recorded",
            conversation_id=str(conversation_id),
            event_type=event_type,
            source_domain=source_domain,
        )
        return event

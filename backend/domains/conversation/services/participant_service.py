"""ConversationParticipant domain service — de-duplicated participant registration."""

import uuid
from datetime import UTC, datetime

from domains.conversation.constants.conversation_constants import ConversationParticipantType
from domains.conversation.models.conversation_participant import ConversationParticipant
from domains.conversation.repositories.participant_repository import (
    ConversationParticipantRepository,
)
from app.platform.logging import get_logger
from shared.base_service import BaseService


class ConversationParticipantService(BaseService):
    def __init__(self, repository: ConversationParticipantRepository) -> None:
        self._repository = repository
        self._logger = get_logger(__name__)

    async def ensure_participant(
        self,
        conversation_id: uuid.UUID,
        participant_type: ConversationParticipantType,
        participant_ref: str | None,
        *,
        role: str | None = None,
    ) -> ConversationParticipant:
        """Registers a participant if it isn't already on the conversation.
        Same (conversation, type, ref) is a no-op on repeat calls — this is
        what guarantees an employee assigned twice, or an AI/customer that
        speaks on every turn, only ever appears once in `/participants`."""
        existing = await self._repository.get_by_conversation_and_ref(
            conversation_id, participant_type, participant_ref
        )
        if existing is not None:
            return existing
        participant = await self._repository.create(
            conversation_id=conversation_id,
            participant_type=participant_type,
            participant_ref=participant_ref,
            role=role,
            joined_at=datetime.now(UTC),
        )
        self._logger.debug(
            "conversation_participant_registered",
            conversation_id=str(conversation_id),
            participant_type=participant_type,
            participant_ref=participant_ref,
        )
        return participant

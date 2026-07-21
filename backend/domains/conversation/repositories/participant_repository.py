"""ConversationParticipant repository."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.conversation.constants.conversation_constants import ConversationParticipantType
from domains.conversation.models.conversation_participant import ConversationParticipant
from app.platform.database.repository import BaseRepository


class ConversationParticipantRepository(BaseRepository[ConversationParticipant]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ConversationParticipant, session)

    async def create(self, **kwargs) -> ConversationParticipant:
        entity = ConversationParticipant(**kwargs)
        return await self.add(entity)

    async def get_by_conversation_and_ref(
        self,
        conversation_id: uuid.UUID,
        participant_type: ConversationParticipantType,
        participant_ref: str | None,
    ) -> ConversationParticipant | None:
        """The de-duplication lookup — same (conversation, type, ref) never
        gets a second participant row."""
        query = select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.participant_type == participant_type,
            ConversationParticipant.participant_ref == participant_ref,
        )
        result = await self._session.execute(query)
        return result.scalars().first()

    async def list_by_conversation(
        self, conversation_id: uuid.UUID
    ) -> Sequence[ConversationParticipant]:
        query = select(ConversationParticipant).where(
            ConversationParticipant.conversation_id == conversation_id
        ).order_by(ConversationParticipant.joined_at.asc())
        result = await self._session.execute(query)
        return result.scalars().all()

    async def mark_left(
        self, participant_id: uuid.UUID, left_at: datetime
    ) -> ConversationParticipant | None:
        entity = await self.get_by_id(participant_id)
        if entity is None:
            return None
        entity.left_at = left_at
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

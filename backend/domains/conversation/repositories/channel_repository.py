"""ConversationChannelLink repository — the reverse-lookup bridge to existing
Interaction rows / voice session ids / complaint ids."""

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.conversation.models.conversation_channel import ConversationChannelLink
from app.platform.database.repository import BaseRepository


class ConversationChannelRepository(BaseRepository[ConversationChannelLink]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ConversationChannelLink, session)

    async def create(self, **kwargs) -> ConversationChannelLink:
        entity = ConversationChannelLink(**kwargs)
        return await self.add(entity)

    async def get_by_external_ref(
        self, external_ref_type: str, external_ref_id: str
    ) -> ConversationChannelLink | None:
        query = select(ConversationChannelLink).where(
            ConversationChannelLink.external_ref_type == external_ref_type,
            ConversationChannelLink.external_ref_id == external_ref_id,
        )
        result = await self._session.execute(query)
        return result.scalars().first()

    async def list_by_conversation(
        self, conversation_id: uuid.UUID
    ) -> Sequence[ConversationChannelLink]:
        query = select(ConversationChannelLink).where(
            ConversationChannelLink.conversation_id == conversation_id
        )
        result = await self._session.execute(query)
        return result.scalars().all()

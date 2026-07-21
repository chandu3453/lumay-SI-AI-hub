"""ConversationMessage repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.conversation.models.conversation_message import ConversationMessage
from app.platform.database.repository import BaseRepository


class ConversationMessageRepository(BaseRepository[ConversationMessage]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ConversationMessage, session)

    async def create(self, **kwargs) -> ConversationMessage:
        entity = ConversationMessage(**kwargs)
        return await self.add(entity)

    async def update(self, message_id: uuid.UUID, **kwargs) -> ConversationMessage | None:
        entity = await self.get_by_id(message_id)
        if entity is None:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(entity, key, value)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def list_by_conversation(
        self,
        conversation_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[Sequence[ConversationMessage], int]:
        query = select(ConversationMessage).where(
            ConversationMessage.conversation_id == conversation_id
        )
        count_query = select(func.count(ConversationMessage.id)).where(
            ConversationMessage.conversation_id == conversation_id
        )

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        # Chronological order — unlike Interaction lists, a conversation transcript
        # reads oldest-first.
        query = query.order_by(ConversationMessage.created_at.asc()).offset(offset).limit(page_size)

        result = await self._session.execute(query)
        items = result.scalars().all()

        return items, total

    # ── Sprint 29 — Reporting aggregates ──────────────────────────────────

    async def list_for_conversations(
        self, conversation_ids: Sequence[uuid.UUID]
    ) -> Sequence[ConversationMessage]:
        """Bulk fetch (one query, not N+1) backing Average Response Time —
        the caller pairs consecutive customer->reply messages per
        conversation in Python, which stays portable across the Postgres
        (prod) / SQLite (test) dialects this codebase runs against."""
        if not conversation_ids:
            return []
        query = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id.in_(conversation_ids))
            .order_by(ConversationMessage.conversation_id, ConversationMessage.created_at.asc())
        )
        result = await self._session.execute(query)
        return result.scalars().all()

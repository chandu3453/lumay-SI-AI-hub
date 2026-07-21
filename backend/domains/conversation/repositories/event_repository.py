"""ConversationEvent repository."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.conversation.models.conversation import Conversation
from domains.conversation.models.conversation_event import ConversationEvent
from app.platform.database.repository import BaseRepository


class ConversationEventRepository(BaseRepository[ConversationEvent]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ConversationEvent, session)

    async def create(self, **kwargs) -> ConversationEvent:
        entity = ConversationEvent(**kwargs)
        return await self.add(entity)

    async def list_by_conversation(
        self,
        conversation_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[Sequence[ConversationEvent], int]:
        query = select(ConversationEvent).where(
            ConversationEvent.conversation_id == conversation_id
        )
        count_query = select(func.count(ConversationEvent.id)).where(
            ConversationEvent.conversation_id == conversation_id
        )

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        query = query.order_by(ConversationEvent.created_at.asc()).offset(offset).limit(page_size)

        result = await self._session.execute(query)
        items = result.scalars().all()

        return items, total

    # ── Sprint 29 — Reporting aggregates ──────────────────────────────────

    async def list_by_customer(
        self,
        customer_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[Sequence[ConversationEvent], int]:
        """Customer-level activity timeline — same merge `GET /conversations/
        {id}/timeline` already does per-conversation, joined out across every
        conversation the customer has ever had."""
        base = select(ConversationEvent).join(
            Conversation, ConversationEvent.conversation_id == Conversation.id
        ).where(Conversation.customer_id == customer_id)
        count_query = select(func.count(ConversationEvent.id)).select_from(
            ConversationEvent.__table__.join(
                Conversation.__table__, ConversationEvent.conversation_id == Conversation.id
            )
        ).where(Conversation.customer_id == customer_id)

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        query = base.order_by(ConversationEvent.created_at.asc()).offset(offset).limit(page_size)

        result = await self._session.execute(query)
        items = result.scalars().all()

        return items, total

    async def list_by_event_type(
        self,
        event_type: str,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> Sequence[ConversationEvent]:
        """Full rows (not just counts) — needed when the caller must inspect
        `payload` (e.g. `ai_handed_over`'s `direction`, `conversation_transferred`'s
        `new_owner`), which varies by JSON dialect to query directly so it's
        filtered in Python instead."""
        query = select(ConversationEvent).where(ConversationEvent.event_type == event_type)
        if date_from is not None:
            query = query.where(ConversationEvent.created_at >= date_from)
        if date_to is not None:
            query = query.where(ConversationEvent.created_at <= date_to)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def count_by_event_types(
        self,
        event_types: Sequence[str],
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> dict[str, int]:
        query = select(ConversationEvent.event_type, func.count(ConversationEvent.id)).where(
            ConversationEvent.event_type.in_(event_types)
        )
        if date_from is not None:
            query = query.where(ConversationEvent.created_at >= date_from)
        if date_to is not None:
            query = query.where(ConversationEvent.created_at <= date_to)
        query = query.group_by(ConversationEvent.event_type)
        result = await self._session.execute(query)
        counts = {event_type: count for event_type, count in result.all()}
        return {et: counts.get(et, 0) for et in event_types}

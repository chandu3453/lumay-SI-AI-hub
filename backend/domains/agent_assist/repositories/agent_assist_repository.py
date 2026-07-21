"""AgentAssistInsight repository."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.agent_assist.models.agent_assist_insight import AgentAssistInsight
from domains.conversation.models.conversation import Conversation
from app.platform.database.repository import BaseRepository


class AgentAssistRepository(BaseRepository[AgentAssistInsight]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AgentAssistInsight, session)

    async def create(self, **kwargs) -> AgentAssistInsight:
        entity = AgentAssistInsight(**kwargs)
        return await self.add(entity)

    async def get_latest(self, conversation_id: uuid.UUID) -> AgentAssistInsight | None:
        query = (
            select(AgentAssistInsight)
            .where(AgentAssistInsight.conversation_id == conversation_id)
            .order_by(desc(AgentAssistInsight.created_at))
            .limit(1)
        )
        result = await self._session.execute(query)
        return result.scalars().first()

    async def list_history(
        self, conversation_id: uuid.UUID, *, limit: int = 20
    ) -> Sequence[AgentAssistInsight]:
        query = (
            select(AgentAssistInsight)
            .where(AgentAssistInsight.conversation_id == conversation_id)
            .order_by(desc(AgentAssistInsight.created_at))
            .limit(limit)
        )
        result = await self._session.execute(query)
        # Oldest-first — a trend line/history list reads chronologically.
        return list(reversed(result.scalars().all()))

    # ── Sprint 29 — Reporting aggregates ──────────────────────────────────

    async def latest_for_customer(self, customer_id: uuid.UUID) -> AgentAssistInsight | None:
        query = (
            select(AgentAssistInsight)
            .join(Conversation, AgentAssistInsight.conversation_id == Conversation.id)
            .where(Conversation.customer_id == customer_id)
            .order_by(desc(AgentAssistInsight.created_at))
            .limit(1)
        )
        result = await self._session.execute(query)
        return result.scalars().first()

    async def latest_per_conversation(
        self, *, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> list[AgentAssistInsight]:
        """Every conversation's most recent insight within the window —
        backs both sentiment and intent distribution (the caller tallies
        whichever field it needs) so "latest per conversation" is reduced
        exactly once, not duplicated per metric."""
        query = select(AgentAssistInsight)
        if date_from is not None:
            query = query.where(AgentAssistInsight.created_at >= date_from)
        if date_to is not None:
            query = query.where(AgentAssistInsight.created_at <= date_to)
        result = await self._session.execute(query)
        rows = result.scalars().all()

        latest_by_conversation: dict[uuid.UUID, AgentAssistInsight] = {}
        for row in rows:
            existing = latest_by_conversation.get(row.conversation_id)
            if existing is None or row.created_at > existing.created_at:
                latest_by_conversation[row.conversation_id] = row
        return list(latest_by_conversation.values())

    async def count_by_employee(
        self, *, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> dict[uuid.UUID, int]:
        """Regeneration counts grouped by the conversation's assigned
        employee — backs "AI Assistance Usage" in Employee Analytics."""
        query = (
            select(Conversation.assigned_employee_id, func.count(AgentAssistInsight.id))
            .join(Conversation, AgentAssistInsight.conversation_id == Conversation.id)
            .where(Conversation.assigned_employee_id.is_not(None))
        )
        if date_from is not None:
            query = query.where(AgentAssistInsight.created_at >= date_from)
        if date_to is not None:
            query = query.where(AgentAssistInsight.created_at <= date_to)
        query = query.group_by(Conversation.assigned_employee_id)
        result = await self._session.execute(query)
        return dict(result.all())

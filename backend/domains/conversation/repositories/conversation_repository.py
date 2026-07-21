"""Conversation repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.conversation.constants.conversation_constants import (
    ConversationChannel,
    ConversationPriority,
    ConversationStatus,
    TERMINAL_CONVERSATION_STATUSES,
)
from domains.conversation.models.conversation import Conversation
from domains.conversation.models.conversation_message import ConversationMessage
from app.platform.database.repository import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Conversation, session)

    async def create(self, **kwargs) -> Conversation:
        entity = Conversation(**kwargs)
        return await self.add(entity)

    async def update(self, conversation_id: uuid.UUID, **kwargs) -> Conversation | None:
        entity = await self.get_by_id(conversation_id)
        if entity is None:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(entity, key, value)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def get_active_by_customer(
        self,
        customer_id: uuid.UUID,
        since: datetime,
    ) -> Conversation | None:
        """The ConversationFactory merge-rule query: most recently updated,
        non-terminal conversation for this customer, touched within `since`."""
        query = (
            select(Conversation)
            .where(Conversation.customer_id == customer_id)
            .where(Conversation.current_status.not_in(TERMINAL_CONVERSATION_STATUSES))
            .where(Conversation.updated_at >= since)
            .order_by(Conversation.updated_at.desc())
            .limit(1)
        )
        result = await self._session.execute(query)
        return result.scalars().first()

    async def touch(self, conversation_id: uuid.UUID) -> None:
        """Bumps `updated_at` as a "last activity" marker. A plain child-table
        insert (a message, an event) never touches the parent `conversations`
        row on its own — `onupdate=func.now()` only fires when the row itself
        is written. Explicitly assigning `updated_at` marks it dirty so the
        flush actually emits the UPDATE."""
        entity = await self.get_by_id(conversation_id)
        if entity is None:
            return
        entity.updated_at = datetime.now(UTC)
        await self._session.flush()

    async def clear_assigned_employee(self, conversation_id: uuid.UUID) -> Conversation | None:
        """The generic `update()` skips `None` values by design (so a partial
        update never accidentally nulls an unrelated field) — that means it
        can't be used to actually clear `assigned_employee_id` on release.
        This is the one explicit-null path."""
        entity = await self.get_by_id(conversation_id)
        if entity is None:
            return None
        entity.assigned_employee_id = None
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def get_by_complaint_id(self, complaint_id: uuid.UUID) -> Conversation | None:
        query = select(Conversation).where(Conversation.complaint_id == complaint_id)
        result = await self._session.execute(query)
        return result.scalars().first()

    async def list(
        self,
        *,
        customer_id: uuid.UUID | None = None,
        status: ConversationStatus | None = None,
        channel: ConversationChannel | None = None,
        assigned_employee_id: uuid.UUID | None = None,
        complaint_id: uuid.UUID | None = None,
        priority: ConversationPriority | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[Conversation], int]:
        query = select(Conversation)
        count_query = select(func.count(Conversation.id))

        def _apply(clause):
            nonlocal query, count_query
            query = query.where(clause)
            count_query = count_query.where(clause)

        if customer_id is not None:
            _apply(Conversation.customer_id == customer_id)
        if status is not None:
            _apply(Conversation.current_status == status)
        if channel is not None:
            _apply(Conversation.current_channel == channel)
        if assigned_employee_id is not None:
            _apply(Conversation.assigned_employee_id == assigned_employee_id)
        if complaint_id is not None:
            _apply(Conversation.complaint_id == complaint_id)
        if priority is not None:
            _apply(Conversation.priority == priority)
        if date_from is not None:
            _apply(Conversation.updated_at >= date_from)
        if date_to is not None:
            _apply(Conversation.updated_at <= date_to)
        if search:
            _apply(self._search_clause(search))

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        query = query.order_by(Conversation.updated_at.desc()).offset(offset).limit(page_size)

        result = await self._session.execute(query)
        items = result.scalars().all()

        return items, total

    async def get_last_message_preview_map(
        self, conversation_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, str]:
        """Batched (not per-card N+1) latest-message lookup, backing the queue
        card's "Last Message Preview" field."""
        if not conversation_ids:
            return {}
        query = (
            select(ConversationMessage.conversation_id, ConversationMessage.content)
            .where(ConversationMessage.conversation_id.in_(conversation_ids))
            .order_by(ConversationMessage.conversation_id, ConversationMessage.created_at.desc())
        )
        result = await self._session.execute(query)
        preview_map: dict[uuid.UUID, str] = {}
        for conversation_id, content in result.all():
            preview_map.setdefault(conversation_id, content)
        return preview_map

    async def get_customer_name_map(self, customer_ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, str]:
        """Batched lookup backing the queue card's "Customer Name" field —
        `ConversationSummary` only carries `customer_id`."""
        if not customer_ids:
            return {}
        from domains.customer.models.customer import Customer

        query = select(Customer.id, Customer.full_name).where(Customer.id.in_(customer_ids))
        result = await self._session.execute(query)
        return dict(result.all())

    # ── Sprint 29 — Reporting aggregates ──────────────────────────────────
    # All filtered on `created_at` (when the conversation started), not
    # `updated_at` (last activity, used by `list()`'s date filter for a
    # different purpose — queue freshness) — the standard "activity in this
    # period" window for analytics. Resolution-time averaging is done in
    # Python over the fetched rows rather than SQL date-diff functions, to
    # stay portable across the Postgres (prod) and SQLite (test) dialects
    # this codebase runs against.

    def _apply_reporting_filters(
        self,
        query,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        channel: ConversationChannel | None = None,
        assigned_employee_id: uuid.UUID | None = None,
        priority: ConversationPriority | None = None,
    ):
        if date_from is not None:
            query = query.where(Conversation.created_at >= date_from)
        if date_to is not None:
            query = query.where(Conversation.created_at <= date_to)
        if channel is not None:
            query = query.where(Conversation.current_channel == channel)
        if assigned_employee_id is not None:
            query = query.where(Conversation.assigned_employee_id == assigned_employee_id)
        if priority is not None:
            query = query.where(Conversation.priority == priority)
        return query

    async def count_by_status(self, **filters) -> dict[str, int]:
        query = self._apply_reporting_filters(
            select(Conversation.current_status, func.count(Conversation.id)), **filters
        ).group_by(Conversation.current_status)
        result = await self._session.execute(query)
        return {str(status): count for status, count in result.all()}

    async def count_by_channel(self, **filters) -> dict[str, int]:
        query = self._apply_reporting_filters(
            select(Conversation.current_channel, func.count(Conversation.id)), **filters
        ).group_by(Conversation.current_channel)
        result = await self._session.execute(query)
        return {str(channel): count for channel, count in result.all()}

    async def count_ai_vs_human(self, **filters) -> dict[str, int]:
        ai_query = self._apply_reporting_filters(
            select(func.count(Conversation.id)).where(Conversation.ai_handling.is_(True)), **filters
        )
        human_query = self._apply_reporting_filters(
            select(func.count(Conversation.id)).where(Conversation.human_handling.is_(True)), **filters
        )
        ai_count = (await self._session.execute(ai_query)).scalar_one()
        human_count = (await self._session.execute(human_query)).scalar_one()
        return {"ai_handled": ai_count, "human_handled": human_count}

    async def avg_resolution_seconds(self, **filters) -> float | None:
        query = self._apply_reporting_filters(
            select(Conversation.created_at, Conversation.updated_at).where(
                Conversation.current_status.in_(TERMINAL_CONVERSATION_STATUSES)
            ),
            **filters,
        )
        result = await self._session.execute(query)
        rows = result.all()
        if not rows:
            return None
        durations = [(updated - created).total_seconds() for created, updated in rows]
        return sum(durations) / len(durations)

    async def avg_duration_seconds(self, **filters) -> float | None:
        """All conversations regardless of terminal status — "average
        conversation duration" (created_at -> last activity), distinct from
        resolution time (terminal conversations only)."""
        query = self._apply_reporting_filters(
            select(Conversation.created_at, Conversation.updated_at), **filters
        )
        result = await self._session.execute(query)
        rows = result.all()
        if not rows:
            return None
        durations = [(updated - created).total_seconds() for created, updated in rows]
        return sum(durations) / len(durations)

    async def list_by_customer(self, customer_id: uuid.UUID) -> Sequence[Conversation]:
        query = (
            select(Conversation)
            .where(Conversation.customer_id == customer_id)
            .order_by(Conversation.updated_at.desc())
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    async def list_ids(self, *, limit: int = 200, **filters) -> Sequence[uuid.UUID]:
        """Most-recent-first conversation ids matching the reporting filters
        — backs Average Response Time's bounded message scan."""
        query = self._apply_reporting_filters(select(Conversation.id), **filters)
        query = query.order_by(Conversation.created_at.desc()).limit(limit)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def list_for_trends(self, *, limit: int = 5000, **filters) -> Sequence[Conversation]:
        """Full rows within the reporting window, for time-bucketing trend
        charts (created_at/status/ai_handling/human_handling)."""
        query = self._apply_reporting_filters(select(Conversation), **filters)
        query = query.order_by(Conversation.created_at.desc()).limit(limit)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def list_assigned(self, **filters) -> Sequence[Conversation]:
        """Every conversation with a non-null `assigned_employee_id` within
        the reporting window — backs Employee Analytics' per-employee groups."""
        query = self._apply_reporting_filters(select(Conversation), **filters).where(
            Conversation.assigned_employee_id.is_not(None)
        )
        result = await self._session.execute(query)
        return result.scalars().all()

    @staticmethod
    def _search_clause(search: str):
        """Backs the `search` filter — covers the 4 spec'd text-search targets
        (customer name, conversation id, complaint id/policy number, message
        text) via OR'd subqueries, so filtering stays server-side instead of
        requiring the frontend to page through everything and filter client-side.
        The only place this repository reads across domains (Customer,
        Complaint, ConversationMessage) — read-only, mirrors how
        `conversation_engine.py` already reads across domains for orchestration.
        """
        from sqlalchemy import String, cast

        from domains.complaint.models.complaint import Complaint
        from domains.customer.models.customer import Customer

        like = f"%{search}%"
        conditions = [cast(Conversation.id, String).ilike(like)]

        try:
            search_uuid = uuid.UUID(search)
        except ValueError:
            search_uuid = None
        if search_uuid is not None:
            conditions.append(Conversation.complaint_id == search_uuid)

        conditions.append(
            Conversation.customer_id.in_(
                select(Customer.id).where(Customer.full_name.ilike(like))
            )
        )
        conditions.append(
            Conversation.complaint_id.in_(
                select(Complaint.id).where(
                    or_(
                        Complaint.policy_number.ilike(like),
                        Complaint.complaint_number.ilike(like),
                    )
                )
            )
        )
        conditions.append(
            Conversation.id.in_(
                select(ConversationMessage.conversation_id).where(
                    ConversationMessage.content.ilike(like)
                )
            )
        )
        return or_(*conditions)

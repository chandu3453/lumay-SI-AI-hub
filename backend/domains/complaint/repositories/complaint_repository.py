"""Complaint Repository — Phase 2 with full filter support.

Phase 2 additions:
- list(): Extended with theme, sla_risk, is_repeat, detected_language,
          escalation_risk_min, product, channel, regulatory_flag filters
- list_by_customer_since(): FR-008 repeat complaint detection query
- get_by_complaint_number(): Lookup by human-readable number
"""

import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.database.repository import BaseRepository
from domains.complaint.constants.complaint_constants import (
    ComplaintCategory,
    ComplaintPriority,
    ComplaintSeverity,
    ComplaintStatus,
)
from domains.complaint.models.complaint import Complaint


class ComplaintRepository(BaseRepository[Complaint]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Complaint, session)

    async def create(self, **kwargs) -> Complaint:
        entity = Complaint(**kwargs)
        return await self.add(entity)

    async def update(
        self, complaint_id: uuid.UUID, **kwargs
    ) -> Complaint | None:
        entity = await self.get_by_id(complaint_id)
        if entity is None:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(entity, key, value)
        await self._session.flush()
        result = await self._session.execute(
            select(Complaint).where(Complaint.id == complaint_id)
        )
        return result.unique().scalar_one()

    async def list(
        self,
        *,
        customer_id: uuid.UUID | None = None,
        status: ComplaintStatus | None = None,
        category: ComplaintCategory | None = None,
        priority: ComplaintPriority | None = None,
        severity: ComplaintSeverity | None = None,
        # Phase 2 filters (FR-004, FR-007, FR-008, FR-019)
        theme: str | None = None,
        sla_risk: str | None = None,
        is_repeat: bool | None = None,
        detected_language: str | None = None,
        escalation_risk_min: int | None = None,
        product: str | None = None,
        channel: str | None = None,
        regulatory_flag: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[Complaint], int]:
        query = select(Complaint)
        count_query = select(func.count(Complaint.id))

        # Core filters
        if customer_id is not None:
            query = query.where(Complaint.customer_id == customer_id)
            count_query = count_query.where(Complaint.customer_id == customer_id)
        if status is not None:
            query = query.where(Complaint.status == status)
            count_query = count_query.where(Complaint.status == status)
        if category is not None:
            query = query.where(Complaint.category == category)
            count_query = count_query.where(Complaint.category == category)
        if priority is not None:
            query = query.where(Complaint.priority == priority)
            count_query = count_query.where(Complaint.priority == priority)
        if severity is not None:
            query = query.where(Complaint.severity == severity)
            count_query = count_query.where(Complaint.severity == severity)

        # Phase 2 filters
        if theme is not None:
            query = query.where(Complaint.theme == theme)
            count_query = count_query.where(Complaint.theme == theme)
        if sla_risk is not None:
            query = query.where(Complaint.sla_risk == sla_risk)
            count_query = count_query.where(Complaint.sla_risk == sla_risk)
        if is_repeat is not None:
            query = query.where(Complaint.is_repeat == is_repeat)
            count_query = count_query.where(Complaint.is_repeat == is_repeat)
        if detected_language is not None:
            query = query.where(Complaint.detected_language == detected_language)
            count_query = count_query.where(Complaint.detected_language == detected_language)
        if escalation_risk_min is not None:
            query = query.where(Complaint.escalation_risk_score >= escalation_risk_min)
            count_query = count_query.where(Complaint.escalation_risk_score >= escalation_risk_min)
        if product is not None:
            query = query.where(Complaint.product == product)
            count_query = count_query.where(Complaint.product == product)
        if channel is not None:
            query = query.where(Complaint.channel == channel)
            count_query = count_query.where(Complaint.channel == channel)
        if regulatory_flag is not None:
            query = query.where(Complaint.regulatory_flag == regulatory_flag)
            count_query = count_query.where(Complaint.regulatory_flag == regulatory_flag)

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        query = query.order_by(Complaint.created_at.desc())
        query = query.offset(offset).limit(page_size)

        result = await self._session.execute(query)
        items = result.scalars().all()

        return items, total

    async def list_by_customer_since(
        self,
        customer_id: uuid.UUID,
        since: datetime,
        exclude_id: uuid.UUID | None = None,
    ) -> Sequence[Complaint]:
        """FR-008 — List complaints from a customer since a given datetime.

        Used by RepeatComplaintService to detect repeat complaints within
        configurable time windows (30, 60, 90 days per BR-002).
        """
        query = (
            select(Complaint)
            .where(Complaint.customer_id == customer_id)
            .where(Complaint.created_at >= since)
        )
        if exclude_id is not None:
            query = query.where(Complaint.id != exclude_id)

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_by_customer_id(
        self, customer_id: uuid.UUID
    ) -> Sequence[Complaint]:
        result = await self._session.execute(
            select(Complaint).where(Complaint.customer_id == customer_id)
            .order_by(Complaint.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_complaint_number(
        self, complaint_number: str
    ) -> Complaint | None:
        """Lookup complaint by human-readable complaint number."""
        result = await self._session.execute(
            select(Complaint).where(Complaint.complaint_number == complaint_number)
        )
        return result.unique().scalar_one_or_none()

    async def get_by_interaction_id(
        self, interaction_id: uuid.UUID
    ) -> Sequence[Complaint]:
        result = await self._session.execute(
            select(Complaint).where(
                Complaint.interaction_id == interaction_id
            )
        )
        return result.scalars().all()

    async def get_related_complaints(
        self,
        customer_id: uuid.UUID,
        theme: str | None = None,
        exclude_id: uuid.UUID | None = None,
        limit: int = 10,
    ) -> Sequence[Complaint]:
        """FR-008 — Get related/repeat complaints for a customer, optionally filtered by theme."""
        query = select(Complaint).where(Complaint.customer_id == customer_id)
        if theme is not None:
            query = query.where(Complaint.theme == theme)
        if exclude_id is not None:
            query = query.where(Complaint.id != exclude_id)
        query = query.order_by(Complaint.created_at.desc()).limit(limit)
        result = await self._session.execute(query)
        return result.scalars().all()

    # ── Sprint 29 — Reporting aggregates ──────────────────────────────────

    def _apply_reporting_filters(
        self,
        query,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        category: ComplaintCategory | None = None,
        priority: ComplaintPriority | None = None,
    ):
        if date_from is not None:
            query = query.where(Complaint.created_at >= date_from)
        if date_to is not None:
            query = query.where(Complaint.created_at <= date_to)
        if category is not None:
            query = query.where(Complaint.category == category)
        if priority is not None:
            query = query.where(Complaint.priority == priority)
        return query

    async def list_created_dates(
        self, *, date_from: datetime | None = None, date_to: datetime | None = None
    ) -> Sequence[datetime]:
        """Just the timestamps — backs the Complaint Trend chart's
        time-bucketing without pulling full rows."""
        query = self._apply_reporting_filters(
            select(Complaint.created_at), date_from=date_from, date_to=date_to
        )
        result = await self._session.execute(query)
        return [row[0] for row in result.all()]

    async def count_by_status(self, **filters) -> dict[str, int]:
        query = self._apply_reporting_filters(
            select(Complaint.status, func.count(Complaint.id)), **filters
        ).group_by(Complaint.status)
        result = await self._session.execute(query)
        return {str(status): count for status, count in result.all()}

    async def count_by_category(self, **filters) -> dict[str, int]:
        query = self._apply_reporting_filters(
            select(Complaint.category, func.count(Complaint.id)), **filters
        ).group_by(Complaint.category)
        result = await self._session.execute(query)
        return {str(category): count for category, count in result.all()}

    async def count_by_severity(self, **filters) -> dict[str, int]:
        query = self._apply_reporting_filters(
            select(Complaint.severity, func.count(Complaint.id)), **filters
        ).group_by(Complaint.severity)
        result = await self._session.execute(query)
        return {str(severity): count for severity, count in result.all()}

    async def avg_resolution_seconds(self, **filters) -> float | None:
        query = self._apply_reporting_filters(
            select(Complaint.created_at, Complaint.updated_at).where(
                Complaint.status.in_(
                    [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED, ComplaintStatus.ARCHIVED]
                )
            ),
            **filters,
        )
        result = await self._session.execute(query)
        rows = result.all()
        if not rows:
            return None
        durations = [(updated - created).total_seconds() for created, updated in rows]
        return sum(durations) / len(durations)

    async def count_open_by_customer(self, customer_id: uuid.UUID) -> int:
        query = select(func.count(Complaint.id)).where(
            Complaint.customer_id == customer_id,
            Complaint.status.not_in(
                [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED, ComplaintStatus.ARCHIVED]
            ),
        )
        result = await self._session.execute(query)
        return result.scalar_one()

    async def count_high_priority_open(self) -> int:
        """Supervisor Dashboard's "High Priority Complaints" — open complaints
        at high/critical priority, right now, no date filter."""
        query = select(func.count(Complaint.id)).where(
            Complaint.priority.in_([ComplaintPriority.HIGH, ComplaintPriority.CRITICAL]),
            Complaint.status.not_in(
                [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED, ComplaintStatus.ARCHIVED]
            ),
        )
        result = await self._session.execute(query)
        return result.scalar_one()

"""Workflow Repository — Workflow domain."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.workflow.constants.workflow_constants import (
    EscalationLevel,
    SLAStatus,
    WorkflowStage,
    WorkflowStatus,
)
from domains.workflow.models.workflow import Workflow
from app.platform.database.repository import BaseRepository


class WorkflowRepository(BaseRepository[Workflow]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Workflow, session)

    async def create(self, **kwargs) -> Workflow:
        entity = Workflow(**kwargs)
        return await self.add(entity)

    async def update(
        self, workflow_id: uuid.UUID, **kwargs
    ) -> Workflow | None:
        entity = await self.get_by_id(workflow_id)
        if entity is None:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(entity, key, value)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def list(
        self,
        *,
        workflow_status: WorkflowStatus | None = None,
        workflow_stage: WorkflowStage | None = None,
        assigned_team: str | None = None,
        sla_status: SLAStatus | None = None,
        escalation_level: EscalationLevel | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[Workflow], int]:
        query = select(Workflow)
        count_query = select(func.count(Workflow.id))

        if workflow_status is not None:
            query = query.where(Workflow.workflow_status == workflow_status)
            count_query = count_query.where(Workflow.workflow_status == workflow_status)
        if workflow_stage is not None:
            query = query.where(Workflow.workflow_stage == workflow_stage)
            count_query = count_query.where(Workflow.workflow_stage == workflow_stage)
        if assigned_team is not None:
            query = query.where(Workflow.assigned_team == assigned_team)
            count_query = count_query.where(Workflow.assigned_team == assigned_team)
        if sla_status is not None:
            query = query.where(Workflow.sla_status == sla_status)
            count_query = count_query.where(Workflow.sla_status == sla_status)
        if escalation_level is not None:
            query = query.where(Workflow.escalation_level == escalation_level)
            count_query = count_query.where(Workflow.escalation_level == escalation_level)

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        query = query.order_by(Workflow.created_at.desc())
        query = query.offset(offset).limit(page_size)

        result = await self._session.execute(query)
        items = result.scalars().all()

        return items, total

    async def delete(self, workflow_id: uuid.UUID) -> bool:
        entity = await self.get_by_id(workflow_id)
        if entity is None:
            return False
        await self._session.delete(entity)
        await self._session.flush()
        return True

    async def get_by_complaint_id(
        self, complaint_id: uuid.UUID
    ) -> Sequence[Workflow]:
        result = await self._session.execute(
            select(Workflow).where(Workflow.complaint_id == complaint_id)
        )
        return result.scalars().all()

    async def get_active_by_complaint_id(
        self, complaint_id: uuid.UUID
    ) -> Workflow | None:
        result = await self._session.execute(
            select(Workflow).where(
                Workflow.complaint_id == complaint_id,
                Workflow.workflow_status.in_([
                    WorkflowStatus.PENDING,
                    WorkflowStatus.ACTIVE,
                    WorkflowStatus.SUSPENDED,
                ]),
            )
        )
        return result.scalar_one_or_none()

    # ── Sprint 29 — Reporting aggregates ──────────────────────────────────

    async def count_by_status(self) -> dict[str, int]:
        query = select(Workflow.workflow_status, func.count(Workflow.id)).group_by(
            Workflow.workflow_status
        )
        result = await self._session.execute(query)
        return {str(status): count for status, count in result.all()}
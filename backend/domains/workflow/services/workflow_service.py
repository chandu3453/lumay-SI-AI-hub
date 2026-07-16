"""Workflow domain service - business orchestration layer."""

import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from app.platform.logging import get_logger
from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.workflow.constants.workflow_constants import (
    ApprovalStatus,
    EscalationLevel,
    SLAStatus,
    WorkflowStage,
    WorkflowStatus,
)
from domains.workflow.events.workflow_events import (
    WorkflowApproved,
    WorkflowArchived,
    WorkflowAssigned,
    WorkflowCompleted,
    WorkflowEscalated,
    WorkflowRejected,
    WorkflowStarted,
)
from shared.base_event import DomainEvent
from domains.workflow.exceptions.workflow_exceptions import (
    WorkflowNotFoundError,
    WorkflowValidationError,
)
from domains.workflow.models.workflow import Workflow
from domains.workflow.repositories.workflow_repository import WorkflowRepository
from domains.workflow.schemas.workflow_schemas import WorkflowCreate, WorkflowUpdate
from shared.base_service import BaseService

_STAGE_TRANSITIONS: dict[WorkflowStage, set[WorkflowStage]] = {
    WorkflowStage.INITIATED: {WorkflowStage.QUEUED, WorkflowStage.ASSIGNED},
    WorkflowStage.QUEUED: {WorkflowStage.ASSIGNED},
    WorkflowStage.ASSIGNED: {WorkflowStage.IN_PROGRESS},
    WorkflowStage.IN_PROGRESS: {WorkflowStage.REVIEW},
    WorkflowStage.REVIEW: {WorkflowStage.APPROVAL},
    WorkflowStage.APPROVAL: {WorkflowStage.RESOLUTION, WorkflowStage.COMPLETED, WorkflowStage.REVIEW},
    WorkflowStage.RESOLUTION: {WorkflowStage.COMPLETED},
    WorkflowStage.COMPLETED: set(),
}

_TERMINAL_STAGES = {WorkflowStage.COMPLETED}

_APPROVAL_TRANSITIONS: dict[ApprovalStatus, set[ApprovalStatus]] = {
    ApprovalStatus.NOT_REQUIRED: {ApprovalStatus.PENDING},
    ApprovalStatus.PENDING: {ApprovalStatus.APPROVED, ApprovalStatus.REJECTED},
    ApprovalStatus.APPROVED: set(),
    ApprovalStatus.REJECTED: set(),
}

_TERMINAL_APPROVALS = {ApprovalStatus.APPROVED, ApprovalStatus.REJECTED}

_IMMUTABLE_STATUSES = {WorkflowStatus.COMPLETED, WorkflowStatus.ARCHIVED, WorkflowStatus.CANCELLED}


class WorkflowService(BaseService):
    def __init__(
        self,
        repository: WorkflowRepository,
        complaint_repository: ComplaintRepository,
    ) -> None:
        self._repository = repository
        self._complaint_repository = complaint_repository
        self._logger = get_logger(__name__)

    async def create_workflow(
        self, data: WorkflowCreate
    ) -> tuple[Workflow, list[DomainEvent]]:
        self._logger.info("workflow_create_requested", complaint_id=str(data.complaint_id))

        complaint = await self._complaint_repository.get_by_id(data.complaint_id)
        if complaint is None:
            raise WorkflowValidationError(
                message="Referenced complaint not found.",
                context={"complaint_id": str(data.complaint_id)},
            )

        existing = await self._repository.get_active_by_complaint_id(data.complaint_id)
        if existing is not None:
            raise WorkflowValidationError(
                message="An active workflow already exists for this complaint.",
                context={"complaint_id": str(data.complaint_id), "existing_workflow_id": str(existing.id)},
            )

        now = datetime.now(timezone.utc)
        if data.due_at is not None and data.due_at < now:
            raise WorkflowValidationError(
                message="Due date cannot be earlier than the current time.",
                context={"due_at": data.due_at.isoformat()},
            )

        workflow = await self._repository.create(
            complaint_id=data.complaint_id,
            current_queue=data.current_queue,
            assigned_team=data.assigned_team,
            assigned_agent_id=data.assigned_agent_id,
            priority=data.priority,
            due_at=data.due_at,
            workflow_status=WorkflowStatus.ACTIVE,
            workflow_stage=WorkflowStage.INITIATED,
            sla_status=SLAStatus.WITHIN_SLA,
            escalation_level=EscalationLevel.LEVEL_0,
            approval_status=ApprovalStatus.NOT_REQUIRED,
            started_at=now,
        )
        events: list[DomainEvent] = [
            WorkflowStarted(workflow_id=workflow.id, complaint_id=workflow.complaint_id)
        ]
        self._logger.info(
            "workflow_created",
            workflow_id=str(workflow.id),
            complaint_id=str(workflow.complaint_id),
        )
        return workflow, events

    async def get_workflow(self, workflow_id: uuid.UUID) -> Workflow:
        workflow = await self._repository.get_by_id(workflow_id)
        if workflow is None:
            raise WorkflowNotFoundError(context={"workflow_id": str(workflow_id)})
        return workflow

    async def list_workflows(
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
        self._logger.debug(
            "workflow_list_requested",
            status=workflow_status,
            stage=workflow_stage,
            page=page,
        )
        return await self._repository.list(
            workflow_status=workflow_status,
            workflow_stage=workflow_stage,
            assigned_team=assigned_team,
            sla_status=sla_status,
            escalation_level=escalation_level,
            page=page,
            page_size=page_size,
        )

    async def update_workflow(
        self, workflow_id: uuid.UUID, data: WorkflowUpdate
    ) -> tuple[Workflow, list[DomainEvent]]:
        workflow = await self.get_workflow(workflow_id)
        self._assert_mutable(workflow)

        new_stage = data.workflow_stage
        if new_stage is not None and new_stage != workflow.workflow_stage:
            self._validate_stage_transition(workflow.workflow_stage, new_stage)

        if data.due_at is not None and data.escalation_level is None:
            started = workflow.started_at or datetime.now(timezone.utc)
            if data.due_at < started:
                raise WorkflowValidationError(
                    message="Due date cannot be earlier than start date.",
                    context={"due_at": data.due_at.isoformat(), "started_at": started.isoformat()},
                )

        updated = await self._repository.update(
            workflow_id, **data.model_dump(exclude_none=True)
        )
        self._logger.info("workflow_updated", workflow_id=str(workflow_id))
        return updated, []

    async def assign_workflow(
        self,
        workflow_id: uuid.UUID,
        agent_id: uuid.UUID,
        team: str | None = None,
        queue: str | None = None,
    ) -> tuple[Workflow, list[DomainEvent]]:
        workflow = await self.get_workflow(workflow_id)
        self._assert_mutable(workflow)

        kwargs: dict = {"assigned_agent_id": agent_id}
        if team is not None:
            kwargs["assigned_team"] = team
        if queue is not None:
            kwargs["current_queue"] = queue

        if workflow.workflow_stage in {WorkflowStage.INITIATED, WorkflowStage.QUEUED}:
            kwargs["workflow_stage"] = WorkflowStage.ASSIGNED

        updated = await self._repository.update(workflow_id, **kwargs)
        events: list[DomainEvent] = [
            WorkflowAssigned(
                workflow_id=workflow.id,
                assigned_agent_id=agent_id,
                assigned_team=team or "",
                queue=queue or "",
            )
        ]
        self._logger.info(
            "workflow_assigned",
            workflow_id=str(workflow_id),
            agent_id=str(agent_id),
        )
        return updated, events

    async def transfer_workflow(
        self,
        workflow_id: uuid.UUID,
        agent_id: uuid.UUID,
        team: str | None = None,
        queue: str | None = None,
    ) -> tuple[Workflow, list[DomainEvent]]:
        workflow = await self.get_workflow(workflow_id)
        self._assert_mutable(workflow)

        if workflow.assigned_agent_id is None:
            raise WorkflowValidationError(
                message="Cannot transfer a workflow that is not assigned.",
                context={"workflow_id": str(workflow_id)},
            )

        kwargs: dict = {"assigned_agent_id": agent_id}
        if team is not None:
            kwargs["assigned_team"] = team
        if queue is not None:
            kwargs["current_queue"] = queue

        updated = await self._repository.update(workflow_id, **kwargs)
        events: list[DomainEvent] = [
            WorkflowAssigned(
                workflow_id=workflow.id,
                assigned_agent_id=agent_id,
                assigned_team=team or "",
                queue=queue or "",
            )
        ]
        self._logger.info(
            "workflow_transferred",
            workflow_id=str(workflow_id),
            from_agent=str(workflow.assigned_agent_id),
            to_agent=str(agent_id),
        )
        return updated, events

    async def escalate_workflow(
        self,
        workflow_id: uuid.UUID,
        reason: str = "",
    ) -> tuple[Workflow, list[DomainEvent]]:
        workflow = await self.get_workflow(workflow_id)
        self._assert_mutable(workflow)

        current = workflow.escalation_level
        levels = list(EscalationLevel)
        current_index = levels.index(current)

        if current_index >= len(levels) - 1:
            raise WorkflowValidationError(
                message="Workflow is already at the highest escalation level.",
                context={
                    "workflow_id": str(workflow_id),
                    "current_level": current,
                },
            )

        next_level = levels[current_index + 1]
        updated = await self._repository.update(
            workflow_id,
            escalation_level=next_level,
            sla_status=SLAStatus.AT_RISK,
        )
        events: list[DomainEvent] = [
            WorkflowEscalated(
                workflow_id=workflow.id,
                escalation_level=next_level,
                reason=reason,
            )
        ]
        self._logger.info(
            "workflow_escalated",
            workflow_id=str(workflow_id),
            from_level=str(current),
            to_level=str(next_level),
        )
        return updated, events

    async def approve_workflow(
        self,
        workflow_id: uuid.UUID,
        approved_by: uuid.UUID,
    ) -> tuple[Workflow, list[DomainEvent]]:
        workflow = await self.get_workflow(workflow_id)
        self._assert_mutable(workflow)

        if workflow.approval_status not in {ApprovalStatus.PENDING, ApprovalStatus.NOT_REQUIRED}:
            raise WorkflowValidationError(
                message="Workflow approval is already finalised.",
                context={
                    "workflow_id": str(workflow_id),
                    "current_approval": workflow.approval_status,
                },
            )

        updated = await self._repository.update(
            workflow_id,
            approval_status=ApprovalStatus.APPROVED,
        )
        events: list[DomainEvent] = [
            WorkflowApproved(workflow_id=workflow.id, approved_by=approved_by)
        ]
        self._logger.info(
            "workflow_approved",
            workflow_id=str(workflow_id),
            approved_by=str(approved_by),
        )
        return updated, events

    async def reject_workflow(
        self,
        workflow_id: uuid.UUID,
        rejected_by: uuid.UUID,
        reason: str = "",
    ) -> tuple[Workflow, list[DomainEvent]]:
        workflow = await self.get_workflow(workflow_id)
        self._assert_mutable(workflow)

        if workflow.approval_status not in {ApprovalStatus.PENDING, ApprovalStatus.NOT_REQUIRED}:
            raise WorkflowValidationError(
                message="Workflow approval is already finalised.",
                context={
                    "workflow_id": str(workflow_id),
                    "current_approval": workflow.approval_status,
                },
            )

        updated = await self._repository.update(
            workflow_id,
            approval_status=ApprovalStatus.REJECTED,
            workflow_stage=WorkflowStage.REVIEW,
        )
        events: list[DomainEvent] = [
            WorkflowRejected(workflow_id=workflow.id, rejected_by=rejected_by, reason=reason)
        ]
        self._logger.info(
            "workflow_rejected",
            workflow_id=str(workflow_id),
            rejected_by=str(rejected_by),
        )
        return updated, events

    async def complete_workflow(
        self, workflow_id: uuid.UUID
    ) -> tuple[Workflow, list[DomainEvent]]:
        workflow = await self.get_workflow(workflow_id)
        self._assert_mutable(workflow)

        if workflow.approval_status not in {ApprovalStatus.APPROVED, ApprovalStatus.NOT_REQUIRED}:
            raise WorkflowValidationError(
                message="Workflow cannot complete without an approved or not-required approval state.",
                context={
                    "workflow_id": str(workflow_id),
                    "approval_status": workflow.approval_status,
                },
            )

        now = datetime.now(timezone.utc)
        updated = await self._repository.update(
            workflow_id,
            workflow_status=WorkflowStatus.COMPLETED,
            workflow_stage=WorkflowStage.COMPLETED,
            completed_at=now,
            sla_status=SLAStatus.WITHIN_SLA,
        )
        events: list[DomainEvent] = [
            WorkflowCompleted(workflow_id=workflow.id, complaint_id=workflow.complaint_id)
        ]
        self._logger.info("workflow_completed", workflow_id=str(workflow_id))
        return updated, events

    async def archive_workflow(
        self, workflow_id: uuid.UUID
    ) -> tuple[Workflow, list[DomainEvent]]:
        workflow = await self.get_workflow(workflow_id)

        if workflow.workflow_status == WorkflowStatus.ARCHIVED:
            raise WorkflowValidationError(
                message="Workflow is already archived.",
                context={"workflow_id": str(workflow_id)},
            )

        if workflow.workflow_status != WorkflowStatus.COMPLETED:
            raise WorkflowValidationError(
                message="Only completed workflows can be archived.",
                context={
                    "workflow_id": str(workflow_id),
                    "current_status": workflow.workflow_status,
                },
            )

        updated = await self._repository.update(
            workflow_id, workflow_status=WorkflowStatus.ARCHIVED
        )
        events: list[DomainEvent] = [
            WorkflowArchived(workflow_id=workflow.id)
        ]
        self._logger.info("workflow_archived", workflow_id=str(workflow_id))
        return updated, events

    def _assert_mutable(self, workflow: Workflow) -> None:
        if workflow.workflow_status in _IMMUTABLE_STATUSES:
            raise WorkflowValidationError(
                message=f"Cannot modify workflow in status '{workflow.workflow_status}'.",
                context={
                    "workflow_id": str(workflow.id),
                    "current_status": workflow.workflow_status,
                },
            )

    @staticmethod
    def _validate_stage_transition(current: WorkflowStage, target: WorkflowStage) -> None:
        allowed = _STAGE_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise WorkflowValidationError(
                message=f"Cannot transition workflow stage from '{current}' to '{target}'.",
                context={
                    "current_stage": current,
                    "target_stage": target,
                },
            )

    @staticmethod
    def _validate_approval_transition(current: ApprovalStatus, target: ApprovalStatus) -> None:
        allowed = _APPROVAL_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise WorkflowValidationError(
                message=f"Cannot transition approval from '{current}' to '{target}'.",
                context={
                    "current_approval": current,
                    "target_approval": target,
                },
            )
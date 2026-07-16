"""Workflow Pydantic schemas — Workflow domain."""

import uuid
from datetime import datetime

from pydantic import Field

from domains.workflow.constants.workflow_constants import (
    ApprovalStatus,
    EscalationLevel,
    SLAStatus,
    WorkflowStage,
    WorkflowStatus,
)
from shared.base_schema import AppBaseModel, EntitySchema


class WorkflowCreate(AppBaseModel):
    complaint_id: uuid.UUID
    current_queue: str | None = None
    assigned_team: str | None = None
    assigned_agent_id: uuid.UUID | None = None
    priority: str | None = None
    due_at: datetime | None = None


class WorkflowUpdate(AppBaseModel):
    current_queue: str | None = None
    assigned_team: str | None = None
    assigned_agent_id: uuid.UUID | None = None
    workflow_status: WorkflowStatus | None = None
    workflow_stage: WorkflowStage | None = None
    priority: str | None = None
    sla_status: SLAStatus | None = None
    escalation_level: EscalationLevel | None = None
    approval_status: ApprovalStatus | None = None
    due_at: datetime | None = None
    completed_at: datetime | None = None
    workflow_metadata: dict[str, object] | None = None


class WorkflowAssignRequest(AppBaseModel):
    agent_id: uuid.UUID
    team: str | None = None
    queue: str | None = None


class WorkflowTransferRequest(AppBaseModel):
    agent_id: uuid.UUID
    team: str | None = None
    queue: str | None = None


class WorkflowEscalateRequest(AppBaseModel):
    reason: str = ""


class WorkflowApproveRequest(AppBaseModel):
    approved_by: uuid.UUID


class WorkflowRejectRequest(AppBaseModel):
    rejected_by: uuid.UUID
    reason: str = ""


class WorkflowResponse(EntitySchema):
    workflow_number: str | None = None
    complaint_id: uuid.UUID
    current_queue: str | None = None
    assigned_team: str | None = None
    assigned_agent_id: uuid.UUID | None = None
    workflow_status: WorkflowStatus
    workflow_stage: WorkflowStage
    priority: str | None = None
    sla_status: SLAStatus
    escalation_level: EscalationLevel
    approval_status: ApprovalStatus
    started_at: datetime | None = None
    due_at: datetime | None = None
    completed_at: datetime | None = None
    workflow_metadata: dict[str, object] | None = None


class WorkflowSummary(AppBaseModel):
    id: uuid.UUID
    workflow_number: str | None = None
    complaint_id: uuid.UUID
    workflow_status: WorkflowStatus
    workflow_stage: WorkflowStage
    priority: str | None = None
    sla_status: SLAStatus
    escalation_level: EscalationLevel
    assigned_agent_id: uuid.UUID | None = None
    created_at: datetime
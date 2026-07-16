"""Workflow ORM model — Workflow domain."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum as SAEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domains.workflow.constants.workflow_constants import (
    ApprovalStatus,
    EscalationLevel,
    SLAStatus,
    WorkflowStage,
    WorkflowStatus,
)
from shared.base_model import AuditModel


class Workflow(AuditModel):
    __tablename__ = "workflows"

    workflow_number: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True, index=True
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=False, index=True
    )
    current_queue: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    assigned_team: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    assigned_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    workflow_status: Mapped[WorkflowStatus] = mapped_column(
        SAEnum(WorkflowStatus, name="workflow_status", create_constraint=True),
        nullable=False,
        default=WorkflowStatus.PENDING,
        index=True,
    )
    workflow_stage: Mapped[WorkflowStage] = mapped_column(
        SAEnum(WorkflowStage, name="workflow_stage", create_constraint=True),
        nullable=False,
        default=WorkflowStage.INITIATED,
    )
    priority: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sla_status: Mapped[SLAStatus] = mapped_column(
        SAEnum(SLAStatus, name="sla_status", create_constraint=True),
        nullable=False,
        default=SLAStatus.WITHIN_SLA,
    )
    escalation_level: Mapped[EscalationLevel] = mapped_column(
        SAEnum(EscalationLevel, name="escalation_level", create_constraint=True),
        nullable=False,
        default=EscalationLevel.LEVEL_0,
    )
    approval_status: Mapped[ApprovalStatus] = mapped_column(
        SAEnum(ApprovalStatus, name="approval_status", create_constraint=True),
        nullable=False,
        default=ApprovalStatus.NOT_REQUIRED,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    due_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    workflow_metadata: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, default=dict
    )

    complaint = relationship("Complaint", foreign_keys=[complaint_id])
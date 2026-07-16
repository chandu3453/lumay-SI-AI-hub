"""Workflow Domain Events."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from shared.base_event import DomainEvent


@dataclass(frozen=True)
class WorkflowStarted(DomainEvent):
    workflow_id: UUID = field(default_factory=uuid4)
    complaint_id: UUID | None = None
    routing_key: str = field(init=False, default="workflow.started")


@dataclass(frozen=True)
class WorkflowAssigned(DomainEvent):
    workflow_id: UUID = field(default_factory=uuid4)
    assigned_agent_id: UUID = field(default_factory=uuid4)
    assigned_team: str = ""
    queue: str = ""
    routing_key: str = field(init=False, default="workflow.assigned")


@dataclass(frozen=True)
class WorkflowEscalated(DomainEvent):
    workflow_id: UUID = field(default_factory=uuid4)
    escalation_level: str = ""
    reason: str = ""
    routing_key: str = field(init=False, default="workflow.escalated")


@dataclass(frozen=True)
class WorkflowApproved(DomainEvent):
    workflow_id: UUID = field(default_factory=uuid4)
    approved_by: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="workflow.approved")


@dataclass(frozen=True)
class WorkflowRejected(DomainEvent):
    workflow_id: UUID = field(default_factory=uuid4)
    rejected_by: UUID = field(default_factory=uuid4)
    reason: str = ""
    routing_key: str = field(init=False, default="workflow.rejected")


@dataclass(frozen=True)
class WorkflowCompleted(DomainEvent):
    workflow_id: UUID = field(default_factory=uuid4)
    complaint_id: UUID | None = None
    routing_key: str = field(init=False, default="workflow.completed")


@dataclass(frozen=True)
class WorkflowArchived(DomainEvent):
    workflow_id: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="workflow.archived")
"""Complaint Domain Events."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from shared.base_event import DomainEvent


@dataclass(frozen=True)
class ComplaintCreatedEvent(DomainEvent):
    complaint_id: UUID = field(default_factory=uuid4)
    customer_id: UUID | None = None
    category: str = ""
    routing_key: str = field(init=False, default="complaint.created")


@dataclass(frozen=True)
class ComplaintUpdatedEvent(DomainEvent):
    complaint_id: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="complaint.updated")


@dataclass(frozen=True)
class ComplaintAssignedEvent(DomainEvent):
    complaint_id: UUID = field(default_factory=uuid4)
    agent_id: UUID = field(default_factory=uuid4)
    queue: str = ""
    routing_key: str = field(init=False, default="complaint.assigned")


@dataclass(frozen=True)
class ComplaintEscalatedEvent(DomainEvent):
    complaint_id: UUID = field(default_factory=uuid4)
    reason: str = ""
    routing_key: str = field(init=False, default="complaint.escalated")


@dataclass(frozen=True)
class ComplaintResolvedEvent(DomainEvent):
    complaint_id: UUID = field(default_factory=uuid4)
    resolution_summary: str = ""
    routing_key: str = field(init=False, default="complaint.resolved")


@dataclass(frozen=True)
class ComplaintClosedEvent(DomainEvent):
    complaint_id: UUID = field(default_factory=uuid4)
    closure_reason: str = ""
    routing_key: str = field(init=False, default="complaint.closed")


@dataclass(frozen=True)
class ComplaintArchivedEvent(DomainEvent):
    complaint_id: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="complaint.archived")

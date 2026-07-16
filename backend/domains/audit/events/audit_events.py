"""
Audit Domain Events.

The audit domain consumes events from other domains
and writes immutable audit log entries.
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from shared.base_event import DomainEvent


@dataclass(frozen=True)
class AuditEntryCreatedEvent(DomainEvent):
    """Emitted after a new audit log entry has been persisted."""
    audit_id: UUID = field(default_factory=uuid4)
    actor_id: UUID = field(default_factory=uuid4)
    action: str = ""
    resource_type: str = ""
    resource_id: str = ""
    routing_key: str = field(init=False, default="audit.entry_created")

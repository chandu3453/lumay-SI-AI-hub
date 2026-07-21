"""Conversation Domain Events.

Modeled the same way as every other domain's events (`interaction_events.py`,
`complaint_events.py`, ...): immutable dataclasses returned by the service and
not yet dispatched to a bus anywhere in this codebase. Kept consistent so a
future phase can wire dispatch once for all domains at the same time.
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from shared.base_event import DomainEvent


@dataclass(frozen=True)
class ConversationCreatedEvent(DomainEvent):
    conversation_id: UUID = field(default_factory=uuid4)
    customer_id: UUID | None = None
    channel: str = ""
    routing_key: str = field(init=False, default="conversation.created")


@dataclass(frozen=True)
class ConversationStatusChangedEvent(DomainEvent):
    conversation_id: UUID = field(default_factory=uuid4)
    previous_status: str = ""
    new_status: str = ""
    routing_key: str = field(init=False, default="conversation.status_changed")


@dataclass(frozen=True)
class ConversationAssignedEvent(DomainEvent):
    conversation_id: UUID = field(default_factory=uuid4)
    employee_id: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="conversation.assigned")


@dataclass(frozen=True)
class ConversationClosedEvent(DomainEvent):
    conversation_id: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="conversation.closed")

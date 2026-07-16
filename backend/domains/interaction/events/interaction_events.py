"""
Interaction Domain Events.
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from shared.base_event import DomainEvent


@dataclass(frozen=True)
class InteractionReceivedEvent(DomainEvent):
    interaction_id: UUID = field(default_factory=uuid4)
    customer_id: UUID = field(default_factory=uuid4)
    channel: str = ""
    routing_key: str = field(init=False, default="interaction.received")


@dataclass(frozen=True)
class InteractionClassifiedEvent(DomainEvent):
    interaction_id: UUID = field(default_factory=uuid4)
    classification: str = ""
    sentiment_score: float = 0.0
    routing_key: str = field(init=False, default="interaction.classified")


@dataclass(frozen=True)
class InteractionLinkedToComplaintEvent(DomainEvent):
    interaction_id: UUID = field(default_factory=uuid4)
    complaint_id: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="interaction.linked_to_complaint")


@dataclass(frozen=True)
class InteractionUpdatedEvent(DomainEvent):
    interaction_id: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="interaction.updated")


@dataclass(frozen=True)
class InteractionCompletedEvent(DomainEvent):
    interaction_id: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="interaction.completed")


@dataclass(frozen=True)
class InteractionArchivedEvent(DomainEvent):
    interaction_id: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="interaction.archived")

"""Customer Domain Events."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from shared.base_event import DomainEvent


@dataclass(frozen=True)
class CustomerCreatedEvent(DomainEvent):
    customer_id: UUID = field(default_factory=uuid4)
    email: str = ""
    routing_key: str = field(init=False, default="customer.created")


@dataclass(frozen=True)
class CustomerUpdatedEvent(DomainEvent):
    customer_id: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="customer.updated")


@dataclass(frozen=True)
class CustomerMergedEvent(DomainEvent):
    source_customer_id: UUID = field(default_factory=uuid4)
    target_customer_id: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="customer.merged")


@dataclass(frozen=True)
class CustomerActivatedEvent(DomainEvent):
    customer_id: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="customer.activated")


@dataclass(frozen=True)
class CustomerDeactivatedEvent(DomainEvent):
    customer_id: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="customer.deactivated")


@dataclass(frozen=True)
class CustomerArchivedEvent(DomainEvent):
    customer_id: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="customer.archived")

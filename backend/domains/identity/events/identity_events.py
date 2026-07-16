"""Identity domain events."""

import uuid
from dataclasses import dataclass, field

from shared.base_event import DomainEvent


@dataclass(frozen=True)
class UserRegisteredEvent(DomainEvent):
    email: str = ""

    @property
    def routing_key(self) -> str:
        return "identity.user.registered"


@dataclass(frozen=True)
class UserLoggedInEvent(DomainEvent):
    ip_address: str = ""

    @property
    def routing_key(self) -> str:
        return "identity.user.logged_in"


@dataclass(frozen=True)
class UserDeactivatedEvent(DomainEvent):
    deactivated_by: uuid.UUID = field(default_factory=uuid.uuid4)

    @property
    def routing_key(self) -> str:
        return "identity.user.deactivated"


@dataclass(frozen=True)
class PasswordChangedEvent(DomainEvent):
    @property
    def routing_key(self) -> str:
        return "identity.user.password_changed"

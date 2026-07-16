"""Notification Domain Events."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from shared.base_event import DomainEvent


@dataclass(frozen=True)
class NotificationCreatedEvent(DomainEvent):
    notification_id: UUID = field(default_factory=uuid4)
    notification_type: str = ""
    channel: str = ""
    recipient: str = ""
    routing_key: str = field(init=False, default="notification.created")


@dataclass(frozen=True)
class NotificationQueuedEvent(DomainEvent):
    notification_id: UUID = field(default_factory=uuid4)
    channel: str = ""
    scheduled_at: str = ""
    routing_key: str = field(init=False, default="notification.queued")


@dataclass(frozen=True)
class NotificationSentEvent(DomainEvent):
    notification_id: UUID = field(default_factory=uuid4)
    channel: str = ""
    provider: str = ""
    routing_key: str = field(init=False, default="notification.sent")


@dataclass(frozen=True)
class NotificationDeliveredEvent(DomainEvent):
    notification_id: UUID = field(default_factory=uuid4)
    channel: str = ""
    delivered_at: str = ""
    routing_key: str = field(init=False, default="notification.delivered")


@dataclass(frozen=True)
class NotificationFailedEvent(DomainEvent):
    notification_id: UUID = field(default_factory=uuid4)
    channel: str = ""
    error: str = ""
    retry_count: int = 0
    routing_key: str = field(init=False, default="notification.failed")


@dataclass(frozen=True)
class NotificationRetriedEvent(DomainEvent):
    notification_id: UUID = field(default_factory=uuid4)
    attempt: int = 0
    next_retry_at: str = ""
    routing_key: str = field(init=False, default="notification.retried")


@dataclass(frozen=True)
class NotificationArchivedEvent(DomainEvent):
    notification_id: UUID = field(default_factory=uuid4)
    reason: str = ""
    routing_key: str = field(init=False, default="notification.archived")
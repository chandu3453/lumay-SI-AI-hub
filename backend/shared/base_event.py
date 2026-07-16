"""
Domain Event Base.

All domain events inherit from DomainEvent.
Events are immutable value objects published to RabbitMQ.
"""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class DomainEvent:
    """
    Base class for all domain events.

    Fields:
        event_id:    Unique event identifier for idempotency checks.
        occurred_at: UTC timestamp of when the event occurred.
        aggregate_id: ID of the aggregate root that raised this event.
    """

    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    aggregate_id: uuid.UUID = field(default_factory=uuid.uuid4)

    @property
    def routing_key(self) -> str:
        """AMQP routing key — must be overridden by concrete events."""
        raise NotImplementedError

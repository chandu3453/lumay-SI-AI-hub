"""Customer domain events."""
from domains.customer.events.customer_events import (
    CustomerActivatedEvent,
    CustomerArchivedEvent,
    CustomerCreatedEvent,
    CustomerDeactivatedEvent,
    CustomerMergedEvent,
    CustomerUpdatedEvent,
)

__all__ = [
    "CustomerActivatedEvent",
    "CustomerArchivedEvent",
    "CustomerCreatedEvent",
    "CustomerDeactivatedEvent",
    "CustomerMergedEvent",
    "CustomerUpdatedEvent",
]

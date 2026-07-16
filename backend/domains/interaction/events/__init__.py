"""Interaction domain events."""
from domains.interaction.events.interaction_events import (
    InteractionArchivedEvent,
    InteractionClassifiedEvent,
    InteractionCompletedEvent,
    InteractionLinkedToComplaintEvent,
    InteractionReceivedEvent,
    InteractionUpdatedEvent,
)

__all__ = [
    "InteractionArchivedEvent",
    "InteractionClassifiedEvent",
    "InteractionCompletedEvent",
    "InteractionLinkedToComplaintEvent",
    "InteractionReceivedEvent",
    "InteractionUpdatedEvent",
]

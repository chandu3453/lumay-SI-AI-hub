"""Messaging platform — RabbitMQ connection lifecycle and EventPublisher."""

from app.platform.messaging.client import (
    EventPublisher,
    close_messaging,
    get_connection,
    init_messaging,
)

__all__ = [
    "close_messaging",
    "EventPublisher",
    "get_connection",
    "init_messaging",
]

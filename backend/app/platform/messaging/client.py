"""
RabbitMQ Messaging Client.

Manages AMQP connection and channel lifecycle using aio-pika.
Provides a publisher abstraction for domain event publishing.
"""

from typing import Any

import asyncio

import aio_pika
import orjson
from aio_pika import Channel, Connection, ExchangeType, Message
from aio_pika.abc import AbstractRobustConnection

from app.config import get_settings
from app.platform.logging import get_logger

logger = get_logger(__name__)

_connection: AbstractRobustConnection | None = None


async def init_messaging() -> None:
    """Establishes the RabbitMQ connection. Called during application startup."""
    global _connection

    settings = get_settings()

    _connection = await asyncio.wait_for(
        aio_pika.connect_robust(settings.rabbitmq.url, reconnect_interval=5),
        timeout=5,
    )
    logger.info("rabbitmq_connected")


async def close_messaging() -> None:
    """Closes the RabbitMQ connection. Called during application shutdown."""
    global _connection

    if _connection is not None and not _connection.is_closed:
        await _connection.close()
        _connection = None
        logger.info("rabbitmq_connection_closed")


def get_connection() -> AbstractRobustConnection:
    if _connection is None:
        raise RuntimeError("RabbitMQ connection is not initialised. Call init_messaging() first.")
    return _connection


class EventPublisher:
    """
    Publishes domain events to RabbitMQ exchanges.
    Each domain instantiates its own publisher with a dedicated exchange name.
    """

    def __init__(self, exchange_name: str, exchange_type: ExchangeType = ExchangeType.TOPIC) -> None:
        self._exchange_name = exchange_name
        self._exchange_type = exchange_type

    async def publish(
        self,
        routing_key: str,
        payload: dict[str, Any],
        *,
        persistent: bool = True,
    ) -> None:
        """
        Publishes a JSON-serialised payload to the configured exchange.

        Args:
            routing_key: AMQP routing key for message routing.
            payload: Serialisable event payload dictionary.
            persistent: If True, marks the message as durable (survives broker restart).
        """
        connection = get_connection()
        async with connection.channel() as channel:
            exchange = await channel.declare_exchange(
                self._exchange_name,
                self._exchange_type,
                durable=True,
            )

            message = Message(
                body=orjson.dumps(payload),
                content_type="application/json",
                delivery_mode=(
                    aio_pika.DeliveryMode.PERSISTENT
                    if persistent
                    else aio_pika.DeliveryMode.NOT_PERSISTENT
                ),
            )

            await exchange.publish(message, routing_key=routing_key)

            logger.debug(
                "event_published",
                exchange=self._exchange_name,
                routing_key=routing_key,
            )

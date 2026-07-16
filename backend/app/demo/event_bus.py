"""Global Demo Event Bus — broadcasts demo events to SSE subscribers."""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.platform.logging import get_logger

logger = get_logger(__name__)


class DemoEvent:
    def __init__(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        channel: str = "system",
        customer_name: str | None = None,
    ) -> None:
        self.id: str = uuid4().hex[:12]
        self.event_type: str = event_type
        self.data: dict[str, Any] = data or {}
        self.channel: str = channel
        self.customer_name: str | None = customer_name
        self.timestamp: str = datetime.now(timezone.utc).isoformat()


class DemoEventBus:
    _subscribers: list[asyncio.Queue] = []
    _events: list[DemoEvent] = []
    _max_events: int = 200

    @classmethod
    def subscribe(cls) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        cls._subscribers.append(q)
        return q

    @classmethod
    def unsubscribe(cls, q: asyncio.Queue) -> None:
        if q in cls._subscribers:
            cls._subscribers.remove(q)

    @classmethod
    def publish(cls, event: DemoEvent) -> None:
        cls._events.append(event)
        if len(cls._events) > cls._max_events:
            cls._events = cls._events[-cls._max_events:]
        for q in cls._subscribers[:]:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass
        logger.debug(
            "demo_event_published",
            event_type=event.event_type,
            channel=event.channel,
        )

    @classmethod
    def get_recent(cls, limit: int = 50) -> list[dict[str, Any]]:
        return [
            {
                "id": e.id,
                "event_type": e.event_type,
                "data": e.data,
                "channel": e.channel,
                "customer_name": e.customer_name,
                "timestamp": e.timestamp,
            }
            for e in cls._events[-limit:]
        ]

    @classmethod
    def clear(cls) -> None:
        cls._events.clear()


def publish_demo_event(
    event_type: str,
    data: dict[str, Any] | None = None,
    channel: str = "system",
    customer_name: str | None = None,
) -> None:
    DemoEventBus.publish(DemoEvent(
        event_type=event_type,
        data=data,
        channel=channel,
        customer_name=customer_name,
    ))

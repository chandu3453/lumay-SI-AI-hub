"""
Redis Cache Client.

Manages the Redis connection pool lifecycle.
Provides typed cache operations with JSON serialisation.
"""

from typing import Any

import orjson
from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import BusyLoadingError, ConnectionError, TimeoutError

from app.config import get_settings
from app.platform.logging import get_logger

logger = get_logger(__name__)

_redis_client: Redis | None = None


async def _create_client() -> Redis:
    settings = get_settings()

    retry = Retry(
        ExponentialBackoff(cap=10, base=1),
        retries=3,
        supported_errors=(ConnectionError, TimeoutError, BusyLoadingError),
    )

    pool = ConnectionPool.from_url(
        settings.redis.url,
        max_connections=settings.redis.max_connections,
        socket_timeout=5,
        socket_connect_timeout=5,
        decode_responses=False,
        retry=retry,
        retry_on_timeout=True,
    )
    client = Redis(connection_pool=pool)
    logger.info("redis_client_initialized")
    return client


async def init_redis() -> None:
    """Eagerly initialises the Redis client during application startup."""
    global _redis_client

    if _redis_client is None:
        _redis_client = await _create_client()


async def get_redis_client() -> Redis:
    """Returns the shared Redis client. Lazy-initialises if not already created."""
    global _redis_client

    if _redis_client is None:
        _redis_client = await _create_client()

    return _redis_client


async def shutdown_redis() -> None:
    """Closes the Redis connection pool. Called during application shutdown."""
    global _redis_client

    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
        logger.info("redis_client_closed")


class CacheService:
    """
    High-level cache service with JSON serialisation.
    Intended to be extended by domain-specific cache adapters.
    """

    def __init__(self, client: Redis, key_prefix: str = "") -> None:
        self._client = client
        self._prefix = key_prefix

    def _build_key(self, key: str) -> str:
        return f"{self._prefix}:{key}" if self._prefix else key

    async def get(self, key: str) -> Any | None:
        """Returns the deserialised value for the given key, or None."""
        raw = await self._client.get(self._build_key(key))
        return orjson.loads(raw) if raw is not None else None

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Serialises and stores a value. Optional TTL in seconds."""
        serialised = orjson.dumps(value)
        if ttl_seconds:
            await self._client.setex(self._build_key(key), ttl_seconds, serialised)
        else:
            await self._client.set(self._build_key(key), serialised)

    async def delete(self, key: str) -> None:
        """Removes a key from the cache."""
        await self._client.delete(self._build_key(key))

    async def exists(self, key: str) -> bool:
        """Returns True if the key exists in the cache."""
        return bool(await self._client.exists(self._build_key(key)))

    async def ping(self) -> bool:
        """Tests connectivity to Redis."""
        try:
            return await self._client.ping()
        except Exception:
            return False

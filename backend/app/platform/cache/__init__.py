"""Cache platform — Redis connection lifecycle and CacheService."""

from app.platform.cache.client import CacheService, get_redis_client, init_redis, shutdown_redis

__all__ = [
    "CacheService",
    "get_redis_client",
    "init_redis",
    "shutdown_redis",
]

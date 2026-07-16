"""
Health Check Service.

Aggregates dependency health checks and returns a unified health response.
Checks can be run in full (all deps) or critical-only mode.
"""

import time

from app.config import get_settings
from app.platform.cache.client import get_redis_client
from app.platform.database.session import get_engine
from app.platform.health.schemas import DependencyHealth, HealthResponse, HealthStatus
from app.platform.logging import get_logger
from app.platform.search.client import get_search_client
from app.platform.storage.client import get_storage_client

logger = get_logger(__name__)


class HealthCheckService:
    """
    Runs health checks against all registered platform dependencies.
    """

    async def check_all(self) -> HealthResponse:
        """Runs health checks against all dependencies."""
        settings = get_settings()

        checks = await _run_all_checks()
        overall = _aggregate_status(checks)

        return HealthResponse(
            status=overall,
            version=settings.application.version,
            environment=settings.application.environment,
            dependencies=checks,
        )

    async def check_critical(self) -> HealthResponse:
        """Runs health checks against critical dependencies only (database, cache)."""
        settings = get_settings()

        checks = [
            await _check_database(),
            await _check_redis(),
        ]
        overall = _aggregate_status(checks)

        return HealthResponse(
            status=overall,
            version=settings.application.version,
            environment=settings.application.environment,
            dependencies=checks,
        )


async def _run_all_checks() -> list[DependencyHealth]:
    return [
        await _check_database(),
        await _check_redis(),
        await _check_opensearch(),
        await _check_minio(),
    ]


def _aggregate_status(checks: list[DependencyHealth]) -> HealthStatus:
    if any(c.status == HealthStatus.UNHEALTHY for c in checks):
        return HealthStatus.UNHEALTHY
    if any(c.status == HealthStatus.DEGRADED for c in checks):
        return HealthStatus.DEGRADED
    return HealthStatus.HEALTHY


async def _check_database() -> DependencyHealth:
    start = time.perf_counter()
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            from sqlalchemy import text
            await conn.execute(text("SELECT 1"))
        return DependencyHealth(
            name="postgresql",
            status=HealthStatus.HEALTHY,
            latency_ms=round((time.perf_counter() - start) * 1000, 2),
        )
    except Exception as exc:
        return DependencyHealth(
            name="postgresql",
            status=HealthStatus.UNHEALTHY,
            error=str(exc),
        )


async def _check_redis() -> DependencyHealth:
    start = time.perf_counter()
    try:
        client = await get_redis_client()
        await client.ping()
        return DependencyHealth(
            name="redis",
            status=HealthStatus.HEALTHY,
            latency_ms=round((time.perf_counter() - start) * 1000, 2),
        )
    except Exception as exc:
        return DependencyHealth(
            name="redis",
            status=HealthStatus.UNHEALTHY,
            error=str(exc),
        )


async def _check_opensearch() -> DependencyHealth:
    start = time.perf_counter()
    try:
        client = get_search_client()
        await client.ping()
        return DependencyHealth(
            name="opensearch",
            status=HealthStatus.HEALTHY,
            latency_ms=round((time.perf_counter() - start) * 1000, 2),
        )
    except Exception as exc:
        return DependencyHealth(
            name="opensearch",
            status=HealthStatus.DEGRADED,
            error=str(exc),
        )


async def _check_minio() -> DependencyHealth:
    start = time.perf_counter()
    try:
        settings = get_settings()
        client = get_storage_client()
        client.bucket_exists(settings.minio.default_bucket)
        return DependencyHealth(
            name="minio",
            status=HealthStatus.HEALTHY,
            latency_ms=round((time.perf_counter() - start) * 1000, 2),
        )
    except Exception as exc:
        return DependencyHealth(
            name="minio",
            status=HealthStatus.DEGRADED,
            error=str(exc),
        )


def get_health_check_service() -> HealthCheckService:
    """FastAPI dependency provider for HealthCheckService."""
    return HealthCheckService()

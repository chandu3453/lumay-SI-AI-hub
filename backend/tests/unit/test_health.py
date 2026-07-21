"""Health endpoint unit tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.platform.health.checks import HealthCheckService, get_health_check_service
from app.platform.health.schemas import DependencyHealth, HealthResponse, HealthStatus


@pytest.mark.asyncio
async def test_liveness(client: AsyncClient) -> None:
    response = await client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


class _FakeHealthCheckService(HealthCheckService):
    def __init__(self, status: HealthStatus) -> None:
        self._status = status

    async def check_all(self) -> HealthResponse:
        return HealthResponse(
            status=self._status,
            version="test",
            environment="test",
            dependencies=[DependencyHealth(name="postgresql", status=self._status)],
        )

    async def check_critical(self) -> HealthResponse:
        return await self.check_all()


async def _client_with_health_status(status: HealthStatus) -> AsyncClient:
    app = create_app()
    app.dependency_overrides[get_health_check_service] = lambda: _FakeHealthCheckService(status)
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


@pytest.mark.asyncio
async def test_health_returns_200_when_all_dependencies_healthy() -> None:
    async with await _client_with_health_status(HealthStatus.HEALTHY) as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_returns_503_when_database_unhealthy() -> None:
    # The bug this guards against: /health used to unconditionally return
    # "healthy" regardless of whether Postgres was actually reachable.
    async with await _client_with_health_status(HealthStatus.UNHEALTHY) as ac:
        response = await ac.get("/health")
        assert response.status_code == 503
        assert response.json()["status"] == "unhealthy"


@pytest.mark.asyncio
async def test_ready_returns_503_when_database_unhealthy() -> None:
    async with await _client_with_health_status(HealthStatus.UNHEALTHY) as ac:
        response = await ac.get("/health/ready")
        assert response.status_code == 503


@pytest.mark.asyncio
async def test_health_without_initialised_engine_reports_unhealthy_not_a_crash(
    client: AsyncClient,
) -> None:
    # In the test app the global DB engine singleton is never initialised
    # (requests use an overridden per-test session instead) — /health must
    # degrade gracefully to a 503, never raise.
    response = await client.get("/health")
    assert response.status_code == 503
    assert response.json()["status"] == "unhealthy"

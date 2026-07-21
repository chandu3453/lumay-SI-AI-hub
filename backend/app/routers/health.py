"""Health check router — liveness, readiness, and full dependency probes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.platform.health.checks import HealthCheckService, get_health_check_service
from app.platform.health.schemas import HealthResponse, HealthStatus

router = APIRouter(prefix="/health")


@router.get("", summary="Full health check", response_model=HealthResponse)
async def health(
    response: Response,
    service: Annotated[HealthCheckService, Depends(get_health_check_service)],
) -> HealthResponse:
    result = await service.check_all()
    if result.status == HealthStatus.UNHEALTHY:
        response.status_code = 503
    return result


@router.get("/live", summary="Liveness probe")
async def liveness() -> dict:
    return {"status": "alive"}


@router.get("/ready", summary="Readiness probe", response_model=HealthResponse)
async def readiness(
    response: Response,
    service: Annotated[HealthCheckService, Depends(get_health_check_service)],
) -> HealthResponse:
    result = await service.check_critical()
    if result.status != HealthStatus.HEALTHY:
        response.status_code = 503
    return result

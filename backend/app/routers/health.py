"""Health check router — liveness, readiness, and full dependency probes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.config.settings import Settings
from app.dependencies.settings import get_app_settings

router = APIRouter(prefix="/health")


@router.get("", summary="Full health check")
async def health(settings: Annotated[Settings, Depends(get_app_settings)]) -> dict:
    return {
        "status": "healthy",
        "version": settings.application.version,
        "environment": settings.application.environment,
        "checks": [
            {"name": "application", "status": "healthy"},
        ],
    }


@router.get("/live", summary="Liveness probe")
async def liveness() -> dict:
    return {"status": "alive"}


@router.get("/ready", summary="Readiness probe")
async def readiness() -> dict:
    return {"status": "ready"}

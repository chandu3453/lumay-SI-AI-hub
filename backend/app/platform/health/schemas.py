"""
Health Check Response Schemas.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class DependencyHealth(BaseModel):
    name: str
    status: HealthStatus
    latency_ms: float | None = None
    error: str | None = None


class HealthResponse(BaseModel):
    status: HealthStatus
    version: str
    environment: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    dependencies: list[DependencyHealth] = Field(default_factory=list)

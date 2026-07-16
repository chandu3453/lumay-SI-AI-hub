"""Request logging middleware — logs method, path, status, duration, and metadata for every request."""

import time

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.platform.logging import get_logger

logger = get_logger(__name__)

_SKIP_PATHS: frozenset[str] = frozenset({"/health", "/health/live", "/health/ready"})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        t0 = time.perf_counter()
        structlog.contextvars.bind_contextvars(
            method=request.method,
            path=request.url.path,
            client_ip=self._client_ip(request),
            user_agent=request.headers.get("user-agent", ""),
        )
        response = await call_next(request)
        ms = round((time.perf_counter() - t0) * 1000, 2)
        log = logger.bind(status=response.status_code, duration_ms=ms)

        if response.status_code >= 500:
            log.error("request_completed")
        elif response.status_code >= 400:
            log.warning("request_completed")
        else:
            log.info("request_completed")

        return response

    @staticmethod
    def _client_ip(request: Request) -> str:
        fwd = request.headers.get("X-Forwarded-For")
        if fwd:
            return fwd.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

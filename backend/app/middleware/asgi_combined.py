"""Combined ASGI middleware — request ID, correlation ID, logging, security headers.

Uses pure ASGI (not BaseHTTPMiddleware) so it doesn't block
responses that launch long-running background tasks.
"""

import time
import uuid

import structlog
from starlette.types import ASGIApp, Receive, Scope, Send


SKIP_PATHS: frozenset[str] = frozenset({"/health", "/health/live", "/health/ready", "/voice-test"})


class CombinedASGIMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = _get_header(scope, "X-Request-ID") or str(uuid.uuid4())
        correlation_id = _get_header(scope, "X-Correlation-ID") or str(uuid.uuid4())
        t0 = time.perf_counter()

        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            correlation_id=correlation_id,
        )

        sent_headers = False
        skip_security = scope.get("path", "") in SKIP_PATHS

        async def send_wrapper(message: dict) -> None:
            nonlocal sent_headers
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                headers.append((b"X-Request-ID", request_id.encode()))
                headers.append((b"X-Correlation-ID", correlation_id.encode()))
                headers.append((b"X-Content-Type-Options", b"nosniff"))
                headers.append((b"X-Frame-Options", b"DENY"))
                headers.append((b"X-XSS-Protection", b"1; mode=block"))
                headers.append((b"Referrer-Policy", b"strict-origin-when-cross-origin"))
                if not skip_security:
                    headers.append((b"Permissions-Policy", b"geolocation=(), microphone=(), camera=()"))
                message["headers"] = headers
                sent_headers = True
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except GeneratorExit:
            pass

        ms = round((time.perf_counter() - t0) * 1000, 2)
        if sent_headers and scope.get("path") not in SKIP_PATHS:
            _log_request(scope, ms)


def _get_header(scope: Scope, name: str) -> str | None:
    for key, value in scope.get("headers", []):
        if key.lower() == name.lower().encode():
            return value.decode()
    return None


def _log_request(scope: Scope, duration_ms: float) -> None:
    logger = structlog.get_logger(__name__)
    path = scope.get("path", "?")
    logger.info(
        "request_completed",
        method=scope.get("method", "?"),
        path=path,
        duration_ms=duration_ms,
    )

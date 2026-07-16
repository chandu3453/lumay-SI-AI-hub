from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class RequestContext:
    request_id: str
    correlation_id: str
    start_time: datetime
    user_id: str | None = None


def build_context(request) -> RequestContext:
    return RequestContext(
        request_id=getattr(request.state, "request_id", ""),
        correlation_id=getattr(request.state, "correlation_id", ""),
        start_time=datetime.now(timezone.utc),
    )

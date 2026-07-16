"""Analytics REST API — dashboard, trends, SLA, and report endpoints."""

from fastapi import APIRouter, Depends, Query

from app.dependencies.auth import CurrentUser, get_current_user
from app.platform.logging import get_logger
from domains.analytics.services.analytics_service import AnalyticsService
from shared.response_schemas import SuccessResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = get_logger(__name__)

_service = AnalyticsService()


@router.get("/kpis", summary="Dashboard KPIs")
async def get_kpis(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_kpis().model_dump())


@router.get("/trends", summary="Complaint trends")
async def get_trends(
    granularity: str = Query("daily", description="Daily, weekly, or monthly"),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_trends(granularity).model_dump())


@router.get("/sla", summary="SLA compliance metrics")
async def get_sla(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_sla().model_dump())


@router.get("/departments", summary="Department workload")
async def get_departments(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=[d.model_dump() for d in _service.compute_department_workload()])


@router.get("/resolution", summary="Resolution metrics")
async def get_resolution(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_resolution_metrics().model_dump())


@router.get("/customers", summary="Customer metrics")
async def get_customer_metrics(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_customer_metrics().model_dump())


@router.get("/workflows", summary="Workflow analytics")
async def get_workflow_analytics(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_workflow_analytics().model_dump())


@router.get("/notifications", summary="Notification analytics")
async def get_notification_analytics(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_notification_analytics().model_dump())


@router.get("/report", summary="Full analytics report")
async def get_report(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.generate_report().model_dump())


# ---------------------------------------------------------------------------
# Phase 2 Analytics Endpoints (FR-015, FR-017)
# ---------------------------------------------------------------------------

@router.get(
    "/themes",
    summary="Theme distribution (FR-004 / FR-015)",
    description="Returns complaint volume by the 7-bucket LuMay theme taxonomy with trend comparison.",
)
async def get_theme_distribution(
    days: int = Query(30, ge=1, le=365, description="Rolling window in days"),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_theme_distribution(days=days))


@router.get(
    "/escalation-heatmap",
    summary="Escalation risk heatmap (FR-006 / FR-015)",
    description="Returns escalation risk breakdown by risk band, channel, and branch.",
)
async def get_escalation_heatmap(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_escalation_heatmap())


@router.get(
    "/sla-breach-summary",
    summary="SLA breach probability summary (FR-007 / FR-015)",
    description="Returns SLA breach probability distribution and at-risk complaint count.",
)
async def get_sla_breach_summary(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_sla_breach_summary())


@router.get(
    "/repeat-rate",
    summary="Repeat complaint rate (FR-008 / FR-015)",
    description="Returns repeat complaint rate by customer segment and time window.",
)
async def get_repeat_rate(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_repeat_rate())


@router.get(
    "/sentiment-trend",
    summary="Sentiment trend over time (FR-003 / FR-015)",
    description="Returns rolling average sentiment score and trend direction.",
)
async def get_sentiment_trend(
    days: int = Query(30, ge=1, le=365, description="Rolling window in days"),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_sentiment_trend(days=days))


@router.get(
    "/language-split",
    summary="Language distribution (FR-019 / FR-015)",
    description="Returns complaint volume split by detected language (AR / EN / Mixed).",
)
async def get_language_split(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_language_split())


@router.get(
    "/spikes",
    summary="Complaint volume spike detection (FR-015)",
    description="Detects sudden complaint volume increases vs historical baseline. Returns emerging themes.",
)
async def get_spike_detection(
    window_days: int = Query(7, ge=1, le=30, description="Current window in days"),
    baseline_days: int = Query(30, ge=7, le=365, description="Baseline comparison window in days"),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_spike_detection(window_days=window_days, baseline_days=baseline_days))


@router.get(
    "/provider-breakdown",
    summary="Provider & garage complaint breakdown (FR-015)",
    description="Returns complaint volume by provider/garage subcategory.",
)
async def get_provider_breakdown(
    days: int = Query(30, ge=1, le=365, description="Rolling window in days"),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_provider_breakdown(days=days))


@router.get(
    "/product-breakdown",
    summary="Product-level complaint breakdown (FR-015)",
    description="Returns complaint volume split by insurance product type (motor, medical, travel, etc.).",
)
async def get_product_breakdown(
    days: int = Query(30, ge=1, le=365, description="Rolling window in days"),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_service.compute_product_breakdown(days=days))
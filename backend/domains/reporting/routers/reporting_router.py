"""Reporting REST API — Customer 360 + Enterprise Analytics (Sprint 29).
Entirely additive, read-only. Nested under /conversations for the
customer-scoped endpoints (mirrors how Phase 4/5 nested presence/agent-assist
under the same prefix) and under /reporting for the cross-customer analytics."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.dependencies.auth import CurrentUser, get_current_user
from app.dependencies.reporting import get_reporting_service
from domains.complaint.schemas.complaint_schemas import ComplaintPriority
from domains.conversation.constants.conversation_constants import ConversationChannel
from domains.reporting.schemas.reporting_schemas import (
    ConversationAnalyticsSummary,
    ConversationDistributions,
    ConversationTrends,
    Customer360Response,
    CustomerActivityTimelineResponse,
    EmployeeAnalyticsItem,
    SupervisorDashboard,
)
from domains.reporting.services.export_service import rows_to_csv, rows_to_xlsx
from domains.reporting.services.reporting_service import ReportingService
from shared.response_schemas import SuccessResponse

router = APIRouter(tags=["Reporting"])


def _reporting_filters(
    date_from: datetime | None,
    date_to: datetime | None,
    channel: ConversationChannel | None,
    assigned_employee_id: uuid.UUID | None,
    priority: ComplaintPriority | None,
) -> dict:
    return {
        "date_from": date_from,
        "date_to": date_to,
        "channel": channel,
        "assigned_employee_id": assigned_employee_id,
        "priority": priority,
    }


# ── Customer 360 ─────────────────────────────────────────────────────────


@router.get(
    "/customers/{customer_id}/360",
    response_model=SuccessResponse[Customer360Response],
    summary="Unified Customer 360 profile",
)
async def get_customer_360(
    customer_id: uuid.UUID,
    service: ReportingService = Depends(get_reporting_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[Customer360Response]:
    data = await service.get_customer_360(customer_id)
    return SuccessResponse(data=data)


@router.get(
    "/customers/{customer_id}/activity",
    response_model=SuccessResponse[CustomerActivityTimelineResponse],
    summary="Customer activity timeline — chat/voice/complaint/workflow/notification/assignment, merged",
)
async def get_customer_activity(
    customer_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    service: ReportingService = Depends(get_reporting_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[CustomerActivityTimelineResponse]:
    data = await service.get_customer_activity_timeline(customer_id, page=page, page_size=page_size)
    return SuccessResponse(data=data)


# ── Enterprise Analytics ─────────────────────────────────────────────────


@router.get(
    "/reporting/conversations/summary",
    response_model=SuccessResponse[ConversationAnalyticsSummary],
    summary="Conversation KPI summary",
)
async def get_conversation_summary(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    channel: ConversationChannel | None = None,
    assigned_employee_id: uuid.UUID | None = None,
    priority: ComplaintPriority | None = None,
    service: ReportingService = Depends(get_reporting_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ConversationAnalyticsSummary]:
    filters = _reporting_filters(date_from, date_to, channel, assigned_employee_id, priority)
    data = await service.get_conversation_summary(**filters)
    return SuccessResponse(data=data)


@router.get(
    "/reporting/conversations/distributions",
    response_model=SuccessResponse[ConversationDistributions],
    summary="Intent/sentiment/complaint/channel distributions",
)
async def get_conversation_distributions(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    channel: ConversationChannel | None = None,
    assigned_employee_id: uuid.UUID | None = None,
    priority: ComplaintPriority | None = None,
    service: ReportingService = Depends(get_reporting_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ConversationDistributions]:
    filters = _reporting_filters(date_from, date_to, channel, assigned_employee_id, priority)
    data = await service.get_distributions(**filters)
    return SuccessResponse(data=data)


@router.get(
    "/reporting/conversations/trends",
    response_model=SuccessResponse[ConversationTrends],
    summary="Time-bucketed conversation/complaint/sentiment/intent/AI-utilization trends",
)
async def get_conversation_trends(
    granularity: str = Query("day", pattern="^(day|week|month)$"),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    service: ReportingService = Depends(get_reporting_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ConversationTrends]:
    data = await service.get_trends(granularity=granularity, date_from=date_from, date_to=date_to)
    return SuccessResponse(data=data)


@router.get(
    "/reporting/employees",
    response_model=SuccessResponse[list[EmployeeAnalyticsItem]],
    summary="Per-employee workload/resolution/AI-assistance/transfer analytics",
)
async def get_employee_analytics(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    channel: ConversationChannel | None = None,
    assigned_employee_id: uuid.UUID | None = None,
    priority: ComplaintPriority | None = None,
    service: ReportingService = Depends(get_reporting_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[list[EmployeeAnalyticsItem]]:
    filters = _reporting_filters(date_from, date_to, channel, assigned_employee_id, priority)
    data = await service.get_employee_analytics(**filters)
    return SuccessResponse(data=data)


@router.get(
    "/reporting/supervisor/dashboard",
    response_model=SuccessResponse[SupervisorDashboard],
    summary="Live supervisor view — queue, escalations, high-priority complaints, AI/employee presence",
)
async def get_supervisor_dashboard(
    service: ReportingService = Depends(get_reporting_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[SupervisorDashboard]:
    data = await service.get_supervisor_dashboard()
    return SuccessResponse(data=data)


# ── Export ───────────────────────────────────────────────────────────────

_EXPORT_MEDIA_TYPES = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


@router.get(
    "/reporting/export/{report}",
    summary="Export a report as CSV or Excel",
    description="`report` is one of summary|distributions|employees. PDF is not "
    "implemented (501) — CSV/Excel need no external service, PDF rendering does.",
)
async def export_report(
    report: str,
    format: str = Query("csv", pattern="^(csv|xlsx|pdf)$"),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    channel: ConversationChannel | None = None,
    assigned_employee_id: uuid.UUID | None = None,
    priority: ComplaintPriority | None = None,
    service: ReportingService = Depends(get_reporting_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> Response:
    if format == "pdf":
        raise HTTPException(status_code=501, detail="PDF export is not available yet.")

    filters = _reporting_filters(date_from, date_to, channel, assigned_employee_id, priority)
    rows, columns = await _build_export_rows(service, report, filters)

    content = rows_to_csv(rows, columns=columns) if format == "csv" else rows_to_xlsx(
        rows, columns=columns, sheet_title=report
    )
    filename = f"{report}.{format}"
    return Response(
        content=content,
        media_type=_EXPORT_MEDIA_TYPES[format],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


async def _build_export_rows(
    service: ReportingService, report: str, filters: dict
) -> tuple[list[dict], list[str] | None]:
    if report == "summary":
        summary = await service.get_conversation_summary(**filters)
        return [summary.model_dump()], list(summary.model_dump().keys())

    if report == "employees":
        employees = await service.get_employee_analytics(**filters)
        rows = [e.model_dump() for e in employees]
        columns = list(employees[0].model_dump().keys()) if employees else list(
            EmployeeAnalyticsItem.model_fields.keys()
        )
        return rows, columns

    if report == "distributions":
        distributions = await service.get_distributions(**filters)
        rows = [
            {"dimension": "intent", "value": k, "count": v}
            for k, v in distributions.intent_distribution.items()
        ] + [
            {"dimension": "sentiment", "value": k, "count": v}
            for k, v in distributions.sentiment_distribution.items()
        ] + [
            {"dimension": "complaint_category", "value": k, "count": v}
            for k, v in distributions.complaint_distribution.items()
        ] + [
            {"dimension": "channel", "value": k, "count": v}
            for k, v in distributions.channel_distribution.items()
        ]
        return rows, ["dimension", "value", "count"]

    raise HTTPException(
        status_code=400, detail="Unknown report — expected one of summary|distributions|employees."
    )

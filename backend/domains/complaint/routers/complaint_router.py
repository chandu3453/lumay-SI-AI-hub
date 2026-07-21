"""Complaint REST API — Phase 2 endpoints.

Phase 2 additions:
- POST /ingest             : FR-001 omnichannel ingestion endpoint
- POST /{id}/ai-override   : FR-014 human override of AI fields
- POST /{id}/analyze       : FR-010 trigger AI analysis on demand
- GET  /{id}/ai-analysis   : FR-020 retrieve full AI analysis result
- POST /{id}/acknowledge   : FR-007 record acknowledgment time
- GET  /{id}/sla-status    : FR-007 real-time SLA status
- GET  /{id}/related       : FR-008 related/repeat complaints
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status

from app.dependencies.auth import CurrentUser, get_current_active_user, get_current_user
from app.dependencies.complaint import get_complaint_service
from domains.complaint.constants.complaint_constants import (
    ComplaintCategory,
    ComplaintPriority,
    ComplaintSeverity,
    ComplaintStatus,
)
from domains.complaint.schemas.complaint_schemas import (
    AIOverrideRequest,
    ComplaintAssignRequest,
    ComplaintCreate,
    ComplaintIngestRequest,
    ComplaintIngestResponse,
    ComplaintResponse,
    ComplaintSummary,
    ComplaintUpdate,
    RelatedComplaintSummary,
)
from domains.complaint.services.complaint_service import ComplaintService
from app.platform.logging import get_logger
from shared.response_schemas import PaginatedResponse, SuccessResponse

router = APIRouter(prefix="/complaints", tags=["Complaints"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# FR-001 — Omnichannel Ingestion
# ---------------------------------------------------------------------------
@router.post(
    "/ingest",
    response_model=SuccessResponse[ComplaintIngestResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Ingest interaction (FR-001)",
    description=(
        "FR-001: Structured omnichannel ingestion endpoint for SMART CALL, WhatsApp, "
        "email and CRM webhooks. Creates or updates a complaint case and triggers AI analysis."
    ),
)
async def ingest_interaction(
    body: ComplaintIngestRequest,
    background_tasks: BackgroundTasks,
    service: ComplaintService = Depends(get_complaint_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ComplaintIngestResponse]:
    """FR-001: Ingest an omnichannel interaction and create a complaint case."""
    from domains.complaint.constants.complaint_constants import ComplaintSource

    # Map channel to source
    channel_to_source: dict[str, ComplaintSource] = {
        "voice": ComplaintSource.PHONE,
        "whatsapp": ComplaintSource.WHATSAPP,
        "web_chat": ComplaintSource.WEB_CHAT,
        "email": ComplaintSource.EMAIL,
        "smart_call": ComplaintSource.SMART_CALL,
        "crm": ComplaintSource.AGENT_ENTERED,
        "agent_entered": ComplaintSource.AGENT_ENTERED,
    }
    source = channel_to_source.get(body.channel.lower(), ComplaintSource.WEB_FORM)

    # Build title from transcript / email body
    transcript = body.transcript or body.email_body or ""
    title_text = transcript[:200].strip() if transcript else f"Complaint via {body.channel}"

    create_data = ComplaintCreate(
        customer_id=body.customer_id,
        title=title_text,
        description=transcript,
        category=ComplaintCategory.GENERAL,
        source=source,
        channel=body.channel,
        policy_number=body.policy_number,
        claim_number=body.claim_number,
        product=body.product,
        detected_language=body.language or "en",
    )

    complaint, _ = await service.create_complaint(create_data)
    background_tasks.add_task(service.trigger_ai_analysis, complaint.id)

    from domains.conversation.integration_hooks import on_complaint_filed_manually

    background_tasks.add_task(
        on_complaint_filed_manually, body.customer_id, complaint.id, complaint.complaint_number
    )

    return SuccessResponse(
        data=ComplaintIngestResponse(
            complaint_id=complaint.id,
            complaint_number=complaint.complaint_number,
            action="created",
            ai_analysis_queued=True,
            message=f"Complaint created from {body.channel} interaction. AI analysis queued.",
        )
    )


# ---------------------------------------------------------------------------
# Core CRUD
# ---------------------------------------------------------------------------
@router.post(
    "",
    response_model=SuccessResponse[ComplaintResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a complaint",
    description="Creates a new complaint. Triggers AI analysis as a background task (FR-010).",
)
async def create_complaint(
    body: ComplaintCreate,
    background_tasks: BackgroundTasks,
    service: ComplaintService = Depends(get_complaint_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ComplaintResponse]:
    complaint, _ = await service.create_complaint(body)
    # FR-010: Trigger AI analysis in the background
    background_tasks.add_task(service.trigger_ai_analysis, complaint.id)

    from domains.conversation.integration_hooks import on_complaint_filed_manually

    background_tasks.add_task(
        on_complaint_filed_manually, body.customer_id, complaint.id, complaint.complaint_number
    )

    return SuccessResponse(data=ComplaintResponse.model_validate(complaint))


@router.get(
    "",
    response_model=PaginatedResponse[ComplaintSummary],
    summary="List complaints",
    description="Returns a paginated list of complaints with optional Phase 2 filters.",
)
async def list_complaints(
    customer_id: uuid.UUID | None = Query(None, description="Filter by customer"),
    status: ComplaintStatus | None = Query(None, description="Filter by status"),
    category: ComplaintCategory | None = Query(None, description="Filter by category"),
    priority: ComplaintPriority | None = Query(None, description="Filter by priority"),
    severity: ComplaintSeverity | None = Query(None, description="Filter by severity"),
    theme: str | None = Query(None, description="Filter by FR-004 theme"),
    sla_risk: str | None = Query(None, description="Filter by SLA risk: within_sla, at_risk, breached"),
    is_repeat: bool | None = Query(None, description="Filter repeat complaints"),
    detected_language: str | None = Query(None, description="Filter by language: ar, en, mixed"),
    escalation_risk_min: int | None = Query(None, ge=0, le=100, description="Min escalation risk score"),
    product: str | None = Query(None, description="Filter by product type (motor, medical, etc.)"),
    channel: str | None = Query(None, description="Filter by channel (voice, whatsapp, etc.)"),
    regulatory_flag: bool | None = Query(None, description="Filter by regulatory flag"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    service: ComplaintService = Depends(get_complaint_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> PaginatedResponse[ComplaintSummary]:
    items, total = await service.list_complaints(
        customer_id=customer_id,
        status=status,
        category=category,
        priority=priority,
        severity=severity,
        theme=theme,
        sla_risk=sla_risk,
        is_repeat=is_repeat,
        detected_language=detected_language,
        escalation_risk_min=escalation_risk_min,
        product=product,
        channel=channel,
        regulatory_flag=regulatory_flag,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        data=[ComplaintSummary.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get(
    "/{complaint_id}",
    response_model=SuccessResponse[ComplaintResponse],
    summary="Get complaint by ID",
    description="Returns a single complaint with all Phase 2 AI intelligence fields.",
)
async def get_complaint(
    complaint_id: uuid.UUID,
    service: ComplaintService = Depends(get_complaint_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ComplaintResponse]:
    complaint = await service.get_complaint(complaint_id)
    return SuccessResponse(data=ComplaintResponse.model_validate(complaint))


@router.patch(
    "/{complaint_id}",
    response_model=SuccessResponse[ComplaintResponse],
    summary="Update a complaint",
    description="Updates an existing complaint. Terminal-status complaints are read-only.",
)
async def update_complaint(
    complaint_id: uuid.UUID,
    body: ComplaintUpdate,
    service: ComplaintService = Depends(get_complaint_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ComplaintResponse]:
    complaint, _ = await service.update_complaint(complaint_id, body)

    from domains.conversation.integration_hooks import on_complaint_lifecycle

    await on_complaint_lifecycle(service._repository._session, complaint, "complaint.updated")

    return SuccessResponse(data=ComplaintResponse.model_validate(complaint))


# ---------------------------------------------------------------------------
# Phase 2 — AI & Intelligence Endpoints
# ---------------------------------------------------------------------------
@router.post(
    "/{complaint_id}/ai-override",
    response_model=SuccessResponse[ComplaintResponse],
    summary="Override AI classification (FR-014)",
    description=(
        "Allows an agent to override AI-generated fields (category, theme, severity, "
        "sentiment, root_cause, regulatory_flag). Original AI values are preserved in ai_override_log for audit."
    ),
)
async def override_ai_classification(
    complaint_id: uuid.UUID,
    body: AIOverrideRequest,
    service: ComplaintService = Depends(get_complaint_service),
    current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ComplaintResponse]:
    complaint, _ = await service.apply_ai_override(
        complaint_id=complaint_id,
        override=body,
        agent_id=current_user.user_id,
    )

    from domains.conversation.integration_hooks import on_complaint_lifecycle

    await on_complaint_lifecycle(service._repository._session, complaint, "complaint.ai_override_applied")

    return SuccessResponse(data=ComplaintResponse.model_validate(complaint))


@router.post(
    "/{complaint_id}/analyze",
    response_model=SuccessResponse[ComplaintResponse],
    summary="Trigger AI analysis (FR-010)",
    description=(
        "Runs the full Phase 2 AI analysis pipeline on the complaint and stores results. "
        "Use when complaint was created manually or to refresh AI fields."
    ),
)
async def analyze_complaint(
    complaint_id: uuid.UUID,
    service: ComplaintService = Depends(get_complaint_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ComplaintResponse]:
    complaint = await service.run_ai_analysis(complaint_id)

    from domains.conversation.integration_hooks import on_complaint_lifecycle

    # `run_ai_analysis` emits no DomainEvent (confirmed — it returns a bare
    # Complaint), so this is the one complaint lifecycle hook with a synthetic
    # event_type rather than a reused routing-key string.
    await on_complaint_lifecycle(
        service._repository._session,
        complaint,
        "complaint.intelligence_result",
        {
            "category": str(complaint.category) if complaint.category else None,
            "severity": str(complaint.severity) if complaint.severity else None,
            "priority": str(complaint.priority) if complaint.priority else None,
            "sentiment": complaint.sentiment,
        },
    )

    return SuccessResponse(data=ComplaintResponse.model_validate(complaint))


@router.get(
    "/{complaint_id}/ai-analysis",
    response_model=SuccessResponse[dict],
    summary="Get AI analysis result (FR-020)",
    description=(
        "FR-020: Returns the full AI analysis result for a complaint including all "
        "confidence scores, supporting excerpts, rules triggered, and human overrides."
    ),
)
async def get_ai_analysis(
    complaint_id: uuid.UUID,
    service: ComplaintService = Depends(get_complaint_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[dict]:
    """FR-020: Return complete AI analysis with full explainability data."""
    complaint = await service.get_complaint(complaint_id)
    analysis: dict[str, Any] = {
        "complaint_id": str(complaint.id),
        "complaint_number": complaint.complaint_number,
        # FR-002
        "detection": {
            "is_complaint": complaint.complaint_detected,
            "detection_type": complaint.detection_type,
            "confidence": complaint.detection_confidence,
            "primary_statement": complaint.primary_complaint_statement,
        },
        # FR-003
        "sentiment": {
            "overall": complaint.sentiment,
            "start": complaint.sentiment_start,
            "end": complaint.sentiment_end,
            "trend": complaint.sentiment_trend,
            "target": complaint.sentiment_target,
            "polarity": complaint.sentiment_polarity,
            "intensity": complaint.sentiment_intensity,
            "emotions": complaint.sentiment_emotions,
        },
        # FR-004
        "theme": {
            "primary": complaint.theme,
            "secondary": complaint.theme_secondary,
            "keywords": complaint.theme_keywords,
        },
        # FR-005
        "severity": {
            "level": str(complaint.severity),
            "score": complaint.severity_score,
            "auto_escalation_triggers": complaint.auto_escalation_triggers,
        },
        # FR-006
        "escalation": {
            "risk_score": complaint.escalation_risk_score,
            "risk_level": complaint.escalation_risk_level,
            "triggers": complaint.escalation_triggers,
        },
        # FR-007
        "sla": {
            "risk": complaint.sla_risk,
            "breach_probability": complaint.sla_breach_probability,
            "hours_remaining": complaint.sla_hours_remaining,
            "resolution_deadline": complaint.resolution_deadline,
            "acknowledged_time": complaint.acknowledged_time,
        },
        # FR-008
        "repeat": {
            "is_repeat": complaint.is_repeat,
            "prior_count": complaint.prior_complaint_count,
            "window_days": complaint.repeat_window_days,
            "prior_ids": complaint.prior_complaint_ids,
        },
        # FR-016
        "root_cause": {
            "cause": complaint.root_cause,
            "category": complaint.root_cause_category,
            "factors": complaint.contributing_factors,
            "failure_point": complaint.process_failure_point,
        },
        # FR-019
        "language": {
            "detected": complaint.detected_language,
            "arabic_percentage": complaint.arabic_percentage,
        },
        # FR-020
        "explainability": {
            "ai_explanation": complaint.ai_explanation,
            "routing_rule": complaint.routing_rule,
            "recommendation": complaint.recommendation,
        },
        # FR-014
        "human_overrides": complaint.ai_override_log or [],
        "human_validation": complaint.human_validation,
        "regulatory_flag": complaint.regulatory_flag,
    }
    return SuccessResponse(data=analysis)


# ---------------------------------------------------------------------------
# FR-007 — SLA Endpoints
# ---------------------------------------------------------------------------
@router.post(
    "/{complaint_id}/acknowledge",
    response_model=SuccessResponse[ComplaintResponse],
    summary="Acknowledge complaint (FR-007)",
    description=(
        "FR-007: Records the acknowledgment timestamp, recalculates SLA status, "
        "and transitions status from SUBMITTED to UNDER_REVIEW."
    ),
)
async def acknowledge_complaint(
    complaint_id: uuid.UUID,
    service: ComplaintService = Depends(get_complaint_service),
    current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ComplaintResponse]:
    complaint, _ = await service.acknowledge_complaint(
        complaint_id=complaint_id,
        agent_id=current_user.user_id if current_user else None,
    )

    from domains.conversation.integration_hooks import on_complaint_lifecycle

    await on_complaint_lifecycle(service._repository._session, complaint, "complaint.acknowledged")

    return SuccessResponse(data=ComplaintResponse.model_validate(complaint))


@router.get(
    "/{complaint_id}/sla-status",
    response_model=SuccessResponse[dict],
    summary="Real-time SLA status (FR-007)",
    description=(
        "FR-007: Returns the real-time SLA status with time remaining, breach probability, "
        "deadline timestamp, and recommended action."
    ),
)
async def get_sla_status(
    complaint_id: uuid.UUID,
    service: ComplaintService = Depends(get_complaint_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[dict]:
    sla_data = await service.get_sla_status(complaint_id)
    return SuccessResponse(data=sla_data)


# ---------------------------------------------------------------------------
# FR-008 — Related Complaints
# ---------------------------------------------------------------------------
@router.get(
    "/{complaint_id}/related",
    response_model=SuccessResponse[list[RelatedComplaintSummary]],
    summary="Get related complaints (FR-008)",
    description=(
        "FR-008: Returns complaints from the same customer with the same or related theme. "
        "Used to detect repeat complaints and view complaint history."
    ),
)
async def get_related_complaints(
    complaint_id: uuid.UUID,
    limit: int = Query(10, ge=1, le=50, description="Max related complaints to return"),
    service: ComplaintService = Depends(get_complaint_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[list[RelatedComplaintSummary]]:
    related = await service.get_related_complaints(complaint_id, limit=limit)
    now = datetime.now(tz=timezone.utc)
    result = []
    for r in related:
        days_ago = None
        if r.created_at:
            try:
                created = r.created_at
                if created.tzinfo is None:
                    from datetime import timezone as tz_
                    created = created.replace(tzinfo=tz_.utc)
                days_ago = max((now - created).days, 0)
            except Exception:
                pass
        result.append(RelatedComplaintSummary(
            id=r.id,
            complaint_number=r.complaint_number,
            title=r.title,
            theme=r.theme,
            severity=str(r.severity),
            status=str(r.status),
            created_at=r.created_at,
            days_ago=days_ago,
        ))
    return SuccessResponse(data=result)


# ---------------------------------------------------------------------------
# Lifecycle Actions
# ---------------------------------------------------------------------------
@router.post(
    "/{complaint_id}/assign",
    response_model=SuccessResponse[ComplaintResponse],
    summary="Assign a complaint",
    description="Assigns a complaint to an agent and optionally a queue.",
)
async def assign_complaint(
    complaint_id: uuid.UUID,
    body: ComplaintAssignRequest,
    service: ComplaintService = Depends(get_complaint_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ComplaintResponse]:
    complaint, _ = await service.assign_complaint(
        complaint_id, agent_id=body.agent_id, queue=body.queue
    )

    from domains.conversation.integration_hooks import on_complaint_lifecycle

    await on_complaint_lifecycle(
        service._repository._session,
        complaint,
        "complaint.assigned",
        {"queue": body.queue},
        assigned_agent_id=body.agent_id,
    )

    return SuccessResponse(data=ComplaintResponse.model_validate(complaint))


@router.post(
    "/{complaint_id}/escalate",
    response_model=SuccessResponse[ComplaintResponse],
    summary="Escalate a complaint",
    description="Transitions a complaint to ESCALATED status.",
)
async def escalate_complaint(
    complaint_id: uuid.UUID,
    service: ComplaintService = Depends(get_complaint_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ComplaintResponse]:
    complaint, _ = await service.escalate_complaint(complaint_id)

    from domains.conversation.integration_hooks import on_complaint_lifecycle

    await on_complaint_lifecycle(service._repository._session, complaint, "complaint.escalated")

    return SuccessResponse(data=ComplaintResponse.model_validate(complaint))


@router.post(
    "/{complaint_id}/resolve",
    response_model=SuccessResponse[ComplaintResponse],
    summary="Resolve a complaint",
    description="Transitions a complaint to RESOLVED status.",
)
async def resolve_complaint(
    complaint_id: uuid.UUID,
    service: ComplaintService = Depends(get_complaint_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ComplaintResponse]:
    complaint, _ = await service.resolve_complaint(complaint_id)

    from domains.conversation.integration_hooks import on_complaint_lifecycle

    await on_complaint_lifecycle(service._repository._session, complaint, "complaint.resolved")

    return SuccessResponse(data=ComplaintResponse.model_validate(complaint))


@router.post(
    "/{complaint_id}/close",
    response_model=SuccessResponse[ComplaintResponse],
    summary="Close a complaint",
    description="Transitions a complaint to CLOSED status. Closed complaints are read-only.",
)
async def close_complaint(
    complaint_id: uuid.UUID,
    service: ComplaintService = Depends(get_complaint_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ComplaintResponse]:
    complaint, _ = await service.close_complaint(complaint_id)

    from domains.conversation.integration_hooks import on_complaint_lifecycle

    await on_complaint_lifecycle(service._repository._session, complaint, "complaint.closed")

    return SuccessResponse(data=ComplaintResponse.model_validate(complaint))


@router.post(
    "/{complaint_id}/archive",
    response_model=SuccessResponse[ComplaintResponse],
    summary="Archive a complaint",
    description="Transitions a complaint to ARCHIVED status. Archived complaints are read-only.",
)
async def archive_complaint(
    complaint_id: uuid.UUID,
    service: ComplaintService = Depends(get_complaint_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ComplaintResponse]:
    complaint, _ = await service.archive_complaint(complaint_id)

    from domains.conversation.integration_hooks import on_complaint_lifecycle

    await on_complaint_lifecycle(service._repository._session, complaint, "complaint.archived")

    return SuccessResponse(data=ComplaintResponse.model_validate(complaint))

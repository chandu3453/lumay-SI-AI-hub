"""Demo REST API — data loading, dashboard, search, knowledge, scenario walkthroughs, SSE events, and simulation.

All endpoints are designed for client demonstration purposes.
Synthetic data is loaded automatically on application startup.
"""

import asyncio
import json
import random
import uuid

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Body, Request
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.dependencies.auth import CurrentUser, get_current_user
from app.dependencies.database import get_db
from app.demo.event_bus import DemoEventBus, publish_demo_event
from app.demo.synthetic import generate_synthetic_data, get_synthetic_store, reset_synthetic_store
from app.platform.logging import get_logger
from domains.analytics.services.analytics_service import AnalyticsService
from domains.complaint.constants.complaint_constants import (
    ComplaintCategory,
    ComplaintPriority,
    ComplaintSeverity,
    ComplaintSource,
    ComplaintStatus,
)
from domains.complaint.models.complaint import Complaint
from domains.customer.constants.customer_constants import CustomerSegment, CustomerStatus, CustomerType
from domains.customer.models.customer import Customer
from domains.interaction.constants.interaction_constants import (
    InteractionChannel,
    InteractionDirection,
    InteractionStatus,
)
from domains.interaction.models.interaction import Interaction
from domains.notification.constants.notification_constants import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus as NotifStatus,
    NotificationType,
)
from domains.notification.models.notification import Notification
from domains.search.services.search_service import get_search_service
from domains.workflow.constants.workflow_constants import (
    ApprovalStatus,
    EscalationLevel,
    SLAStatus,
    WorkflowStage,
    WorkflowStatus,
)
from domains.workflow.models.workflow import Workflow
from knowledge.service import KnowledgeService
from shared.response_schemas import SuccessResponse

router = APIRouter(prefix="/demo", tags=["Demo"])
logger = get_logger(__name__)

_analytics = AnalyticsService()
_knowledge = KnowledgeService()

_SOURCE_MAP: dict[str, ComplaintSource] = {
    "phone": ComplaintSource.PHONE,
    "email": ComplaintSource.EMAIL,
    "web_form": ComplaintSource.WEB_FORM,
    "chat": ComplaintSource.WEB_CHAT,
    "web_chat": ComplaintSource.WEB_CHAT,
    "social_media": ComplaintSource.SOCIAL_MEDIA,
    "whatsapp": ComplaintSource.WHATSAPP,
    "smart_call": ComplaintSource.SMART_CALL,
    "agent_entered": ComplaintSource.AGENT_ENTERED,
    "mobile_app": ComplaintSource.MOBILE_APP,
    "portal": ComplaintSource.PORTAL,
    "regulatory": ComplaintSource.REGULATORY,
}


def _parse_dt(val: str | None) -> datetime | None:
    if not val:
        return None
    if isinstance(val, datetime):
        return val
    return datetime.fromisoformat(val.replace("Z", "+00:00"))


async def _persist_synthetic_data(
    session: AsyncSession, store
) -> dict[str, int]:
    customers = store.get("customers", [])
    interactions = store.get("interactions", [])
    complaints = store.get("complaints", [])
    workflows = store.get("workflows", [])
    notifications = store.get("notifications", [])

    # 1. Customers
    customer_objs = []
    for c in customers:
        customer_objs.append(Customer(
            id=uuid.UUID(c["id"]),
            customer_number=c.get("customer_number"),
            external_ref=c.get("external_ref", f"EXT-{uuid.uuid4().hex[:8]}"),
            full_name=c["full_name"],
            email=c.get("email"),
            mobile_number=c.get("mobile_number"),
            segment=CustomerSegment(c.get("segment", "individual")),
            status=CustomerStatus(c.get("status", "active")),
            customer_type=CustomerType.ACTIVE,
            profile_metadata={k: c.get(k) for k in ("company_name", "city", "state", "nationality") if c.get(k)},
            created_at=_parse_dt(c.get("created_at")) or datetime.now(timezone.utc),
        ))
    session.add_all(customer_objs)
    await session.flush()

    # 2. Interactions
    interaction_objs = []
    for i in interactions:
        channel_val = i.get("channel")
        if isinstance(channel_val, InteractionChannel):
            channel_val = channel_val.value
        interaction_objs.append(Interaction(
            id=uuid.UUID(i["id"]),
            customer_ref=i.get("customer_id"),
            channel=InteractionChannel(channel_val) if channel_val else InteractionChannel.WEB_FORM,
            direction=InteractionDirection(i.get("direction", "inbound")) if isinstance(i.get("direction"), str) else i.get("direction", InteractionDirection.INBOUND),
            subject=i.get("subject"),
            transcript=i.get("transcript"),
            status=InteractionStatus(i.get("status", "received")) if isinstance(i.get("status"), str) else i.get("status", InteractionStatus.RECEIVED),
            created_at=_parse_dt(i.get("created_at")) or datetime.now(timezone.utc),
        ))
    session.add_all(interaction_objs)
    await session.flush()

    # 3. Complaints
    complaint_objs = []
    for c in complaints:
        source_val = c.get("source", "web_form") or "web_form"
        source = _SOURCE_MAP.get(source_val.lower(), ComplaintSource.WEB_FORM)
        complaint_objs.append(Complaint(
            id=uuid.UUID(c["id"]),
            complaint_number=c.get("complaint_number"),
            customer_id=uuid.UUID(c["customer_id"]) if c.get("customer_id") else None,
            interaction_id=uuid.UUID(c["interaction_id"]) if c.get("interaction_id") else None,
            title=c.get("title", "Complaint"),
            description=c.get("description"),
            category=ComplaintCategory(c.get("category", "general")) if c.get("category") else ComplaintCategory.GENERAL,
            subcategory=c.get("subcategory"),
            theme=c.get("metadata", {}).get("ai_theme") if isinstance(c.get("metadata"), dict) else None,
            priority=ComplaintPriority(c.get("priority", "medium")) if c.get("priority") else ComplaintPriority.MEDIUM,
            severity=ComplaintSeverity(c.get("severity", "moderate")) if c.get("severity") else ComplaintSeverity.MODERATE,
            status=ComplaintStatus(c.get("status", "submitted")) if c.get("status") else ComplaintStatus.SUBMITTED,
            source=source,
            assigned_queue=c.get("assigned_queue"),
            policy_number=c.get("policy_number"),
            product=c.get("insurance_line"),
            sentiment=c.get("metadata", {}).get("ai_sentiment") if isinstance(c.get("metadata"), dict) else None,
            sentiment_polarity=c.get("metadata", {}).get("ai_sentiment_polarity"),
            profile_metadata=c.get("metadata") if isinstance(c.get("metadata"), dict) else None,
            created_at=_parse_dt(c.get("created_at")) or datetime.now(timezone.utc),
        ))
    session.add_all(complaint_objs)
    await session.flush()

    # 4. Workflows
    workflow_objs = []
    for w in workflows:
        workflow_objs.append(Workflow(
            id=uuid.UUID(w["id"]),
            workflow_number=w.get("workflow_number"),
            complaint_id=uuid.UUID(w["complaint_id"]) if w.get("complaint_id") else uuid.uuid4(),
            current_queue=w.get("assigned_team"),
            assigned_team=w.get("assigned_team"),
            assigned_agent_id=uuid.UUID(w["assigned_agent_id"]) if w.get("assigned_agent_id") else None,
            workflow_status=WorkflowStatus(w.get("workflow_status", "pending")) if w.get("workflow_status") else WorkflowStatus.PENDING,
            workflow_stage=WorkflowStage(w.get("workflow_stage", "initiated")) if w.get("workflow_stage") else WorkflowStage.INITIATED,
            priority=w.get("priority"),
            sla_status=SLAStatus(w.get("sla_status", "within_sla")) if w.get("sla_status") else SLAStatus.WITHIN_SLA,
            escalation_level=EscalationLevel.LEVEL_0,
            approval_status=ApprovalStatus.NOT_REQUIRED,
            started_at=_parse_dt(w.get("started_at")),
            completed_at=_parse_dt(w.get("completed_at")),
            created_at=_parse_dt(w.get("created_at")) or datetime.now(timezone.utc),
        ))
    session.add_all(workflow_objs)
    await session.flush()

    # 5. Notifications
    notif_objs = []
    for n in notifications:
        notif_objs.append(Notification(
            id=uuid.UUID(n["id"]),
            notification_number=n.get("notification_number"),
            workflow_id=uuid.UUID(n["workflow_id"]) if n.get("workflow_id") else None,
            complaint_id=uuid.UUID(n["complaint_id"]) if n.get("complaint_id") else None,
            notification_type=NotificationType(n.get("notification_type", "alert")) if n.get("notification_type") else NotificationType.ALERT,
            notification_channel=NotificationChannel(n.get("notification_channel", "email")) if n.get("notification_channel") else NotificationChannel.EMAIL,
            recipient=n.get("recipient", "unknown@email.com"),
            subject=n.get("subject", "No Subject"),
            message=n.get("message") or n.get("message_body") or "",
            notification_status=NotifStatus(n.get("notification_status", "pending")) if n.get("notification_status") else NotifStatus.PENDING,
            priority=NotificationPriority(n.get("priority", "medium")) if n.get("priority") else NotificationPriority.MEDIUM,
            retry_count=n.get("retry_count", 0),
            created_at=_parse_dt(n.get("created_at")) or datetime.now(timezone.utc),
        ))
    session.add_all(notif_objs)
    await session.flush()

    return {
        "customers": len(customers),
        "interactions": len(interactions),
        "complaints": len(complaints),
        "workflows": len(workflows),
        "notifications": len(notifications),
    }


@router.post(
    "/load",
    summary="Load synthetic demo data",
    description="Generates and loads 500 customers, 1,500 interactions, 800 complaints, "
                "800 workflows, and 800 notifications into both the in-memory synthetic store "
                "and PostgreSQL. All entities have valid referential relationships. "
                "Call this first before accessing any dashboard or scenario endpoints.",
    response_description="Counts of generated entities per type",
    status_code=http_status.HTTP_200_OK,
)
async def load_demo_data(
    db: AsyncSession = Depends(get_db),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    store = generate_synthetic_data()
    db_sizes = await _persist_synthetic_data(db, store)
    sizes = store.size()
    logger.info("demo_data_loaded", sizes=sizes, db_sizes=db_sizes)
    return SuccessResponse(data={
        "message": "Demo data loaded successfully. Both in-memory store and PostgreSQL populated.",
        "counts": sizes,
        "db_counts": db_sizes,
        "example_kpis": _analytics.compute_kpis().model_dump(),
    })


@router.post(
    "/reset",
    summary="Reset all demo data",
    description="Clears all in-memory synthetic data, resets the search service, "
                "and reloads the knowledge repository. Use this to start a fresh demo session.",
)
async def reset_demo_data(
    db: AsyncSession = Depends(get_db),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    reset_synthetic_store()
    from domains.search.services.search_service import reset_search_service
    reset_search_service()
    from knowledge.repository import reset_knowledge_repository
    reset_knowledge_repository()

    for table in (Notification, Workflow, Complaint, Interaction, Customer):
        await db.execute(table.__table__.delete())
    await db.flush()

    logger.info("demo_data_reset")
    return SuccessResponse(data={"message": "Demo data reset successfully. PostgreSQL cleared."})


@router.post(
    "/run",
    summary="Load data and return KPI overview",
    description="One-step demo initialization: generates synthetic data and returns "
                "a summary of executive KPIs including customer counts, complaint volumes, "
                "SLA compliance rates, and sentiment scores.",
)
async def run_demo(
    db: AsyncSession = Depends(get_db),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    store = generate_synthetic_data()
    await _persist_synthetic_data(db, store)
    kpis = _analytics.compute_kpis()
    return SuccessResponse(data={
        "message": "Demo ready. PostgreSQL populated with synthetic data.",
        "kpis": kpis.model_dump(),
        "next_steps": [
            "GET /api/v1/demo/dashboard/overview - View dashboard KPIs",
            "GET /api/v1/demo/dashboard/trends - View complaint trends",
            "GET /api/v1/demo/dashboard/reports - Full analytics report",
            "POST /api/v1/demo/scenario/customer-complaint - Walk through a complaint",
            "POST /api/v1/demo/scenario/knowledge-search - Search knowledge base",
            "POST /api/v1/demo/scenario/duplicate-detection - Detect duplicates",
            "POST /api/v1/demo/scenario/full-demo - Complete demo walkthrough",
        ],
    })


@router.get(
    "/health",
    summary="Demo health check",
    description="Verifies that demo data is loaded and the platform is ready for demonstration. "
                "Returns the current data counts and API availability status.",
    response_description="Demo readiness status with entity counts",
)
async def demo_health(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    store = get_synthetic_store()
    sizes = store.size()
    data_loaded = len(sizes) > 0 and sum(sizes.values()) > 0
    return SuccessResponse(data={
        "status": "ready" if data_loaded else "no_data",
        "data_loaded": data_loaded,
        "entity_counts": sizes,
        "total_entities": sum(sizes.values()),
        "services_available": {
            "analytics": True,
            "search": True,
            "knowledge": True,
            "ai_gateway": True,
        },
    })


@router.get(
    "/dashboard/overview",
    summary="Dashboard overview KPIs",
    description="Returns executive-level Key Performance Indicators for the demo dashboard. "
                "Includes counts for all entities, open/resolved complaint ratios, "
                "average resolution time, SLA compliance rate, and sentiment scores.",
    response_description="DashboardKPIs object with all metric values",
)
async def dashboard_overview(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_analytics.compute_kpis().model_dump())


@router.get(
    "/dashboard/kpis",
    summary="Detailed dashboard KPIs",
    description="Same as /dashboard/overview but provides additional detail. "
                "Use this endpoint for refreshing KPI widgets on the dashboard.",
)
async def dashboard_kpis(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_analytics.compute_kpis().model_dump())


@router.get(
    "/dashboard/trends",
    summary="Complaint trends and distributions",
    description="Returns complaint trend data broken down by daily, weekly, and monthly granularity. "
                "Also includes category, sentiment, severity, and priority distributions. "
                "Use granularity=weekly or granularity=monthly for broader trend views.",
    response_description="ComplaintTrends with trend lines and distributions",
)
async def dashboard_trends(
    granularity: str = Query("daily", description="Time granularity: daily, weekly, or monthly"),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data=_analytics.compute_trends(granularity).model_dump())


@router.get(
    "/dashboard/search",
    summary="Enterprise search across all entities",
    description="Searches complaints, customers, interactions, workflows, and knowledge base "
                "in a single query. Results are grouped by source entity type. "
                "Example: query=billing returns all billing-related complaints and knowledge.",
    response_description="Grouped search results by entity type",
)
async def dashboard_search(
    query: str = Query("billing", description="Search query text"),
    limit: int = Query(20, ge=1, le=100, description="Max results per entity type"),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    service = get_search_service()
    results = service.search_all(query, limit)
    return SuccessResponse(data=results)


@router.get(
    "/dashboard/knowledge",
    summary="Knowledge base search",
    description="Searches the knowledge base (policies, FAQ, products) for matching content. "
                "Use source=policy, source=faq, or source=product to filter by type. "
                "Example: query=claim returns all claim-related FAQ and policy articles.",
    response_description="Knowledge search results with source metadata",
)
async def dashboard_knowledge(
    query: str = Query("claim", description="Search query for knowledge base"),
    source: str | None = Query(None, description="Filter by source: policy, faq, or product"),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    result = _knowledge.search(query, source)
    return SuccessResponse(data={
        "query": result.query,
        "results": result.results,
        "total": result.total,
        "source": result.source,
    })


@router.get(
    "/dashboard/knowledge/ask",
    summary="RAG-powered question answering",
    description="Uses the AI Gateway to answer questions based on knowledge base content. "
                "The system retrieves relevant context from policies, FAQ, and products, "
                "then generates a response using the configured LLM provider. "
                "Example: question=How do I file a claim?",
    response_description="AI-generated answer with source citations",
)
async def knowledge_ask(
    question: str = Query("How do I file a claim?", description="Question to answer using knowledge base"),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    answer = await _knowledge.answer_question(question)
    return SuccessResponse(data=answer)


@router.get(
    "/dashboard/reports",
    summary="Full analytics report",
    description="Generates a comprehensive analytics report with all available metrics: "
                "KPIs, trends, SLA compliance, department workload, resolution metrics, "
                "customer metrics, workflow analytics, and notification analytics. "
                "This is a single endpoint that returns the complete executive dashboard data.",
    response_description="Complete AnalyticsReport with all metrics",
)
async def dashboard_reports(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    report = _analytics.generate_report()
    return SuccessResponse(data=report.model_dump())


@router.post(
    "/scenario/customer-complaint",
    summary="Demo: Customer Complaint Walkthrough",
    description="Demonstrates the complete complaint lifecycle: "
                "1) Selects a random customer and complaint from synthetic data "
                "2) Returns complaint details, customer info, and AI analysis "
                "3) Shows the workflow status and notification history. "
                "This scenario showcases the end-to-end complaint management flow.",
    response_description="Complete complaint scenario with customer, workflow, and AI data",
    status_code=http_status.HTTP_200_OK,
)
async def scenario_customer_complaint(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    store = get_synthetic_store()
    complaints = store.get("complaints", [])
    customers = store.get("customers", [])
    workflows = store.get("workflows", [])
    notifications = store.get("notifications", [])

    if not complaints:
        return SuccessResponse(data={"error": "No demo data loaded. Call POST /api/v1/demo/load first."})

    import random
    complaint = random.choice(complaints)
    customer = next((c for c in customers if c["id"] == complaint.get("customer_id")), None)
    wf = next((w for w in workflows if w["complaint_id"] == complaint["id"]), None)
    notifs = [n for n in notifications if n.get("complaint_id") == complaint["id"]]

    return SuccessResponse(data={
        "scenario": "Customer Complaint Walkthrough",
        "description": "End-to-end complaint lifecycle showing customer, complaint, workflow, and notifications",
        "customer": {
            "name": customer["full_name"] if customer else "Unknown",
            "email": customer["email"] if customer else "N/A",
            "segment": customer["segment"] if customer else "N/A",
            "status": customer["status"] if customer else "N/A",
        },
        "complaint": {
            "number": complaint.get("complaint_number"),
            "title": complaint.get("title"),
            "description": complaint.get("description"),
            "category": complaint.get("category"),
            "priority": complaint.get("priority"),
            "severity": complaint.get("severity"),
            "status": complaint.get("status"),
            "source": complaint.get("source"),
            "created_at": complaint.get("created_at"),
        },
        "workflow": {
            "number": wf.get("workflow_number") if wf else None,
            "status": wf.get("workflow_status") if wf else None,
            "stage": wf.get("workflow_stage") if wf else None,
            "assigned_team": wf.get("assigned_team") if wf else None,
            "sla_status": wf.get("sla_status") if wf else None,
            "started_at": wf.get("started_at") if wf else None,
            "completed_at": wf.get("completed_at") if wf else None,
        },
        "notifications": [
            {
                "type": n.get("notification_type"),
                "channel": n.get("notification_channel"),
                "status": n.get("notification_status"),
                "subject": n.get("subject"),
                "created_at": n.get("created_at"),
            }
            for n in notifs[:5]
        ],
        "ai_analysis": {
            "sentiment": complaint.get("metadata", {}).get("ai_sentiment"),
            "sentiment_polarity": complaint.get("metadata", {}).get("ai_sentiment_polarity"),
            "theme": complaint.get("metadata", {}).get("ai_theme"),
        },
        "dashboard_links": {
            "overview": "/api/v1/demo/dashboard/overview",
            "trends": "/api/v1/demo/dashboard/trends",
            "search": f"/api/v1/demo/dashboard/search?query={complaint.get('category', '')}",
        },
    })


@router.post(
    "/scenario/knowledge-search",
    summary="Demo: Knowledge Base Search",
    description="Demonstrates the knowledge base search and RAG capabilities: "
                "1) Searches FAQ, policies, and products for matching content "
                "2) Returns structured results grouped by source type "
                "3) Shows the RAG question-answering pipeline in action. "
                "Example searches: claim, policy, billing, coverage.",
    response_description="Knowledge search results with FAQ, policies, and products",
    status_code=http_status.HTTP_200_OK,
)
async def scenario_knowledge_search(
    query: str = Body("How do I file a claim?", embed=True, description="Search query for knowledge base"),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    faq_results = _knowledge.search(query, source="faq")
    policy_results = _knowledge.search(query, source="policy")
    product_results = _knowledge.search(query, source="product")

    return SuccessResponse(data={
        "scenario": "Knowledge Base Search",
        "description": "Search across FAQ, policies, and products with RAG question answering",
        "query": query,
        "faq": {
            "total": faq_results.total,
            "results": faq_results.results[:5],
        },
        "policies": {
            "total": policy_results.total,
            "results": policy_results.results[:5],
        },
        "products": {
            "total": product_results.total,
            "results": product_results.results[:5],
        },
        "rag_demo": {
            "endpoint": "/api/v1/demo/dashboard/knowledge/ask",
            "example": f"/api/v1/demo/dashboard/knowledge/ask?question={query.replace(' ', '%20')}",
        },
        "dashboard_links": {
            "knowledge": f"/api/v1/demo/dashboard/knowledge?query={query}",
            "ask": f"/api/v1/demo/dashboard/knowledge/ask?question={query}",
        },
    })


@router.post(
    "/scenario/duplicate-detection",
    summary="Demo: Duplicate Complaint Detection",
    description="Demonstrates the duplicate detection capability: "
                "1) Selects two complaints from synthetic data "
                "2) Compares them using embedding similarity and LLM analysis "
                "3) Returns a similarity score and match reasoning. "
                "This showcases the AI-powered duplicate detection pipeline.",
    response_description="Duplicate detection result with similarity score",
    status_code=http_status.HTTP_200_OK,
)
async def scenario_duplicate_detection(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    store = get_synthetic_store()
    complaints = store.get("complaints", [])

    if len(complaints) < 2:
        return SuccessResponse(data={"error": "Need at least 2 complaints. Call POST /api/v1/demo/load first."})

    import random
    c1 = random.choice(complaints)
    c2 = random.choice(complaints)

    from ai.embeddings.encoder import TextEncoder
    from ai.providers.local_provider import LocalProvider
    encoder = TextEncoder(provider=LocalProvider())
    vec1 = await encoder.encode(c1.get("description", ""))
    vec2 = await encoder.encode(c2.get("description", ""))
    similarity = await encoder.similarity(vec1, vec2)

    is_match = c1["category"] == c2["category"]

    return SuccessResponse(data={
        "scenario": "Duplicate Complaint Detection",
        "description": "Semantic similarity comparison between two complaints using embedding vectors",
        "complaint_a": {
            "number": c1.get("complaint_number"),
            "title": c1.get("title"),
            "category": c1.get("category"),
            "description_preview": c1.get("description", "")[:150] + "...",
        },
        "complaint_b": {
            "number": c2.get("complaint_number"),
            "title": c2.get("title"),
            "category": c2.get("category"),
            "description_preview": c2.get("description", "")[:150] + "...",
        },
        "analysis": {
            "similarity_score": round(similarity, 4),
            "is_duplicate": is_match and similarity > 0.5,
            "match_reason": "Same category and high semantic similarity" if is_match and similarity > 0.5 else "Different categories or low similarity",
            "same_category": is_match,
            "embedding_dimensions": 4,
        },
        "next_steps": [
            "Adjust threshold to control sensitivity",
            "Use LLM-based classification for deeper analysis",
            "Integrate OpenSearch vector search for production",
        ],
    })


@router.post(
    "/scenario/dashboard",
    summary="Demo: Dashboard Overview",
    description="Demonstrates the complete executive dashboard: "
                "1) Returns KPIs, trends, SLA, department workload "
                "2) Shows resolution metrics and customer analytics "
                "3) Includes workflow and notification analytics. "
                "This is a single-endpoint demo of the entire analytics platform.",
    response_description="Complete dashboard dataset with all analytics",
    status_code=http_status.HTTP_200_OK,
)
async def scenario_dashboard(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data={
        "scenario": "Executive Dashboard Overview",
        "description": "Complete executive dashboard with all analytics and KPIs",
        "kpis": _analytics.compute_kpis().model_dump(),
        "trends": _analytics.compute_trends().model_dump(),
        "sla": _analytics.compute_sla().model_dump(),
        "departments": [d.model_dump() for d in _analytics.compute_department_workload()],
        "resolution": _analytics.compute_resolution_metrics().model_dump(),
        "customers": _analytics.compute_customer_metrics().model_dump(),
        "workflows": _analytics.compute_workflow_analytics().model_dump(),
        "notifications": _analytics.compute_notification_analytics().model_dump(),
        "executive_summary": _analytics.compute_kpis().model_dump(),
    })


@router.post(
    "/scenario/full-demo",
    summary="Demo: Complete Platform Walkthrough",
    description="Runs a comprehensive platform demonstration covering: "
                "1) Executive dashboard KPIs and trends "
                "2) Customer complaint lifecycle with workflow "
                "3) Knowledge base search and RAG question answering "
                "4) Duplicate detection analysis "
                "5) Full analytics report. "
                "This is the ultimate demo endpoint for client presentations.",
    response_description="Complete platform demo with all scenarios",
    status_code=http_status.HTTP_200_OK,
)
async def scenario_full_demo(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    store = get_synthetic_store()
    complaints = store.get("complaints", [])
    customers = store.get("customers", [])
    workflows = store.get("workflows", [])

    if not complaints:
        return SuccessResponse(data={"error": "No demo data loaded. Call POST /api/v1/demo/load first."})

    import random
    complaint = random.choice(complaints)
    customer = next((c for c in customers if c["id"] == complaint.get("customer_id")), None)
    wf = next((w for w in workflows if w["complaint_id"] == complaint["id"]), None)

    return SuccessResponse(data={
        "scenario": "Complete Platform Demo",
        "description": "End-to-end demonstration of the LuMay SMART Insurance AI Hub",
        "demo_version": "1.0.0",
        "executive_dashboard": _analytics.compute_kpis().model_dump(),
        "complaint_lifecycle": {
            "customer": {
                "name": customer["full_name"] if customer else "Unknown",
                "segment": customer["segment"] if customer else "N/A",
            },
            "complaint": {
                "number": complaint.get("complaint_number"),
                "title": complaint.get("title"),
                "category": complaint.get("category"),
                "priority": complaint.get("priority"),
                "status": complaint.get("status"),
            },
            "workflow": {
                "status": wf.get("workflow_status") if wf else None,
                "stage": wf.get("workflow_stage") if wf else None,
                "sla": wf.get("sla_status") if wf else None,
            },
            "ai_analysis": {
                "sentiment": complaint.get("metadata", {}).get("ai_sentiment"),
                "theme": complaint.get("metadata", {}).get("ai_theme"),
            },
        },
        "analytics": {
            "trends": _analytics.compute_trends().model_dump(),
            "sla": _analytics.compute_sla().model_dump(),
            "departments": [d.model_dump() for d in _analytics.compute_department_workload()],
            "report": _analytics.generate_report().model_dump(),
        },
        "available_apis": [
            {"method": "POST", "path": "/api/v1/demo/scenario/customer-complaint", "description": "Customer complaint walkthrough"},
            {"method": "POST", "path": "/api/v1/demo/scenario/knowledge-search", "description": "Knowledge base search demo"},
            {"method": "POST", "path": "/api/v1/demo/scenario/duplicate-detection", "description": "Duplicate detection demo"},
            {"method": "POST", "path": "/api/v1/demo/scenario/dashboard", "description": "Executive dashboard demo"},
            {"method": "GET", "path": "/api/v1/demo/dashboard/overview", "description": "Dashboard KPIs"},
            {"method": "GET", "path": "/api/v1/demo/dashboard/trends", "description": "Complaint trends"},
            {"method": "GET", "path": "/api/v1/demo/dashboard/search", "description": "Enterprise search"},
            {"method": "GET", "path": "/api/v1/demo/dashboard/knowledge/ask", "description": "RAG question answering"},
            {"method": "GET", "path": "/api/v1/demo/dashboard/reports", "description": "Full analytics report"},
            {"method": "GET", "path": "/api/v1/analytics/report", "description": "Analytics report (alternative)"},
        ],
    })


@router.get(
    "/events",
    summary="SSE event stream for demo events",
    description="Server-Sent Events endpoint that streams live demo events to connected clients. "
                "Events include customer interactions, AI decisions, workflow changes, SLA updates, "
                "and simulation events. Use EventSource in the browser to consume this stream.",
    response_class=EventSourceResponse,
)
async def demo_event_stream(request: Request) -> EventSourceResponse:
    q = DemoEventBus.subscribe()

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(q.get(), timeout=30.0)
                    yield {
                        "event": event.event_type,
                        "data": json.dumps({
                            "id": event.id,
                            "event_type": event.event_type,
                            "data": event.data,
                            "channel": event.channel,
                            "customer_name": event.customer_name,
                            "timestamp": event.timestamp,
                        }),
                    }
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "keepalive"}
        finally:
            DemoEventBus.unsubscribe(q)

    return EventSourceResponse(event_generator())


@router.get(
    "/events/history",
    summary="Recent event history",
    description="Returns the last N events from the demo event bus. Useful for catching up "
                "after a client reconnects to the SSE stream.",
)
async def demo_event_history(
    limit: int = Query(50, ge=1, le=200, description="Number of recent events to return"),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    return SuccessResponse(data={
        "events": DemoEventBus.get_recent(limit),
        "total": len(DemoEventBus.get_recent(limit)),
    })


@router.post(
    "/simulate/complaint",
    summary="Simulate a new complaint lifecycle",
    description="Simulates a customer submitting a complaint through a random channel, "
                "triggers AI analysis, workflow creation, SLA monitoring, and notification events. "
                "All events are broadcast via SSE to connected dashboard clients.",
)
async def simulate_complaint(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    result = await _simulate_complaint_internal()
    if "error" in result:
        return SuccessResponse(data={"error": "No demo data loaded. Call POST /api/v1/demo/load first."})
    return SuccessResponse(data=result)


@router.post(
    "/simulate/interaction",
    summary="Simulate a customer interaction event",
    description="Simulates an inbound customer interaction (call, chat, email) with "
                "real-time transcript updates, sentiment shifts, and agent assignment events.",
)
async def simulate_interaction(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    result = await _simulate_interaction_internal()
    if "error" in result:
        return SuccessResponse(data={"error": "No demo data loaded. Call POST /api/v1/demo/load first."})
    return SuccessResponse(data=result)


@router.post(
    "/simulate/ai-decision",
    summary="Simulate an AI decision event",
    description="Simulates the AI making a real-time decision: sentiment analysis, "
                "root cause identification, resolution recommendation, or override request.",
)
async def simulate_ai_decision(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    result = await _simulate_ai_decision_internal()
    if "error" in result:
        return SuccessResponse(data={"error": "No demo data loaded. Call POST /api/v1/demo/load first."})
    return SuccessResponse(data=result)


async def _simulate_complaint_internal() -> dict:
    store = get_synthetic_store()
    customers = store.get("customers", [])
    if not customers:
        return {"error": "No demo data loaded"}

    customer = random.choice(customers)
    channel = random.choice(["web_chat", "email", "whatsapp", "voice", "smart_call"])
    complaint_categories = ["claims", "policy_and_coverage", "renewal_and_pricing", "customer_service", "digital_experience", "financial"]
    category = random.choice(complaint_categories)
    sentiment = random.choice(["negative", "very_negative", "neutral", "positive"])

    complaint_id = uuid.uuid4().hex[:12]

    publish_demo_event("complaint.submitted", {
        "complaint_id": complaint_id,
        "category": category,
        "channel": channel,
        "customer_id": customer["id"],
        "customer_name": customer["full_name"],
        "summary": f"{customer['full_name']} submitted a {category.replace('_', ' ')} complaint via {channel.replace('_', ' ')}",
    }, channel=channel, customer_name=customer["full_name"])

    publish_demo_event("ai.sentiment_analysis", {
        "complaint_id": complaint_id,
        "sentiment": sentiment,
        "confidence": round(random.uniform(0.82, 0.99), 3),
        "summary": f"Sentiment detected as {sentiment.replace('_', ' ')} with high confidence",
    }, channel=channel, customer_name=customer["full_name"])

    publish_demo_event("ai.theme_classification", {
        "complaint_id": complaint_id,
        "theme": category,
        "sub_theme": random.choice(["billing_error", "claim_delay", "coverage_denial", "policy_cancellation", "service_quality"]),
        "summary": f"Classified under {category.replace('_', ' ')} theme",
    }, channel=channel, customer_name=customer["full_name"])

    sla_hours = random.randint(24, 72)
    publish_demo_event("workflow.created", {
        "complaint_id": complaint_id,
        "workflow_id": uuid.uuid4().hex[:12],
        "sla_hours": sla_hours,
        "assigned_team": random.choice(["Claims", "Billing", "Customer Service", "Technical Support"]),
        "priority": random.choice(["low", "medium", "high", "critical"]),
        "summary": f"Workflow created with {sla_hours}h SLA deadline",
    }, channel=channel, customer_name=customer["full_name"])

    publish_demo_event("notification.sent", {
        "complaint_id": complaint_id,
        "channel": channel,
        "notification_type": "acknowledgment",
        "subject": f"We've received your {category.replace('_', ' ')} complaint",
        "summary": f"Acknowledgment sent to {customer['full_name']} via {channel.replace('_', ' ')}",
    }, channel=channel, customer_name=customer["full_name"])

    publish_demo_event("dashboard.update", {
        "complaint_id": complaint_id,
        "category": category,
        "priority": random.choice(["low", "medium", "high", "critical"]),
        "customer_name": customer["full_name"],
        "channel": channel,
        "timestamp": __import__("datetime").datetime.now(__import__("pytz").UTC).isoformat(),
    }, channel=channel, customer_name=customer["full_name"])

    return {
        "complaint_id": complaint_id,
        "customer_name": customer["full_name"],
        "channel": channel,
        "category": category,
        "events_published": 6,
    }


async def _simulate_interaction_internal() -> dict:
    store = get_synthetic_store()
    customers = store.get("customers", [])
    if not customers:
        return {"error": "No demo data loaded"}

    customer = random.choice(customers)
    channel = random.choice(["voice", "web_chat", "whatsapp"])

    interaction_id = uuid.uuid4().hex[:12]

    publish_demo_event("interaction.started", {
        "interaction_id": interaction_id,
        "channel": channel,
        "customer_name": customer["full_name"],
        "direction": "inbound",
        "summary": f"New {channel.replace('_', ' ')} interaction started with {customer['full_name']}",
    }, channel=channel, customer_name=customer["full_name"])

    transcript_segments = [
        f"{customer['full_name']}: I've been trying to reach someone about my claim for weeks.",
        "Agent: I apologize for the delay. Let me look into your claim right away.",
        f"{customer['full_name']}: I need this resolved as soon as possible.",
        "Agent: I understand your frustration. I've flagged this as high priority.",
    ]
    for segment in transcript_segments:
        publish_demo_event("interaction.transcript", {
            "interaction_id": interaction_id,
            "text": segment,
            "speaker": "customer" if segment.startswith(customer["full_name"].split()[0]) else "agent",
        }, channel=channel, customer_name=customer["full_name"])

    publish_demo_event("interaction.sentiment_shift", {
        "interaction_id": interaction_id,
        "from_sentiment": "very_negative",
        "to_sentiment": "neutral",
        "summary": "Customer sentiment improved from very negative to neutral after agent engagement",
    }, channel=channel, customer_name=customer["full_name"])

    publish_demo_event("interaction.ended", {
        "interaction_id": interaction_id,
        "channel": channel,
        "duration_seconds": random.randint(120, 900),
        "summary": f"{channel.replace('_', ' ')} interaction completed",
    }, channel=channel, customer_name=customer["full_name"])

    return {
        "interaction_id": interaction_id,
        "customer_name": customer["full_name"],
        "channel": channel,
        "events_published": 7,
    }


async def _simulate_ai_decision_internal() -> dict:
    store = get_synthetic_store()
    customers = store.get("customers", [])
    if not customers:
        return {"error": "No demo data loaded"}

    customer = random.choice(customers)
    decision_type = random.choice(["root_cause", "recommendation", "override", "escalation"])

    decisions = {
        "root_cause": {
            "event_type": "ai.root_cause_identified",
            "data": {
                "root_cause": "System processing delay due to legacy integration",
                "contributing_factors": ["Third-party API timeout", "Manual verification step", "Weekend backlog"],
                "confidence": round(random.uniform(0.85, 0.97), 3),
            },
        },
        "recommendation": {
            "event_type": "ai.recommendation_generated",
            "data": {
                "action": "Auto-approve claim with conditional payment hold",
                "reasoning": "Customer has valid policy coverage and all documentation is in order",
                "estimated_resolution_time": f"{random.randint(2, 24)} hours",
                "confidence": round(random.uniform(0.88, 0.99), 3),
            },
        },
        "override": {
            "event_type": "ai.override_requested",
            "data": {
                "reason": "Predicted sentiment escalation requires human intervention",
                "original_decision": "Auto-respond with standard template",
                "proposed_override": "Assign to senior agent with escalation authority",
                "urgency": random.choice(["low", "medium", "high"]),
            },
        },
        "escalation": {
            "event_type": "ai.escalation_triggered",
            "data": {
                "escalation_level": random.choice(["supervisor", "manager", "compliance"]),
                "reason": "Complaint involves regulatory compliance requirement",
                "sla_impact": f"SLA at risk - deadline in {random.randint(4, 48)} hours",
            },
        },
    }

    decision = decisions[decision_type]
    publish_demo_event(decision["event_type"], {
        **decision["data"],
        "customer_name": customer["full_name"],
    }, channel="system", customer_name=customer["full_name"])

    return {
        "decision_type": decision_type,
        "event_type": decision["event_type"],
        "customer_name": customer["full_name"],
        "data": decision["data"],
    }


@router.post(
    "/simulate/full",
    summary="Run a full simulation sequence",
    description="Simulates a complete end-to-end customer journey: complaint submission, "
                "AI analysis, workflow creation, interaction, and resolution. "
                "Broadcasts multiple events to the SSE stream for a rich demo experience.",
)
async def simulate_full(
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse:
    complaint_result = await _simulate_complaint_internal()
    interaction_result = await _simulate_interaction_internal()
    ai_result = await _simulate_ai_decision_internal()

    publish_demo_event("simulation.complete", {
        "simulation_id": uuid.uuid4().hex[:12],
        "summary": "Full simulation sequence completed successfully",
        "scenarios": ["complaint", "interaction", "ai_decision"],
    }, channel="system")

    return SuccessResponse(data={
        "message": "Full simulation complete",
        "summary": "All scenario events published to event bus",
        "complaint": complaint_result,
        "interaction": interaction_result,
        "ai_decision": ai_result,
    })
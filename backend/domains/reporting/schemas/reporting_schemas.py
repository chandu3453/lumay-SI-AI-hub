"""Reporting Pydantic schemas — Customer 360 + Enterprise Analytics (Sprint 29)."""

import uuid
from datetime import datetime

from shared.base_schema import AppBaseModel

from domains.complaint.schemas.complaint_schemas import ComplaintSummary
from domains.conversation.schemas.conversation_schemas import (
    ConversationResponse,
    ConversationSummary,
    TimelineItem,
)


class NotAvailableSection(AppBaseModel):
    """A section with no backing domain in this system (Policies, Claims,
    Payments, Renewals, Documents) — an honest placeholder, not fabricated
    data, matching the pattern already established in the Interaction
    Center's Customer 360 panel."""

    available: bool = False
    message: str = "Not available — no backing domain exists in this system for this data."


# ── Customer 360 ─────────────────────────────────────────────────────────


class CustomerInfo(AppBaseModel):
    id: uuid.UUID
    customer_number: str | None = None
    full_name: str
    email: str | None = None
    mobile_number: str | None = None
    segment: str
    status: str


class AssignedEmployee(AppBaseModel):
    id: uuid.UUID
    full_name: str | None = None


class ConversationStatistics(AppBaseModel):
    total_conversations: int
    avg_resolution_seconds: float | None = None
    escalation_count: int


class CustomerOverview(AppBaseModel):
    open_complaints: int
    conversation_count: int
    avg_resolution_seconds: float | None = None
    escalation_count: int
    open_claims: NotAvailableSection = NotAvailableSection()
    pending_renewals: NotAvailableSection = NotAvailableSection()
    upcoming_payments: NotAvailableSection = NotAvailableSection()
    policy_expiry: NotAvailableSection = NotAvailableSection()


class AgentAssistSnapshot(AppBaseModel):
    summary: str | None = None
    sentiment: str | None = None
    intent: str | None = None
    intent_confidence: float | None = None
    generated_at: datetime | None = None


class Customer360Response(AppBaseModel):
    customer: CustomerInfo
    current_conversation: ConversationResponse | None = None
    assigned_employee: AssignedEmployee | None = None
    recent_conversations: list[ConversationSummary] = []
    conversation_statistics: ConversationStatistics
    overview: CustomerOverview
    agent_assist: AgentAssistSnapshot | None = None
    complaints: list[ComplaintSummary] = []
    policies: NotAvailableSection = NotAvailableSection()
    claims: NotAvailableSection = NotAvailableSection()
    payments: NotAvailableSection = NotAvailableSection()
    renewals: NotAvailableSection = NotAvailableSection()
    documents: NotAvailableSection = NotAvailableSection()


class CustomerActivityTimelineResponse(AppBaseModel):
    items: list[TimelineItem]
    total: int
    page: int
    page_size: int


# ── Enterprise Analytics ─────────────────────────────────────────────────


class ConversationAnalyticsSummary(AppBaseModel):
    total_conversations: int
    active_conversations: int
    resolved_conversations: int
    escalated_conversations: int
    ai_handled: int
    human_handled: int
    ai_to_human_handoffs: int
    avg_response_time_seconds: float | None = None
    avg_resolution_time_seconds: float | None = None
    avg_conversation_duration_seconds: float | None = None
    customer_satisfaction: float | None = None  # placeholder — no CSAT capture exists yet


class VoiceVsChat(AppBaseModel):
    voice: int
    chat: int


class ConversationDistributions(AppBaseModel):
    intent_distribution: dict[str, int]
    sentiment_distribution: dict[str, int]
    complaint_distribution: dict[str, int]
    channel_distribution: dict[str, int]
    voice_vs_chat: VoiceVsChat
    policy_category_distribution: NotAvailableSection = NotAvailableSection()


class TrendPoint(AppBaseModel):
    period: str
    count: int


class SentimentTrendPoint(AppBaseModel):
    period: str
    positive: int = 0
    neutral: int = 0
    frustrated: int = 0
    escalated: int = 0


class IntentTrendPoint(AppBaseModel):
    period: str
    counts: dict[str, int] = {}


class AiUtilizationTrendPoint(AppBaseModel):
    period: str
    ai_handled: int = 0
    human_handled: int = 0


class ConversationTrends(AppBaseModel):
    granularity: str
    conversation_trend: list[TrendPoint]
    complaint_trend: list[TrendPoint]
    sentiment_trend: list[SentimentTrendPoint]
    intent_trend: list[IntentTrendPoint]
    ai_utilization_trend: list[AiUtilizationTrendPoint]


class EmployeeAnalyticsItem(AppBaseModel):
    employee_id: uuid.UUID
    employee_name: str | None = None
    assigned_conversations: int
    resolved: int
    escalated: int
    avg_resolution_seconds: float | None = None
    ai_assistance_usage: int
    transfer_count: int


class SupervisorDashboard(AppBaseModel):
    queue_by_status: dict[str, int]
    live_conversations: int
    high_priority_complaints: int
    escalated_cases: int
    ai_active_conversations: int
    employees_online: int



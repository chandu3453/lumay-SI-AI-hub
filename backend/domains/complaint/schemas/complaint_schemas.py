"""Complaint Pydantic schemas — Phase 2 extended.

Phase 2 additions:
- AIOverrideRequest  : FR-014 human override of AI fields
- ComplaintResponse  : Extended with all Phase 2 AI intelligence fields
- ComplaintIngestRequest : FR-001 omnichannel ingestion payload
- ComplaintAnalysisResponse: Full AI analysis result for API consumers
- RelatedComplaintSummary: FR-008 related/repeat complaint summary
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from domains.complaint.constants.complaint_constants import (
    ComplaintCategory,
    ComplaintPriority,
    ComplaintSeverity,
    ComplaintSource,
    ComplaintStatus,
)
from shared.base_schema import AppBaseModel, EntitySchema


class ComplaintCreate(AppBaseModel):
    customer_id: uuid.UUID | None = None
    interaction_id: uuid.UUID | None = None
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: ComplaintCategory
    subcategory: str | None = None
    priority: ComplaintPriority = ComplaintPriority.MEDIUM
    severity: ComplaintSeverity = ComplaintSeverity.MEDIUM
    source: ComplaintSource = ComplaintSource.WEB_FORM
    # FR-001 — Extended fields
    policy_id: str | None = Field(default=None, description="Related policy ID")
    policy_number: str | None = Field(default=None, description="Related policy number")
    claim_id: str | None = Field(default=None, description="Related claim ID")
    claim_number: str | None = Field(default=None, description="Related claim number")
    product: str | None = Field(default=None, description="Insurance product type (motor, medical, etc.)")
    channel: str | None = Field(default=None, description="Interaction channel (voice, whatsapp, etc.)")
    customer_requested_outcome: str | None = Field(default=None, description="FR-010: What the customer expects")
    detected_language: str | None = Field(default="en", description="Detected language: ar, en, mixed")
    interaction_ids: list[str] | None = Field(default=None, description="FR-001: List of source interaction IDs")


class ComplaintUpdate(AppBaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category: ComplaintCategory | None = None
    subcategory: str | None = None
    priority: ComplaintPriority | None = None
    severity: ComplaintSeverity | None = None
    status: ComplaintStatus | None = None
    assigned_queue: str | None = None
    assigned_agent_id: uuid.UUID | None = None
    resolution_summary: str | None = None
    closure_reason: str | None = None
    # FR-001 / FR-009 extended fields
    policy_id: str | None = None
    policy_number: str | None = None
    claim_id: str | None = None
    claim_number: str | None = None
    product: str | None = None
    channel: str | None = None
    customer_requested_outcome: str | None = None
    regulatory_flag: bool | None = None


class ComplaintAssignRequest(AppBaseModel):
    agent_id: uuid.UUID
    queue: str | None = None


# ---------------------------------------------------------------------------
# FR-001 — Omnichannel Ingestion Request
# ---------------------------------------------------------------------------
class ComplaintIngestRequest(AppBaseModel):
    """FR-001: Structured payload for automated omnichannel ingestion.

    Used by SMART CALL, WhatsApp gateway, email parser, and CRM webhooks.
    """
    interaction_id: str | None = Field(default=None, description="Source interaction ID")
    channel: str = Field(description="Channel: voice, whatsapp, web_chat, email, smart_call, crm")
    customer_id: uuid.UUID | None = Field(default=None, description="Customer UUID if known")
    policy_number: str | None = Field(default=None, description="Policy number from interaction")
    claim_number: str | None = Field(default=None, description="Claim number from interaction")
    product: str | None = Field(default=None, description="Insurance product type")
    agent_id: str | None = Field(default=None, description="Agent or AI-agent identifier")
    transcript: str | None = Field(default=None, description="Full conversation transcript or email body")
    email_body: str | None = Field(default=None, description="Email body (alternative to transcript)")
    language: str | None = Field(default="en", description="Detected or declared language: ar, en, mixed")
    interaction_datetime: str | None = Field(default=None, description="ISO timestamp of the interaction")
    crm_case_ref: str | None = Field(default=None, description="Existing CRM case reference")
    attachments_metadata: list[dict] | None = Field(default=None, description="Attachment metadata list")
    source_metadata: dict | None = Field(default=None, description="Additional source-specific metadata")


# ---------------------------------------------------------------------------
# FR-014 — Human Override Request
# ---------------------------------------------------------------------------
class AIOverrideRequest(AppBaseModel):
    """FR-014: Agent override of AI-generated classification fields.

    All fields are optional — only fields provided will be overridden.
    Original AI values are preserved in ai_override_log.
    """
    category: str | None = Field(default=None, description="Override AI category")
    theme: str | None = Field(default=None, description="Override AI theme (FR-004 taxonomy)")
    severity: str | None = Field(default=None, description="Override AI severity")
    priority: str | None = Field(default=None, description="Override AI priority")
    sentiment: str | None = Field(default=None, description="Override AI sentiment")
    root_cause: str | None = Field(default=None, description="Override AI root cause")
    root_cause_category: str | None = Field(default=None, description="Override root cause category")
    regulatory_flag: bool | None = Field(default=None, description="Override regulatory flag")
    human_validation: str | None = Field(default=None, description="accepted / corrected / rejected")
    override_reason: str = Field(
        min_length=5,
        max_length=500,
        description="Required reason explaining why the AI classification was overridden",
    )


# ---------------------------------------------------------------------------
# FR-008 — Related Complaint Summary
# ---------------------------------------------------------------------------
class RelatedComplaintSummary(AppBaseModel):
    id: uuid.UUID
    complaint_number: str | None = None
    title: str
    theme: str | None = None
    severity: str
    status: str
    created_at: datetime
    days_ago: int | None = None


# ---------------------------------------------------------------------------
# Main Response schemas
# ---------------------------------------------------------------------------
class ComplaintResponse(EntitySchema):
    complaint_number: str | None = None
    customer_id: uuid.UUID | None = None
    interaction_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    category: ComplaintCategory
    subcategory: str | None = None
    priority: ComplaintPriority
    severity: ComplaintSeverity
    status: ComplaintStatus
    source: ComplaintSource
    assigned_queue: str | None = None
    assigned_agent_id: uuid.UUID | None = None
    resolution_summary: str | None = None
    closure_reason: str | None = None

    # FR-001 / FR-009 — Extended identity
    policy_id: str | None = None
    policy_number: str | None = None
    claim_id: str | None = None
    claim_number: str | None = None
    product: str | None = None
    channel: str | None = None
    interaction_ids: list[str] | None = None

    # FR-010 — Customer requested outcome
    customer_requested_outcome: str | None = None

    # FR-020 — Regulatory flag
    regulatory_flag: bool | None = None

    # FR-014 — Human validation
    human_validation: str | None = None

    # FR-007 — SLA deadlines
    acknowledged_time: str | None = None
    acknowledgment_deadline: str | None = None
    resolution_deadline: str | None = None

    # FR-002 — Detection
    complaint_detected: bool | None = None
    detection_type: str | None = None
    detection_confidence: float | None = None
    primary_complaint_statement: str | None = None

    # FR-003 — Sentiment
    sentiment: str | None = None
    sentiment_start: str | None = None
    sentiment_end: str | None = None
    sentiment_trend: str | None = None
    sentiment_target: str | None = None
    sentiment_polarity: float | None = None
    sentiment_intensity: float | None = None
    sentiment_emotions: dict | None = None

    # FR-004 — Theme
    theme: str | None = None
    theme_secondary: list[str] | None = None
    theme_keywords: list[str] | None = None

    # FR-005 — Severity
    severity_score: float | None = None
    auto_escalation_triggers: list[str] | None = None

    # FR-006 — Escalation Risk
    escalation_risk_score: int | None = None
    escalation_risk_level: str | None = None
    escalation_triggers: list[str] | None = None

    # FR-007 — SLA
    sla_risk: str | None = None
    sla_breach_probability: int | None = None
    sla_hours_remaining: float | None = None

    # FR-008 — Repeat
    is_repeat: bool | None = None
    repeat_window_days: int | None = None
    prior_complaint_count: int | None = None
    prior_complaint_ids: list[str] | None = None

    # FR-016 — Root Cause
    root_cause: str | None = None
    root_cause_category: str | None = None
    contributing_factors: list[str] | None = None
    process_failure_point: str | None = None

    # FR-019 — Language
    detected_language: str | None = None
    arabic_percentage: int | None = None

    # FR-020 — Explainability
    ai_summary: str | None = None
    ai_explanation: dict | None = None
    recommendation: str | None = None
    routing_rule: str | None = None
    suggested_response_template: str | None = None

    # FR-014 — Override history
    ai_override_log: list[dict] | None = None


class ComplaintSummary(AppBaseModel):
    id: uuid.UUID
    complaint_number: str | None = None
    title: str
    category: ComplaintCategory
    priority: ComplaintPriority
    severity: ComplaintSeverity
    status: ComplaintStatus
    assigned_queue: str | None = None
    created_at: datetime

    # Phase 2 quick-view fields
    theme: str | None = None
    sentiment: str | None = None
    sentiment_trend: str | None = None
    escalation_risk_score: int | None = None
    sla_risk: str | None = None
    is_repeat: bool | None = None
    detected_language: str | None = None
    detection_type: str | None = None
    # FR-001 channel + product
    channel: str | None = None
    product: str | None = None
    regulatory_flag: bool | None = None


# ---------------------------------------------------------------------------
# Ingest Response
# ---------------------------------------------------------------------------
class ComplaintIngestResponse(AppBaseModel):
    """Response from FR-001 omnichannel ingestion."""
    complaint_id: uuid.UUID
    complaint_number: str | None = None
    action: str  # "created" or "updated"
    ai_analysis_queued: bool = True
    message: str

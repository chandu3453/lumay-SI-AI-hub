"""Complaint ORM model — Phase 2 with full AI intelligence fields.

FR-001: Added policy_id, policy_number, claim_id, claim_number, product, channel,
        interaction_ids (list), customer_requested_outcome
FR-007: Added acknowledged_time, resolution_deadline
FR-010: Added customer_requested_outcome
FR-014: Added human_validation status
FR-020: Added regulatory_flag
"""

import uuid

from sqlalchemy import JSON, Boolean, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domains.complaint.constants.complaint_constants import (
    Channel,
    ComplaintCategory,
    ComplaintPriority,
    ComplaintSeverity,
    ComplaintSource,
    ComplaintStatus,
    HumanValidationStatus,
    ProductType,
)
from shared.base_model import AuditModel


class Complaint(AuditModel):
    __tablename__ = "complaints"

    # ------------------------------------------------------------------
    # Core identity
    # ------------------------------------------------------------------
    complaint_number: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True, index=True
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True, index=True
    )
    interaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("interactions.id"), nullable=True, index=True
    )

    # FR-001 — Multiple source interactions (list of IDs)
    interaction_ids: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    # ------------------------------------------------------------------
    # FR-001 / FR-009 — Policy, Claim, Product, Channel
    # ------------------------------------------------------------------
    policy_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    policy_number: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    claim_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    claim_number: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    # FR-001 — Insurance product type
    product: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)

    # FR-001 — Omnichannel channel (explicit field, separate from source)
    channel: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)

    # ------------------------------------------------------------------
    # Complaint content
    # ------------------------------------------------------------------
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # FR-010 — Customer-stated desired outcome
    customer_requested_outcome: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ------------------------------------------------------------------
    # Classification & routing
    # ------------------------------------------------------------------
    category: Mapped[ComplaintCategory] = mapped_column(
        SAEnum(
            ComplaintCategory,
            name="complaint_category",
            create_constraint=True,
        ),
        nullable=False,
    )
    subcategory: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # FR-004 — Theme (7-bucket LuMay taxonomy, stored as string for flexibility)
    theme: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    theme_secondary: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    theme_keywords: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    # ------------------------------------------------------------------
    # Priority & severity
    # ------------------------------------------------------------------
    priority: Mapped[ComplaintPriority] = mapped_column(
        SAEnum(
            ComplaintPriority,
            name="complaint_priority",
            create_constraint=True,
        ),
        nullable=False,
        default=ComplaintPriority.MEDIUM,
    )
    severity: Mapped[ComplaintSeverity] = mapped_column(
        SAEnum(
            ComplaintSeverity,
            name="complaint_severity",
            create_constraint=True,
        ),
        nullable=False,
        default=ComplaintSeverity.MEDIUM,
    )
    severity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    auto_escalation_triggers: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    # ------------------------------------------------------------------
    # Status & workflow
    # ------------------------------------------------------------------
    status: Mapped[ComplaintStatus] = mapped_column(
        SAEnum(
            ComplaintStatus,
            name="complaint_status",
            create_constraint=True,
        ),
        nullable=False,
        default=ComplaintStatus.SUBMITTED,
        index=True,
    )
    source: Mapped[ComplaintSource] = mapped_column(
        SAEnum(
            ComplaintSource,
            name="complaint_source",
            create_constraint=True,
        ),
        nullable=False,
        default=ComplaintSource.WEB_FORM,
    )
    assigned_queue: Mapped[str | None] = mapped_column(String(255), nullable=True)
    assigned_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    resolution_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    closure_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # FR-020 — Regulatory / compliance flag
    regulatory_flag: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)

    # FR-014 — Human validation outcome (accepted / corrected / rejected / pending)
    human_validation: Mapped[str | None] = mapped_column(String(20), nullable=True, default="pending")

    # ------------------------------------------------------------------
    # FR-007 — SLA Deadlines (actual clock, not just AI prediction)
    # ------------------------------------------------------------------
    acknowledged_time: Mapped[str | None] = mapped_column(String(50), nullable=True)  # ISO timestamp
    resolution_deadline: Mapped[str | None] = mapped_column(String(50), nullable=True)  # ISO timestamp
    acknowledgment_deadline: Mapped[str | None] = mapped_column(String(50), nullable=True)  # ISO timestamp

    # ------------------------------------------------------------------
    # FR-002 — Complaint Detection
    # ------------------------------------------------------------------
    complaint_detected: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    detection_type: Mapped[str | None] = mapped_column(String(20), nullable=True)  # definite/possible/none
    detection_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    primary_complaint_statement: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ------------------------------------------------------------------
    # FR-003 — Sentiment Analysis (enhanced)
    # ------------------------------------------------------------------
    sentiment: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sentiment_start: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sentiment_end: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sentiment_trend: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sentiment_target: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sentiment_polarity: Mapped[float | None] = mapped_column(Float, nullable=True)
    sentiment_intensity: Mapped[float | None] = mapped_column(Float, nullable=True)
    sentiment_emotions: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)

    # ------------------------------------------------------------------
    # FR-006 — Escalation Risk
    # ------------------------------------------------------------------
    escalation_risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    escalation_risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    escalation_triggers: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    # ------------------------------------------------------------------
    # FR-007 — SLA & Priority AI
    # ------------------------------------------------------------------
    sla_risk: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sla_breach_probability: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sla_hours_remaining: Mapped[float | None] = mapped_column(Float, nullable=True)
    priority_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ------------------------------------------------------------------
    # FR-008 — Repeat Complaint Detection
    # ------------------------------------------------------------------
    is_repeat: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    repeat_window_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prior_complaint_ids: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    prior_complaint_count: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)

    # ------------------------------------------------------------------
    # FR-016 — Root Cause Analysis
    # ------------------------------------------------------------------
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contributing_factors: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    process_failure_point: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ------------------------------------------------------------------
    # FR-019 — Language
    # ------------------------------------------------------------------
    detected_language: Mapped[str | None] = mapped_column(String(10), nullable=True, default="en")
    arabic_percentage: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ------------------------------------------------------------------
    # FR-020 — Explainability & Audit
    # ------------------------------------------------------------------
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_explanation: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    routing_rule: Mapped[str | None] = mapped_column(String(100), nullable=True)
    suggested_response_template: Mapped[str | None] = mapped_column(Text, nullable=True)

    # FR-014 — Human Override tracking
    ai_override_log: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    # General metadata / profile
    profile_metadata: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, default=dict
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    customer = relationship("Customer", foreign_keys=[customer_id])
    interaction = relationship("Interaction", foreign_keys=[interaction_id])

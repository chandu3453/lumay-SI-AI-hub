"""AgentAssistInsight ORM model.

One row per regeneration (never overwritten in place) — this is what makes
"sentiment trend over time" / "track intent changes during the conversation"
a cheap `ORDER BY created_at` query instead of needing separate trend
infrastructure. `conversation_id` has no unique constraint: many rows per
conversation are expected and desired.
"""

import uuid

from sqlalchemy import Float, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.database.base import AuditModel


class AgentAssistInsight(AuditModel):
    __tablename__ = "agent_assist_insights"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message_count_at_generation: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    summary: Mapped[str | None] = mapped_column(String, nullable=True)

    intent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    intent_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    sentiment: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sentiment_polarity: Mapped[float | None] = mapped_column(Float, nullable=True)

    escalation_risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    escalation_risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # list[{"action": str, "rationale": str}]
    next_best_actions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # list[{"source": str, "id": str, "title": str, "snippet": str, "score": float}]
    knowledge_articles: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # list[{"type": str, "content": str}]
    suggested_replies: Mapped[list | None] = mapped_column(JSON, nullable=True)
    # {"repeated_questions": [...], "missing_info": [...], "compliance_risks": [...],
    #  "unanswered_questions": [...]}
    insights: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # list[{"type": str, "severity": str, "message": str}] — rule-based, see AgentAssistService
    alerts: Mapped[list | None] = mapped_column(JSON, nullable=True)

    complaint_severity_at_generation: Mapped[str | None] = mapped_column(String(20), nullable=True)

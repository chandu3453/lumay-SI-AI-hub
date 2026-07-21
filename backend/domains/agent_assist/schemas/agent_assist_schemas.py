"""Agent Assist Pydantic schemas."""

import uuid
from datetime import datetime

from shared.base_schema import AppBaseModel, EntitySchema


class NextBestAction(AppBaseModel):
    action: str
    rationale: str = ""


class SuggestedReply(AppBaseModel):
    type: str
    content: str


class KnowledgeArticleSuggestion(AppBaseModel):
    source: str
    id: str
    title: str
    snippet: str
    score: float = 1.0


class ConversationInsights(AppBaseModel):
    repeated_questions: list[str] = []
    missing_info: list[str] = []
    compliance_risks: list[str] = []
    unanswered_questions: list[str] = []


class AgentAssistAlert(AppBaseModel):
    type: str
    severity: str
    message: str


class AgentAssistInsightResponse(EntitySchema):
    conversation_id: uuid.UUID
    message_count_at_generation: int
    summary: str | None = None
    intent: str | None = None
    intent_confidence: float | None = None
    sentiment: str | None = None
    sentiment_polarity: float | None = None
    escalation_risk_score: int | None = None
    escalation_risk_level: str | None = None
    next_best_actions: list[NextBestAction] = []
    knowledge_articles: list[KnowledgeArticleSuggestion] = []
    suggested_replies: list[SuggestedReply] = []
    insights: ConversationInsights = ConversationInsights()
    alerts: list[AgentAssistAlert] = []
    complaint_severity_at_generation: str | None = None
    # Live-computed on every read (see design decision 5) — never persisted.
    duration_minutes: float = 0.0
    minutes_since_last_message: float | None = None
    stalled: bool = False


class AgentAssistEmptyResponse(AppBaseModel):
    """Returned by GET .../agent-assist when no insight has been generated yet."""

    conversation_id: uuid.UUID
    generated: bool = False
    message: str = "Agent Assist insights have not been generated for this conversation yet."


class AgentAssistHistoryItem(AppBaseModel):
    id: uuid.UUID
    created_at: datetime
    sentiment: str | None = None
    sentiment_polarity: float | None = None
    intent: str | None = None
    intent_confidence: float | None = None

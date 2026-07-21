"""Agent Assist domain service.

Split in two halves (design decision 2/4 — reuse, don't duplicate LLM
orchestration; cache via latest-row throttle, no new infra):

- `AgentAssistService` — DI-friendly, read-only (GET latest/history), used by
  the router. Cheap: one repository query + live-computed fields.
- `regenerate_agent_assist_insight()` — the one heavy write path, a plain
  function (not a method) that builds its own repositories/services from
  whatever `AsyncSession` it's given, mirroring
  `conversation_engine.run_complaint_intelligence_async`'s "ad hoc session"
  pattern. Called from BOTH the router's manual-regenerate endpoint (request
  session) and the `on_message` background hook (its own session) — a single
  orchestration path regardless of caller, per "reuse... do not duplicate."
"""

from __future__ import annotations

import asyncio
import time
import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ai.gateway.ai_gateway import get_ai_gateway
from ai.intelligence.pipeline import run_pipeline
from ai.intelligence.service import ComplaintIntelligenceService
from app.platform.logging import get_logger
from domains.agent_assist.constants.agent_assist_constants import (
    KNOWLEDGE_ARTICLE_LIMIT,
    MIN_MESSAGES_SINCE_LAST_REGEN,
    MIN_SECONDS_SINCE_LAST_REGEN,
    STALLED_AFTER_MINUTES,
    AgentAssistAlertSeverity,
    AgentAssistAlertType,
    AgentAssistSentiment,
    TRANSCRIPT_MESSAGE_LIMIT,
)
from domains.agent_assist.models.agent_assist_insight import AgentAssistInsight
from domains.agent_assist.repositories.agent_assist_repository import AgentAssistRepository
from domains.agent_assist.schemas.agent_assist_schemas import (
    AgentAssistHistoryItem,
    AgentAssistInsightResponse,
)
from domains.conversation.models.conversation import Conversation
from shared.base_service import BaseService

logger = get_logger(__name__)

# ai.intelligence.models.SentimentAnalysis.sentiment vocabulary
# -> Phase 5 spec vocabulary (design decision 6).
_SENTIMENT_MAP: dict[str, str] = {
    "very_positive": AgentAssistSentiment.POSITIVE,
    "positive": AgentAssistSentiment.POSITIVE,
    "neutral": AgentAssistSentiment.NEUTRAL,
    "negative": AgentAssistSentiment.FRUSTRATED,
    "very_negative": AgentAssistSentiment.ESCALATED,
}

_SENDER_LABEL = {
    "customer": "Customer",
    "ai": "AI",
    "employee": "Agent",
    "supervisor": "Supervisor",
    "system": "System",
}


class AgentAssistService(BaseService):
    def __init__(self, repository: AgentAssistRepository) -> None:
        self._repository = repository
        self._logger = logger

    async def get_latest(
        self, conversation: Conversation
    ) -> AgentAssistInsightResponse | None:
        insight = await self._repository.get_latest(conversation.id)
        if insight is None:
            return None
        return _to_response(insight, conversation)

    async def get_history(
        self, conversation_id: uuid.UUID, *, limit: int = 20
    ) -> list[AgentAssistHistoryItem]:
        rows = await self._repository.list_history(conversation_id, limit=limit)
        return [
            AgentAssistHistoryItem(
                id=row.id,
                created_at=row.created_at,
                sentiment=row.sentiment,
                sentiment_polarity=row.sentiment_polarity,
                intent=row.intent,
                intent_confidence=row.intent_confidence,
            )
            for row in rows
        ]

    async def should_regenerate(self, conversation_id: uuid.UUID, message_count: int) -> bool:
        latest = await self._repository.get_latest(conversation_id)
        if latest is None:
            return True
        if message_count - latest.message_count_at_generation >= MIN_MESSAGES_SINCE_LAST_REGEN:
            return True
        elapsed = (datetime.now(UTC) - _aware(latest.created_at)).total_seconds()
        return elapsed >= MIN_SECONDS_SINCE_LAST_REGEN


def _clamp_confidence(raw) -> float | None:
    if raw is None:
        return None
    try:
        return max(0.0, min(1.0, float(raw)))
    except (ValueError, TypeError):
        return None


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def _to_response(insight: AgentAssistInsight, conversation: Conversation) -> AgentAssistInsightResponse:
    now = datetime.now(UTC)
    duration_minutes = max(0.0, (now - _aware(conversation.created_at)).total_seconds() / 60)
    minutes_since_last_message = max(0.0, (now - _aware(conversation.updated_at)).total_seconds() / 60)
    from domains.conversation.constants.conversation_constants import TERMINAL_CONVERSATION_STATUSES

    stalled = (
        conversation.current_status not in TERMINAL_CONVERSATION_STATUSES
        and minutes_since_last_message >= STALLED_AFTER_MINUTES
    )
    alerts = list(insight.alerts or [])
    if stalled and not any(a.get("type") == AgentAssistAlertType.CONVERSATION_STALLED for a in alerts):
        alerts.append(
            {
                "type": AgentAssistAlertType.CONVERSATION_STALLED,
                "severity": AgentAssistAlertSeverity.WARNING,
                "message": f"No customer activity for {int(minutes_since_last_message)} minutes.",
            }
        )

    return AgentAssistInsightResponse(
        id=insight.id,
        created_at=insight.created_at,
        updated_at=insight.updated_at,
        conversation_id=insight.conversation_id,
        message_count_at_generation=insight.message_count_at_generation,
        summary=insight.summary,
        intent=insight.intent,
        intent_confidence=insight.intent_confidence,
        sentiment=insight.sentiment,
        sentiment_polarity=insight.sentiment_polarity,
        escalation_risk_score=insight.escalation_risk_score,
        escalation_risk_level=insight.escalation_risk_level,
        next_best_actions=insight.next_best_actions or [],
        knowledge_articles=insight.knowledge_articles or [],
        suggested_replies=insight.suggested_replies or [],
        insights=insight.insights or {},
        alerts=alerts,
        complaint_severity_at_generation=insight.complaint_severity_at_generation,
        duration_minutes=round(duration_minutes, 1),
        minutes_since_last_message=round(minutes_since_last_message, 1),
        stalled=stalled,
    )


def _build_transcript(messages) -> str:
    lines = []
    for m in messages[-TRANSCRIPT_MESSAGE_LIMIT:]:
        label = _SENDER_LABEL.get(str(m.sender_type), str(m.sender_type))
        lines.append(f"{label}: {m.content}")
    return "\n".join(lines) if lines else "(no messages yet)"


def _build_knowledge_snippets(results: list[dict]) -> tuple[str, list[dict]]:
    """Returns (prompt-ready text, structured suggestion list) — the same
    result set backs both the LLM grounding context and the Knowledge Assist
    panel, so suggested replies and displayed articles never disagree."""
    parts: list[str] = []
    suggestions: list[dict] = []
    for r in results[:KNOWLEDGE_ARTICLE_LIMIT]:
        source = r.get("source", "")
        if source == "faq":
            title, snippet = r.get("question", ""), r.get("answer", "")
        elif source == "policy":
            title, snippet = r.get("title", ""), r.get("summary", "")
        elif source == "product":
            title, snippet = r.get("name", ""), r.get("description", "")
        else:
            title, snippet = r.get("title") or r.get("name") or "", str(r)
        parts.append(f"[{source}] {title}: {snippet}")
        suggestions.append(
            {
                "source": source,
                "id": str(r.get("id", "")),
                "title": title,
                "snippet": snippet,
                "score": float(r.get("score", 1.0)),
            }
        )
    text = "\n".join(parts) if parts else "(no relevant knowledge base articles found)"
    return text, suggestions


def _assemble_alerts(
    *,
    sentiment: str,
    previous_sentiment: str | None,
    escalation_risk_score: int,
    missing_info: list[str],
    complaint_severity: str | None,
    previous_complaint_severity: str | None,
) -> list[dict]:
    """Rule-based, deterministic — layered on top of the freshly generated
    fields rather than a second speculative LLM guess (design decision 5)."""
    alerts: list[dict] = []

    worsened = (
        sentiment in (AgentAssistSentiment.FRUSTRATED, AgentAssistSentiment.ESCALATED)
        and previous_sentiment not in (AgentAssistSentiment.FRUSTRATED, AgentAssistSentiment.ESCALATED)
    )
    if worsened:
        alerts.append(
            {
                "type": AgentAssistAlertType.FRUSTRATION_INCREASING,
                "severity": AgentAssistAlertSeverity.WARNING,
                "message": "Customer sentiment has turned negative since the last check.",
            }
        )

    if escalation_risk_score >= 70:
        alerts.append(
            {
                "type": AgentAssistAlertType.ESCALATION_RECOMMENDED,
                "severity": AgentAssistAlertSeverity.CRITICAL,
                "message": f"Escalation risk is high ({escalation_risk_score}/100) — human intervention recommended.",
            }
        )
    elif escalation_risk_score >= 40:
        alerts.append(
            {
                "type": AgentAssistAlertType.URGENT,
                "severity": AgentAssistAlertSeverity.INFO,
                "message": f"Elevated escalation risk ({escalation_risk_score}/100) — monitor closely.",
            }
        )

    if missing_info:
        alerts.append(
            {
                "type": AgentAssistAlertType.DOCUMENTS_MISSING,
                "severity": AgentAssistAlertSeverity.WARNING,
                "message": "Information still required from the customer: " + "; ".join(missing_info[:3]),
            }
        )

    if (
        complaint_severity
        and previous_complaint_severity
        and complaint_severity != previous_complaint_severity
    ):
        alerts.append(
            {
                "type": AgentAssistAlertType.COMPLAINT_SEVERITY_CHANGED,
                "severity": AgentAssistAlertSeverity.WARNING,
                "message": f"Complaint severity changed: {previous_complaint_severity} -> {complaint_severity}.",
            }
        )

    return alerts


async def regenerate_agent_assist_insight(
    session: AsyncSession, conversation_id: uuid.UUID, *, force: bool = False
) -> AgentAssistInsight | None:
    """The one heavy write path (design decision 2/4). Fail-open is the
    CALLER's responsibility (the background hook already wraps every call in
    try/except, matching every other Phase 1-4 hook) — this function itself
    raises normally so the manual `/regenerate` endpoint gets a real error."""
    from domains.agent_assist.repositories.agent_assist_repository import AgentAssistRepository
    from domains.complaint.repositories.complaint_repository import ComplaintRepository
    from domains.conversation.repositories.conversation_repository import ConversationRepository
    from domains.conversation.repositories.event_repository import ConversationEventRepository
    from domains.conversation.services.conversation_service import ConversationService
    from domains.conversation.services.event_service import ConversationEventService
    from domains.conversation.services.message_service import MessageService
    from domains.conversation.repositories.message_repository import ConversationMessageRepository
    from domains.conversation.event_bus import publish_conversation_event
    from knowledge.service import KnowledgeService

    agent_assist_repo = AgentAssistRepository(session=session)
    conversation_service = ConversationService(repository=ConversationRepository(session=session))
    message_service = MessageService(repository=ConversationMessageRepository(session=session))
    event_service = ConversationEventService(repository=ConversationEventRepository(session=session))
    agent_assist_service = AgentAssistService(repository=agent_assist_repo)

    conversation = await conversation_service.get_conversation(conversation_id)

    messages, message_count = await message_service.list_messages(conversation_id, page=1, page_size=200)
    if message_count == 0:
        return None

    if not force and not await agent_assist_service.should_regenerate(conversation_id, message_count):
        return None

    previous = await agent_assist_repo.get_latest(conversation_id)
    transcript = _build_transcript(messages)

    intel = ComplaintIntelligenceService()
    start = time.monotonic()
    summary_result, sentiment_result, escalation_result, resolution_result = await asyncio.gather(
        intel.summarize(transcript),
        intel.analyze_sentiment(transcript),
        intel.assess_escalation_risk(transcript),
        intel.recommend_resolution(transcript),
    )

    latest_customer_message = next(
        (m.content for m in reversed(messages) if str(m.sender_type) == "customer"), transcript
    )
    knowledge_service = KnowledgeService()
    search_result = knowledge_service.search(latest_customer_message)
    knowledge_text, knowledge_articles = _build_knowledge_snippets(search_result.results)

    gateway = get_ai_gateway()
    parsed, _metadata = await run_pipeline(
        gateway,
        "agent_assist/insights/system",
        "agent_assist/insights/user",
        {"knowledge_snippets": knowledge_text, "transcript": transcript},
    )
    parsed = parsed or {}
    insights_raw = parsed.get("insights") or {}

    complaint_severity: str | None = None
    if conversation.complaint_id is not None:
        complaint_repo = ComplaintRepository(session=session)
        complaint = await complaint_repo.get_by_id(conversation.complaint_id)
        if complaint is not None:
            complaint_severity = str(complaint.severity)

    sentiment_label = _SENTIMENT_MAP.get(sentiment_result.sentiment, AgentAssistSentiment.NEUTRAL)
    alerts = _assemble_alerts(
        sentiment=sentiment_label,
        previous_sentiment=previous.sentiment if previous else None,
        escalation_risk_score=escalation_result.escalation_risk_score,
        missing_info=insights_raw.get("missing_info", []),
        complaint_severity=complaint_severity,
        previous_complaint_severity=previous.complaint_severity_at_generation if previous else None,
    )

    next_best_actions = parsed.get("next_best_actions") or []
    if not next_best_actions and resolution_result.recommended_action:
        next_best_actions = [
            {"action": resolution_result.recommended_action, "rationale": resolution_result.explanation}
        ]
    suggested_replies = parsed.get("suggested_replies") or []
    if not suggested_replies and resolution_result.suggested_response_template:
        suggested_replies = [
            {"type": "policy_explanation", "content": resolution_result.suggested_response_template}
        ]

    insight = await agent_assist_repo.create(
        conversation_id=conversation_id,
        message_count_at_generation=message_count,
        summary=summary_result.summary or None,
        intent=parsed.get("intent"),
        intent_confidence=_clamp_confidence(parsed.get("intent_confidence")),
        sentiment=sentiment_label,
        sentiment_polarity=sentiment_result.polarity,
        escalation_risk_score=escalation_result.escalation_risk_score,
        escalation_risk_level=escalation_result.risk_level,
        next_best_actions=next_best_actions,
        knowledge_articles=knowledge_articles,
        suggested_replies=suggested_replies,
        insights={
            "repeated_questions": insights_raw.get("repeated_questions", []),
            "missing_info": insights_raw.get("missing_info", []),
            "compliance_risks": insights_raw.get("compliance_risks", []),
            "unanswered_questions": insights_raw.get("unanswered_questions", []),
        },
        alerts=alerts,
        complaint_severity_at_generation=complaint_severity,
    )

    await event_service.record_event(
        conversation_id,
        "agent_assist_regenerated",
        "agent_assist",
        {"insight_id": str(insight.id), "message_count": message_count},
    )
    await session.commit()

    publish_conversation_event(
        str(conversation_id), "agent_assist_updated", {"insight_id": str(insight.id)}
    )
    logger.info(
        "agent_assist_regenerated",
        conversation_id=str(conversation_id),
        latency_ms=round((time.monotonic() - start) * 1000, 1),
    )
    return insight

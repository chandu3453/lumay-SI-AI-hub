"""Agent Assist Domain Constants."""

from enum import StrEnum
from typing import Final

DOMAIN_NAME: Final[str] = "agent_assist"

# Regeneration throttle (design decision 4 — "cache AI outputs, don't
# regenerate on every message"): a new insight is only generated once at
# least this many messages OR this many seconds have passed since the last
# one, whichever comes first. No insight yet always regenerates.
MIN_MESSAGES_SINCE_LAST_REGEN: Final[int] = 2
MIN_SECONDS_SINCE_LAST_REGEN: Final[int] = 60

# A conversation with no new message for this long (while still open) is
# flagged "stalled" — computed live on read, never persisted.
STALLED_AFTER_MINUTES: Final[int] = 10

# Transcript window fed to the LLM — enough context without unbounded prompt
# growth on long conversations.
TRANSCRIPT_MESSAGE_LIMIT: Final[int] = 20

KNOWLEDGE_ARTICLE_LIMIT: Final[int] = 5


class AgentAssistSentiment(StrEnum):
    """Spec vocabulary — mapped from ai.intelligence.models.SentimentAnalysis.sentiment
    (very_positive/positive/neutral/negative/very_negative); see AgentAssistService."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"
    ESCALATED = "escalated"


class AgentAssistAlertType(StrEnum):
    FRUSTRATION_INCREASING = "frustration_increasing"
    COMPLAINT_SEVERITY_CHANGED = "complaint_severity_changed"
    ESCALATION_RECOMMENDED = "escalation_recommended"
    DOCUMENTS_MISSING = "documents_missing"
    CONVERSATION_STALLED = "conversation_stalled"
    URGENT = "urgent"


class AgentAssistAlertSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

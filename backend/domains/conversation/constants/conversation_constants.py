"""Conversation Domain Constants."""

from enum import StrEnum
from typing import Final

DOMAIN_NAME: Final[str] = "conversation"
EXCHANGE_NAME: Final[str] = "lumay.conversation"

CACHE_PREFIX_CONVERSATION: Final[str] = "conversation"

# ConversationFactory: reuse an active conversation for the same customer if it was
# last touched within this many minutes; otherwise a new conversation is started.
DEFAULT_INACTIVITY_WINDOW_MINUTES: Final[int] = 30


class ConversationStatus(StrEnum):
    NEW = "new"
    ACTIVE = "active"
    WAITING_FOR_CUSTOMER = "waiting_for_customer"
    WAITING_FOR_AGENT = "waiting_for_agent"
    AI_HANDLING = "ai_handling"
    HUMAN_HANDLING = "human_handling"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ConversationChannel(StrEnum):
    WEB_CHAT = "web_chat"
    VOICE = "voice"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    COMPLAINT = "complaint"
    # Future-ready: SMS = "sms"; TEAMS = "teams"; MOBILE_APP = "mobile_app"


class ConversationParticipantType(StrEnum):
    CUSTOMER = "customer"
    AI = "ai"
    EMPLOYEE = "employee"
    SUPERVISOR = "supervisor"
    SYSTEM = "system"


class ConversationMessageType(StrEnum):
    TEXT = "text"
    TRANSCRIPT = "transcript"
    ATTACHMENT = "attachment"
    EVENT = "event"
    SYSTEM_NOTIFICATION = "system_notification"


class ConversationPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


TERMINAL_CONVERSATION_STATUSES: Final[set[ConversationStatus]] = {
    ConversationStatus.RESOLVED,
    ConversationStatus.CLOSED,
}

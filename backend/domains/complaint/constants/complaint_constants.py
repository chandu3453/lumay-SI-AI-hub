"""Complaint Domain Constants — Phase 2.

Theme taxonomy aligned with LuMay Insurance FR-004 specification.
"""

from enum import StrEnum
from typing import Final


DOMAIN_NAME: Final[str] = "complaint"
EXCHANGE_NAME: Final[str] = "lumay.complaint"

CACHE_PREFIX_COMPLAINT: Final[str] = "complaint"


class ComplaintStatus(StrEnum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    INVESTIGATING = "investigating"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ARCHIVED = "archived"


class ComplaintPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplaintSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    # Backward compatibility
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"


class ComplaintTheme(StrEnum):
    """FR-004 — Official LuMay Insurance 7-bucket theme taxonomy."""
    CLAIMS = "claims"
    POLICY_AND_COVERAGE = "policy_and_coverage"
    RENEWAL_AND_PRICING = "renewal_and_pricing"
    CUSTOMER_SERVICE = "customer_service"
    PROVIDER_AND_NETWORK = "provider_and_network"
    DIGITAL_EXPERIENCE = "digital_experience"
    FINANCIAL = "financial"


# Keep ComplaintCategory as an alias for backward compatibility with existing data
class ComplaintCategory(StrEnum):
    BILLING = "billing"
    CLAIMS = "claims"
    POLICY = "policy"
    SERVICE = "service"
    TECHNICAL = "technical"
    GENERAL = "general"


class ComplaintSource(StrEnum):
    PHONE = "phone"
    EMAIL = "email"
    WEB_FORM = "web_form"
    WHATSAPP = "whatsapp"
    WEB_CHAT = "web_chat"
    AGENT_ENTERED = "agent_entered"
    SMART_CALL = "smart_call"
    SOCIAL_MEDIA = "social_media"
    REGULATORY = "regulatory"
    MOBILE_APP = "mobile_app"
    PORTAL = "portal"
    IN_PERSON = "in_person"
    POSTAL_MAIL = "postal_mail"


class ProductType(StrEnum):
    """FR-001 / FR-004 — LuMay Insurance product types."""
    MOTOR = "motor"
    MEDICAL = "medical"
    TRAVEL = "travel"
    HOME = "home"
    LIFE = "life"
    BUSINESS = "business"
    POLICY_SERVICING = "policy_servicing"
    RENEWALS = "renewals"
    CLAIMS = "claims"
    PAYMENTS = "payments"
    PROVIDER_GARAGE = "provider_garage"
    GENERAL = "general"


class Channel(StrEnum):
    """FR-001 — Omnichannel source channel."""
    VOICE = "voice"
    WHATSAPP = "whatsapp"
    WEB_CHAT = "web_chat"
    EMAIL = "email"
    SMART_CALL = "smart_call"
    CRM = "crm"
    AGENT_ENTERED = "agent_entered"
    SURVEY = "survey"
    MOBILE_APP = "mobile_app"


class HumanValidationStatus(StrEnum):
    """FR-014 — Human validation outcome for AI-generated summary."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    CORRECTED = "corrected"
    REJECTED = "rejected"


class SentimentLevel(StrEnum):
    """FR-003 — Sentiment levels."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class SentimentTrend(StrEnum):
    """FR-003 — Sentiment trend within interaction."""
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    VOLATILE = "volatile"


class EscalationRiskLevel(StrEnum):
    """FR-006 — Escalation risk level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SLARiskStatus(StrEnum):
    """FR-007 — SLA risk status."""
    WITHIN_SLA = "within_sla"
    AT_RISK = "at_risk"
    BREACHED = "breached"


class DetectionType(StrEnum):
    """FR-002 — Complaint detection confidence level."""
    DEFINITE = "definite"
    POSSIBLE = "possible"
    NONE = "none"


class RootCauseCategory(StrEnum):
    """FR-016 — Root cause categories."""
    PROCESS_FAILURE = "process_failure"
    SYSTEM_TECHNICAL = "system_technical"
    STAFF_BEHAVIOUR = "staff_behaviour"
    POLICY_GAP = "policy_gap"
    PROVIDER_FAILURE = "provider_failure"
    CUSTOMER_EXPECTATION = "customer_expectation"

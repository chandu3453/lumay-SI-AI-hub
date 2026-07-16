"""Notification Domain Constants."""

from enum import StrEnum
from typing import Final


DOMAIN_NAME: Final[str] = "notification"
EXCHANGE_NAME: Final[str] = "lumay.notification"

CACHE_PREFIX_NOTIFICATION: Final[str] = "notification"

MAX_DELIVERY_ATTEMPTS: Final[int] = 3
RETRY_BACKOFF_SECONDS: Final[list[int]] = [60, 300, 900]


class NotificationType(StrEnum):
    ALERT = "alert"
    REMINDER = "reminder"
    CONFIRMATION = "confirmation"
    STATUS_UPDATE = "status_update"
    ESCALATION = "escalation"
    RESOLUTION = "resolution"
    PROMOTIONAL = "promotional"
    SYSTEM = "system"


class NotificationChannel(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    IN_APP = "in_app"
    PUSH = "push"


class NotificationStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    ARCHIVED = "archived"


class NotificationPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
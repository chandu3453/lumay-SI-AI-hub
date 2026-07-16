"""Notification Pydantic schemas — Notification domain."""

import uuid
from datetime import datetime

from pydantic import Field

from domains.notification.constants.notification_constants import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)
from shared.base_schema import AppBaseModel, EntitySchema


class NotificationCreate(AppBaseModel):
    workflow_id: uuid.UUID | None = None
    complaint_id: uuid.UUID | None = None
    notification_type: NotificationType
    channel: NotificationChannel
    recipient: str = Field(min_length=1, max_length=512)
    subject: str = Field(min_length=1, max_length=255)
    message_body: str = Field(min_length=1)
    priority: NotificationPriority = NotificationPriority.MEDIUM
    scheduled_at: datetime | None = None
    notification_metadata: dict | None = None


class NotificationUpdate(AppBaseModel):
    recipient: str | None = Field(default=None, min_length=1, max_length=512)
    subject: str | None = Field(default=None, min_length=1, max_length=255)
    message_body: str | None = Field(default=None, min_length=1)
    priority: NotificationPriority | None = None
    scheduled_at: datetime | None = None
    notification_metadata: dict | None = None


class NotificationQueueRequest(AppBaseModel):
    scheduled_at: datetime | None = None


class NotificationSendRequest(AppBaseModel):
    provider: str = "default"


class NotificationRetryRequest(AppBaseModel):
    scheduled_at: datetime | None = None


class NotificationDeliverRequest(AppBaseModel):
    delivered_at: datetime | None = None


class NotificationFailRequest(AppBaseModel):
    reason: str = "Unknown error"


class NotificationResponse(EntitySchema):
    notification_number: str | None = None
    workflow_id: uuid.UUID | None = None
    complaint_id: uuid.UUID | None = None
    notification_type: NotificationType
    notification_channel: NotificationChannel
    recipient: str
    subject: str
    message: str
    notification_status: NotificationStatus
    priority: NotificationPriority
    retry_count: int = 0
    scheduled_at: datetime | None = None
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    failure_reason: str | None = None
    notification_metadata: dict | None = None


class NotificationSummary(AppBaseModel):
    id: uuid.UUID
    notification_number: str | None = None
    notification_type: NotificationType
    notification_channel: NotificationChannel
    recipient: str
    subject: str
    notification_status: NotificationStatus
    priority: NotificationPriority
    created_at: datetime
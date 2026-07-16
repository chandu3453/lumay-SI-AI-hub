"""Notification ORM model — Notification domain."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum as SAEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domains.notification.constants.notification_constants import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)
from shared.base_model import AuditModel


class Notification(AuditModel):
    __tablename__ = "notifications"

    notification_number: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True, index=True
    )
    workflow_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=True, index=True
    )
    complaint_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=True, index=True
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        SAEnum(NotificationType, name="notification_type", create_constraint=True),
        nullable=False,
    )
    notification_channel: Mapped[NotificationChannel] = mapped_column(
        SAEnum(NotificationChannel, name="notification_channel", create_constraint=True),
        nullable=False,
    )
    recipient: Mapped[str] = mapped_column(
        String(512), nullable=False
    )
    subject: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    message: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    notification_status: Mapped[NotificationStatus] = mapped_column(
        SAEnum(NotificationStatus, name="notification_status", create_constraint=True),
        nullable=False,
        default=NotificationStatus.PENDING,
        index=True,
    )
    priority: Mapped[NotificationPriority] = mapped_column(
        SAEnum(NotificationPriority, name="notification_priority", create_constraint=True),
        nullable=False,
        default=NotificationPriority.MEDIUM,
    )
    retry_count: Mapped[int] = mapped_column(
        default=0, nullable=False
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failure_reason: Mapped[str | None] = mapped_column(
        String(1024), nullable=True
    )
    notification_metadata: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, default=dict
    )

    workflow = relationship("Workflow", foreign_keys=[workflow_id])
    complaint = relationship("Complaint", foreign_keys=[complaint_id])
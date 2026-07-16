"""Notification domain service — business orchestration layer."""

import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from app.platform.logging import get_logger
from domains.notification.constants.notification_constants import (
    MAX_DELIVERY_ATTEMPTS,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)
from domains.notification.events.notification_events import (
    NotificationArchivedEvent,
    NotificationCreatedEvent,
    NotificationDeliveredEvent,
    NotificationFailedEvent,
    NotificationQueuedEvent,
    NotificationRetriedEvent,
    NotificationSentEvent,
)
from shared.base_event import DomainEvent
from domains.notification.exceptions.notification_exceptions import (
    NotificationNotFoundError,
    NotificationValidationError,
)
from domains.notification.models.notification import Notification
from domains.notification.repositories.notification_repository import NotificationRepository
from domains.notification.schemas.notification_schemas import (
    NotificationCreate,
    NotificationUpdate,
)
from domains.workflow.repositories.workflow_repository import WorkflowRepository
from shared.base_service import BaseService

_ALLOWED_TRANSITIONS: dict[NotificationStatus, set[NotificationStatus]] = {
    NotificationStatus.PENDING: {
        NotificationStatus.QUEUED,
        NotificationStatus.ARCHIVED,
    },
    NotificationStatus.QUEUED: {
        NotificationStatus.SENDING,
        NotificationStatus.FAILED,
        NotificationStatus.ARCHIVED,
    },
    NotificationStatus.SENDING: {
        NotificationStatus.SENT,
        NotificationStatus.FAILED,
        NotificationStatus.ARCHIVED,
    },
    NotificationStatus.SENT: {
        NotificationStatus.DELIVERED,
        NotificationStatus.FAILED,
        NotificationStatus.ARCHIVED,
    },
    NotificationStatus.DELIVERED: {
        NotificationStatus.ARCHIVED,
    },
    NotificationStatus.FAILED: {
        NotificationStatus.RETRYING,
        NotificationStatus.ARCHIVED,
    },
    NotificationStatus.RETRYING: {
        NotificationStatus.QUEUED,
        NotificationStatus.FAILED,
        NotificationStatus.ARCHIVED,
    },
    NotificationStatus.ARCHIVED: set(),
}

_IMMUTABLE_STATUSES = {NotificationStatus.ARCHIVED}

_RETRYABLE_STATUSES = {NotificationStatus.FAILED}


class NotificationService(BaseService):
    def __init__(
        self,
        repository: NotificationRepository,
        workflow_repository: WorkflowRepository,
    ) -> None:
        self._repository = repository
        self._workflow_repository = workflow_repository
        self._logger = get_logger(__name__)

    async def create_notification(
        self, data: NotificationCreate
    ) -> tuple[Notification, list[DomainEvent]]:
        self._logger.info(
            "notification_create_requested",
            notification_type=str(data.notification_type),
            channel=str(data.channel),
        )

        if data.workflow_id:
            workflow = await self._workflow_repository.get_by_id(data.workflow_id)
            if workflow is None:
                raise NotificationValidationError(
                    message="Referenced workflow not found.",
                    context={"workflow_id": str(data.workflow_id)},
                )

        notification = await self._repository.create(
            workflow_id=data.workflow_id,
            complaint_id=data.complaint_id,
            notification_type=data.notification_type,
            notification_channel=data.channel,
            recipient=data.recipient,
            subject=data.subject,
            message=data.message_body,
            notification_status=NotificationStatus.PENDING,
            priority=data.priority,
            scheduled_at=data.scheduled_at,
            notification_metadata=data.notification_metadata,
        )
        events: list[DomainEvent] = [
            NotificationCreatedEvent(
                notification_id=notification.id,
                notification_type=str(notification.notification_type),
                channel=str(notification.notification_channel),
                recipient=notification.recipient,
            )
        ]
        self._logger.info(
            "notification_created",
            notification_id=str(notification.id),
            notification_type=str(notification.notification_type),
        )
        return notification, events

    async def get_notification(self, notification_id: uuid.UUID) -> Notification:
        notification = await self._repository.get_by_id(notification_id)
        if notification is None:
            raise NotificationNotFoundError(
                context={"notification_id": str(notification_id)}
            )
        return notification

    async def list_notifications(
        self,
        *,
        notification_status: NotificationStatus | None = None,
        notification_type: NotificationType | None = None,
        notification_channel: NotificationChannel | None = None,
        priority: NotificationPriority | None = None,
        workflow_id: uuid.UUID | None = None,
        complaint_id: uuid.UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[Notification], int]:
        self._logger.debug(
            "notification_list_requested",
            status=notification_status,
            type=notification_type,
            page=page,
        )
        return await self._repository.list(
            notification_status=notification_status,
            notification_type=notification_type,
            notification_channel=notification_channel,
            priority=priority,
            workflow_id=workflow_id,
            complaint_id=complaint_id,
            page=page,
            page_size=page_size,
        )

    async def update_notification(
        self, notification_id: uuid.UUID, data: NotificationUpdate
    ) -> tuple[Notification, list[DomainEvent]]:
        notification = await self.get_notification(notification_id)
        self._assert_mutable(notification)

        updated = await self._repository.update(
            notification_id, **data.model_dump(exclude_none=True)
        )
        self._logger.info(
            "notification_updated",
            notification_id=str(notification_id),
        )
        return updated, []

    async def queue_notification(
        self, notification_id: uuid.UUID, scheduled_at: datetime | None = None
    ) -> tuple[Notification, list[DomainEvent]]:
        notification = await self.get_notification(notification_id)
        self._assert_mutable(notification)
        self._validate_transition(
            notification.notification_status, NotificationStatus.QUEUED
        )

        updated = await self._repository.update(
            notification_id,
            notification_status=NotificationStatus.QUEUED,
            scheduled_at=scheduled_at,
        )
        events: list[DomainEvent] = [
            NotificationQueuedEvent(
                notification_id=notification.id,
                channel=str(notification.notification_channel),
                scheduled_at=scheduled_at.isoformat() if scheduled_at else "",
            )
        ]
        self._logger.info(
            "notification_queued",
            notification_id=str(notification_id),
        )
        return updated, events

    async def send_notification(
        self, notification_id: uuid.UUID, provider: str = "default"
    ) -> tuple[Notification, list[DomainEvent]]:
        notification = await self.get_notification(notification_id)
        self._assert_mutable(notification)
        self._validate_transition(
            notification.notification_status, NotificationStatus.SENDING
        )

        sending = await self._repository.update(
            notification_id,
            notification_status=NotificationStatus.SENDING,
        )

        sent = await self._repository.update(
            notification_id,
            notification_status=NotificationStatus.SENT,
            sent_at=datetime.now(timezone.utc),
        )
        events: list[DomainEvent] = [
            NotificationSentEvent(
                notification_id=notification.id,
                channel=str(notification.notification_channel),
                provider=provider,
            )
        ]
        self._logger.info(
            "notification_sent",
            notification_id=str(notification_id),
            provider=provider,
        )
        return sent, events

    async def retry_notification(
        self, notification_id: uuid.UUID, scheduled_at: datetime | None = None
    ) -> tuple[Notification, list[DomainEvent]]:
        notification = await self.get_notification(notification_id)

        if notification.notification_status not in _RETRYABLE_STATUSES:
            raise NotificationValidationError(
                message="Only failed notifications can be retried.",
                context={
                    "notification_id": str(notification_id),
                    "current_status": str(notification.notification_status),
                },
            )

        if notification.retry_count >= MAX_DELIVERY_ATTEMPTS:
            raise NotificationValidationError(
                message=f"Max retry attempts ({MAX_DELIVERY_ATTEMPTS}) reached.",
                context={
                    "notification_id": str(notification_id),
                    "retry_count": notification.retry_count,
                    "max_attempts": MAX_DELIVERY_ATTEMPTS,
                },
            )

        self._assert_mutable(notification)
        self._validate_transition(
            notification.notification_status, NotificationStatus.RETRYING
        )

        new_retry_count = notification.retry_count + 1
        updated = await self._repository.update(
            notification_id,
            notification_status=NotificationStatus.RETRYING,
            retry_count=new_retry_count,
            scheduled_at=scheduled_at,
        )
        events: list[DomainEvent] = [
            NotificationRetriedEvent(
                notification_id=notification.id,
                attempt=new_retry_count,
                next_retry_at=scheduled_at.isoformat() if scheduled_at else "",
            )
        ]
        self._logger.info(
            "notification_retry_scheduled",
            notification_id=str(notification_id),
            attempt=new_retry_count,
            max_attempts=MAX_DELIVERY_ATTEMPTS,
        )
        return updated, events

    async def mark_delivered(
        self, notification_id: uuid.UUID, delivered_at: datetime | None = None
    ) -> tuple[Notification, list[DomainEvent]]:
        notification = await self.get_notification(notification_id)
        self._assert_mutable(notification)
        self._validate_transition(
            notification.notification_status, NotificationStatus.DELIVERED
        )

        now = delivered_at or datetime.now(timezone.utc)
        updated = await self._repository.update(
            notification_id,
            notification_status=NotificationStatus.DELIVERED,
            delivered_at=now,
        )
        events: list[DomainEvent] = [
            NotificationDeliveredEvent(
                notification_id=notification.id,
                channel=str(notification.notification_channel),
                delivered_at=now.isoformat(),
            )
        ]
        self._logger.info(
            "notification_delivered",
            notification_id=str(notification_id),
        )
        return updated, events

    async def mark_failed(
        self, notification_id: uuid.UUID, reason: str = "Unknown error"
    ) -> tuple[Notification, list[DomainEvent]]:
        notification = await self.get_notification(notification_id)
        self._assert_mutable(notification)
        self._validate_transition(
            notification.notification_status, NotificationStatus.FAILED
        )

        updated = await self._repository.update(
            notification_id,
            notification_status=NotificationStatus.FAILED,
            failure_reason=reason,
        )
        events: list[DomainEvent] = [
            NotificationFailedEvent(
                notification_id=notification.id,
                channel=str(notification.notification_channel),
                error=reason,
                retry_count=notification.retry_count,
            )
        ]
        self._logger.info(
            "notification_failed",
            notification_id=str(notification_id),
            reason=reason,
        )
        return updated, events

    async def archive_notification(
        self, notification_id: uuid.UUID
    ) -> tuple[Notification, list[DomainEvent]]:
        notification = await self.get_notification(notification_id)

        if notification.notification_status == NotificationStatus.ARCHIVED:
            raise NotificationValidationError(
                message="Notification is already archived.",
                context={"notification_id": str(notification_id)},
            )

        self._validate_transition(
            notification.notification_status, NotificationStatus.ARCHIVED
        )

        updated = await self._repository.update(
            notification_id,
            notification_status=NotificationStatus.ARCHIVED,
        )
        events: list[DomainEvent] = [
            NotificationArchivedEvent(
                notification_id=notification.id,
                reason="Manually archived",
            )
        ]
        self._logger.info(
            "notification_archived",
            notification_id=str(notification_id),
        )
        return updated, events

    def _assert_mutable(self, notification: Notification) -> None:
        if notification.notification_status in _IMMUTABLE_STATUSES:
            raise NotificationValidationError(
                message=f"Cannot modify notification in status '{notification.notification_status}'.",
                context={
                    "notification_id": str(notification.id),
                    "current_status": str(notification.notification_status),
                },
            )

    @staticmethod
    def _validate_transition(
        current: NotificationStatus, target: NotificationStatus
    ) -> None:
        allowed = _ALLOWED_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise NotificationValidationError(
                message=f"Cannot transition from '{current}' to '{target}'.",
                context={
                    "current_status": current,
                    "target_status": target,
                },
            )
"""Notification service unit tests."""

import uuid

import pytest

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
from domains.notification.exceptions.notification_exceptions import (
    NotificationNotFoundError,
    NotificationValidationError,
)
from domains.notification.schemas.notification_schemas import (
    NotificationCreate,
    NotificationUpdate,
)
from domains.notification.services.notification_service import NotificationService


@pytest.fixture
def pending_notification_kwargs() -> dict:
    return dict(
        id=uuid.uuid4(),
        workflow_id=uuid.uuid4(),
        complaint_id=None,
        notification_type=NotificationType.ALERT,
        notification_channel=NotificationChannel.EMAIL,
        recipient="test@example.com",
        subject="Test notification",
        message="Test message body.",
        notification_status=NotificationStatus.PENDING,
        priority=NotificationPriority.MEDIUM,
        retry_count=0,
        scheduled_at=None,
        sent_at=None,
        delivered_at=None,
        failure_reason=None,
        metadata=None,
    )


@pytest.fixture
def delivered_notification_kwargs(pending_notification_kwargs: dict) -> dict:
    kwargs = dict(pending_notification_kwargs)
    kwargs["notification_status"] = NotificationStatus.DELIVERED
    return kwargs


@pytest.fixture
def failed_notification_kwargs(pending_notification_kwargs: dict) -> dict:
    kwargs = dict(pending_notification_kwargs)
    kwargs["notification_status"] = NotificationStatus.FAILED
    kwargs["failure_reason"] = "Connection timeout"
    return kwargs


@pytest.fixture
def archived_notification_kwargs(pending_notification_kwargs: dict) -> dict:
    kwargs = dict(pending_notification_kwargs)
    kwargs["notification_status"] = NotificationStatus.ARCHIVED
    return kwargs


@pytest.fixture
async def service(mocker, pending_notification_kwargs: dict) -> NotificationService:
    mock_repo = mocker.AsyncMock()
    mock_workflow_repo = mocker.AsyncMock()

    mock_repo.get_by_id.return_value = mocker.Mock(**pending_notification_kwargs)
    mock_repo.create.return_value = mocker.Mock(**pending_notification_kwargs)
    mock_repo.update.return_value = mocker.Mock(**pending_notification_kwargs)
    mock_workflow_repo.get_by_id.return_value = object()

    return NotificationService(
        repository=mock_repo,
        workflow_repository=mock_workflow_repo,
    )


@pytest.mark.asyncio
class TestNotificationService:
    async def test_create_notification_returns_entity_and_event(
        self,
        service: NotificationService,
    ) -> None:
        data = NotificationCreate(
            notification_type=NotificationType.ALERT,
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            subject="Test",
            message_body="Test message.",
        )
        service._repository.create.return_value.notification_type = data.notification_type
        service._repository.create.return_value.notification_channel = data.channel
        notification, events = await service.create_notification(data)
        assert notification is not None
        assert len(events) == 1
        assert isinstance(events[0], NotificationCreatedEvent)
        assert events[0].notification_type == str(data.notification_type)

    async def test_create_notification_with_workflow_validation(
        self,
        service: NotificationService,
    ) -> None:
        data = NotificationCreate(
            workflow_id=uuid.uuid4(),
            notification_type=NotificationType.ALERT,
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            subject="Test",
            message_body="Test message.",
        )
        notification, events = await service.create_notification(data)
        assert notification is not None
        assert len(events) == 1

    async def test_create_notification_missing_workflow_raises(
        self,
        service: NotificationService,
    ) -> None:
        service._workflow_repository.get_by_id.return_value = None
        data = NotificationCreate(
            workflow_id=uuid.uuid4(),
            notification_type=NotificationType.ALERT,
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            subject="Test",
            message_body="Test message.",
        )
        with pytest.raises(NotificationValidationError):
            await service.create_notification(data)

    async def test_get_notification_found(
        self,
        service: NotificationService,
    ) -> None:
        notification = await service.get_notification(uuid.uuid4())
        assert notification is not None
        assert notification.notification_status == NotificationStatus.PENDING

    async def test_get_notification_not_found_raises(
        self,
        service: NotificationService,
    ) -> None:
        service._repository.get_by_id.return_value = None
        with pytest.raises(NotificationNotFoundError):
            await service.get_notification(uuid.uuid4())

    async def test_list_notifications(
        self,
        service: NotificationService,
    ) -> None:
        service._repository.list.return_value = ([], 0)
        items, total = await service.list_notifications()
        assert items == []
        assert total == 0

    async def test_queue_notification_returns_entity_and_event(
        self,
        service: NotificationService,
    ) -> None:
        service._repository.update.return_value.notification_status = NotificationStatus.QUEUED
        notification, events = await service.queue_notification(uuid.uuid4())
        assert notification is not None
        assert len(events) == 1
        assert isinstance(events[0], NotificationQueuedEvent)

    async def test_queue_archived_notification_raises(
        self,
        service: NotificationService,
        mocker,
        archived_notification_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**archived_notification_kwargs)
        with pytest.raises(NotificationValidationError):
            await service.queue_notification(uuid.uuid4())

    async def test_send_notification_returns_entity_and_event(
        self,
        service: NotificationService,
        mocker,
        pending_notification_kwargs: dict,
    ) -> None:
        kwargs = dict(pending_notification_kwargs)
        kwargs["notification_status"] = NotificationStatus.QUEUED
        service._repository.get_by_id.return_value = mocker.Mock(**kwargs)
        service._repository.update.return_value.notification_status = NotificationStatus.SENT
        notification, events = await service.send_notification(uuid.uuid4())
        assert notification is not None
        assert len(events) == 1
        assert isinstance(events[0], NotificationSentEvent)

    async def test_send_pending_notification_raises(
        self,
        service: NotificationService,
    ) -> None:
        with pytest.raises(NotificationValidationError):
            await service.send_notification(uuid.uuid4())

    async def test_retry_notification_returns_entity_and_event(
        self,
        service: NotificationService,
        mocker,
        failed_notification_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**failed_notification_kwargs)
        service._repository.update.return_value.notification_status = NotificationStatus.RETRYING
        notification, events = await service.retry_notification(uuid.uuid4())
        assert notification is not None
        assert len(events) == 1
        assert isinstance(events[0], NotificationRetriedEvent)
        assert events[0].attempt == 1

    async def test_retry_max_attempts_raises(
        self,
        service: NotificationService,
        mocker,
        failed_notification_kwargs: dict,
    ) -> None:
        kwargs = dict(failed_notification_kwargs)
        kwargs["retry_count"] = MAX_DELIVERY_ATTEMPTS
        service._repository.get_by_id.return_value = mocker.Mock(**kwargs)
        with pytest.raises(NotificationValidationError):
            await service.retry_notification(uuid.uuid4())

    async def test_retry_non_failed_notification_raises(
        self,
        service: NotificationService,
    ) -> None:
        with pytest.raises(NotificationValidationError):
            await service.retry_notification(uuid.uuid4())

    async def test_mark_delivered_returns_entity_and_event(
        self,
        service: NotificationService,
        mocker,
        pending_notification_kwargs: dict,
    ) -> None:
        kwargs = dict(pending_notification_kwargs)
        kwargs["notification_status"] = NotificationStatus.SENT
        service._repository.get_by_id.return_value = mocker.Mock(**kwargs)
        service._repository.update.return_value.notification_status = NotificationStatus.DELIVERED
        notification, events = await service.mark_delivered(uuid.uuid4())
        assert notification is not None
        assert len(events) == 1
        assert isinstance(events[0], NotificationDeliveredEvent)

    async def test_mark_delivered_pending_raises(
        self,
        service: NotificationService,
    ) -> None:
        with pytest.raises(NotificationValidationError):
            await service.mark_delivered(uuid.uuid4())

    async def test_mark_failed_returns_entity_and_event(
        self,
        service: NotificationService,
        mocker,
        pending_notification_kwargs: dict,
    ) -> None:
        kwargs = dict(pending_notification_kwargs)
        kwargs["notification_status"] = NotificationStatus.SENDING
        service._repository.get_by_id.return_value = mocker.Mock(**kwargs)
        service._repository.update.return_value.notification_status = NotificationStatus.FAILED
        notification, events = await service.mark_failed(
            uuid.uuid4(), reason="SMTP connection refused"
        )
        assert notification is not None
        assert len(events) == 1
        assert isinstance(events[0], NotificationFailedEvent)
        assert events[0].error == "SMTP connection refused"

    async def test_mark_failed_archived_raises(
        self,
        service: NotificationService,
        mocker,
        archived_notification_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**archived_notification_kwargs)
        with pytest.raises(NotificationValidationError):
            await service.mark_failed(uuid.uuid4())

    async def test_archive_notification_returns_entity_and_event(
        self,
        service: NotificationService,
        mocker,
        delivered_notification_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**delivered_notification_kwargs)
        service._repository.update.return_value.notification_status = NotificationStatus.ARCHIVED
        notification, events = await service.archive_notification(uuid.uuid4())
        assert notification is not None
        assert len(events) == 1
        assert isinstance(events[0], NotificationArchivedEvent)

    async def test_archive_archived_notification_raises(
        self,
        service: NotificationService,
        mocker,
        archived_notification_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**archived_notification_kwargs)
        with pytest.raises(NotificationValidationError):
            await service.archive_notification(uuid.uuid4())

    async def test_update_notification_returns_entity(
        self,
        service: NotificationService,
    ) -> None:
        data = NotificationUpdate(recipient="new@example.com")
        notification, events = await service.update_notification(uuid.uuid4(), data)
        assert notification is not None
        assert len(events) == 0

    async def test_update_archived_notification_raises(
        self,
        service: NotificationService,
        mocker,
        archived_notification_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**archived_notification_kwargs)
        data = NotificationUpdate(recipient="new@example.com")
        with pytest.raises(NotificationValidationError):
            await service.update_notification(uuid.uuid4(), data)

    async def test_logging_integration_on_create(
        self,
        service: NotificationService,
        mocker,
    ) -> None:
        service._logger = mocker.Mock()
        data = NotificationCreate(
            notification_type=NotificationType.ALERT,
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            subject="Test",
            message_body="Test message.",
        )
        await service.create_notification(data)
        assert service._logger.info.call_count == 2

    async def test_invalid_transition_raises(
        self,
        service: NotificationService,
    ) -> None:
        with pytest.raises(NotificationValidationError):
            await service.send_notification(uuid.uuid4())

    async def test_complete_queue_send_deliver_lifecycle(
        self,
        service: NotificationService,
        mocker,
        pending_notification_kwargs: dict,
    ) -> None:
        nid = uuid.uuid4()

        queued_kwargs = dict(pending_notification_kwargs)
        queued_kwargs["notification_status"] = NotificationStatus.QUEUED
        sent_kwargs = dict(pending_notification_kwargs)
        sent_kwargs["notification_status"] = NotificationStatus.SENT
        delivered_kwargs = dict(pending_notification_kwargs)
        delivered_kwargs["notification_status"] = NotificationStatus.DELIVERED

        service._repository.get_by_id.return_value = mocker.Mock(**pending_notification_kwargs)
        service._repository.update.return_value = mocker.Mock(**queued_kwargs)
        _, events = await service.queue_notification(nid)
        assert isinstance(events[0], NotificationQueuedEvent)

        service._repository.get_by_id.return_value = mocker.Mock(**queued_kwargs)
        service._repository.update.return_value = mocker.Mock(**sent_kwargs)
        _, events = await service.send_notification(nid)
        assert isinstance(events[0], NotificationSentEvent)

        service._repository.get_by_id.return_value = mocker.Mock(**sent_kwargs)
        service._repository.update.return_value = mocker.Mock(**delivered_kwargs)
        _, events = await service.mark_delivered(nid)
        assert isinstance(events[0], NotificationDeliveredEvent)
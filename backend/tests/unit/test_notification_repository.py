"""Notification repository unit tests."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from domains.complaint.constants.complaint_constants import ComplaintCategory
from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.workflow.constants.workflow_constants import WorkflowStatus, WorkflowStage, SLAStatus, EscalationLevel, ApprovalStatus
from domains.workflow.repositories.workflow_repository import WorkflowRepository
from domains.notification.constants.notification_constants import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)
from domains.notification.repositories.notification_repository import NotificationRepository


@pytest.fixture
async def repo(db_session: AsyncSession) -> NotificationRepository:
    return NotificationRepository(session=db_session)


@pytest.fixture
async def workflow(db_session: AsyncSession):
    complaint_repo = ComplaintRepository(session=db_session)
    complaint = await complaint_repo.create(
        title="Notification complaint",
        category=ComplaintCategory.SERVICE,
    )
    workflow_repo = WorkflowRepository(session=db_session)
    return await workflow_repo.create(complaint_id=complaint.id)


@pytest.mark.asyncio
class TestNotificationRepository:
    async def test_create_notification(self, repo: NotificationRepository, workflow) -> None:
        notification = await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.ALERT,
            notification_channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            subject="Test Alert",
            message="This is a test alert notification.",
        )
        assert notification.id is not None
        assert notification.workflow_id == workflow.id
        assert notification.notification_type == NotificationType.ALERT
        assert notification.notification_channel == NotificationChannel.EMAIL
        assert notification.notification_status == NotificationStatus.PENDING
        assert notification.priority == NotificationPriority.MEDIUM
        assert notification.retry_count == 0

    async def test_get_by_id_found(self, repo: NotificationRepository, workflow) -> None:
        created = await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.REMINDER,
            notification_channel=NotificationChannel.EMAIL,
            recipient="found@example.com",
            subject="Found test",
            message="Found test message.",
        )
        fetched = await repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.recipient == "found@example.com"

    async def test_get_by_id_not_found(self, repo: NotificationRepository) -> None:
        fetched = await repo.get_by_id(uuid.uuid4())
        assert fetched is None

    async def test_update_notification(self, repo: NotificationRepository, workflow) -> None:
        created = await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.SYSTEM,
            notification_channel=NotificationChannel.IN_APP,
            recipient="update@example.com",
            subject="Update test",
            message="Update test message.",
        )
        updated = await repo.update(
            created.id,
            notification_status=NotificationStatus.QUEUED,
            priority=NotificationPriority.HIGH,
        )
        assert updated is not None
        assert updated.notification_status == NotificationStatus.QUEUED
        assert updated.priority == NotificationPriority.HIGH

    async def test_update_not_found(self, repo: NotificationRepository) -> None:
        updated = await repo.update(uuid.uuid4(), notification_status=NotificationStatus.QUEUED)
        assert updated is None

    async def test_delete_notification(self, repo: NotificationRepository, workflow) -> None:
        created = await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.CONFIRMATION,
            notification_channel=NotificationChannel.SMS,
            recipient="delete@example.com",
            subject="Delete test",
            message="Delete test message.",
        )
        result = await repo.delete(created.id)
        assert result is True
        fetched = await repo.get_by_id(created.id)
        assert fetched is None

    async def test_delete_not_found(self, repo: NotificationRepository) -> None:
        result = await repo.delete(uuid.uuid4())
        assert result is False

    async def test_list_without_filters(self, repo: NotificationRepository, workflow) -> None:
        await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.ALERT,
            notification_channel=NotificationChannel.EMAIL,
            recipient="a@example.com",
            subject="A",
            message="A message.",
        )
        await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.REMINDER,
            notification_channel=NotificationChannel.SMS,
            recipient="b@example.com",
            subject="B",
            message="B message.",
        )
        items, total = await repo.list()
        assert total == 2
        assert len(items) == 2

    async def test_list_filters_by_status(self, repo: NotificationRepository, workflow) -> None:
        await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.ALERT,
            notification_channel=NotificationChannel.EMAIL,
            recipient="a@example.com",
            subject="Pending",
            message="Pending message.",
        )
        await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.REMINDER,
            notification_channel=NotificationChannel.SMS,
            recipient="b@example.com",
            subject="Queued",
            message="Queued message.",
            notification_status=NotificationStatus.QUEUED,
        )
        items, total = await repo.list(notification_status=NotificationStatus.PENDING)
        assert total == 1
        assert all(item.notification_status == NotificationStatus.PENDING for item in items)

    async def test_list_filters_by_type(self, repo: NotificationRepository, workflow) -> None:
        await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.ALERT,
            notification_channel=NotificationChannel.EMAIL,
            recipient="a@example.com",
            subject="Alert",
            message="Alert message.",
        )
        await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.REMINDER,
            notification_channel=NotificationChannel.SMS,
            recipient="b@example.com",
            subject="Reminder",
            message="Reminder message.",
        )
        items, total = await repo.list(notification_type=NotificationType.ALERT)
        assert total == 1
        assert all(item.notification_type == NotificationType.ALERT for item in items)

    async def test_list_filters_by_channel(self, repo: NotificationRepository, workflow) -> None:
        await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.ALERT,
            notification_channel=NotificationChannel.EMAIL,
            recipient="a@example.com",
            subject="Email",
            message="Email message.",
        )
        await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.REMINDER,
            notification_channel=NotificationChannel.SMS,
            recipient="b@example.com",
            subject="SMS",
            message="SMS message.",
        )
        items, total = await repo.list(notification_channel=NotificationChannel.EMAIL)
        assert total == 1
        assert all(item.notification_channel == NotificationChannel.EMAIL for item in items)

    async def test_list_filters_by_priority(self, repo: NotificationRepository, workflow) -> None:
        await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.ALERT,
            notification_channel=NotificationChannel.EMAIL,
            recipient="a@example.com",
            subject="Medium",
            message="Medium message.",
            priority=NotificationPriority.MEDIUM,
        )
        await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.REMINDER,
            notification_channel=NotificationChannel.SMS,
            recipient="b@example.com",
            subject="High",
            message="High message.",
            priority=NotificationPriority.HIGH,
        )
        items, total = await repo.list(priority=NotificationPriority.HIGH)
        assert total == 1
        assert all(item.priority == NotificationPriority.HIGH for item in items)

    async def test_list_filters_by_workflow_id(self, repo: NotificationRepository, workflow, db_session: AsyncSession) -> None:
        await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.ALERT,
            notification_channel=NotificationChannel.EMAIL,
            recipient="a@example.com",
            subject="WF1",
            message="WF1 message.",
        )
        w2 = await ComplaintRepository(session=db_session).create(
            title="Second complaint", category=ComplaintCategory.GENERAL
        )
        wf2 = await WorkflowRepository(session=db_session).create(complaint_id=w2.id)
        await repo.create(
            workflow_id=wf2.id,
            notification_type=NotificationType.REMINDER,
            notification_channel=NotificationChannel.SMS,
            recipient="b@example.com",
            subject="WF2",
            message="WF2 message.",
        )
        items, total = await repo.list(workflow_id=workflow.id)
        assert total == 1
        assert items[0].workflow_id == workflow.id

    async def test_list_pagination(self, repo: NotificationRepository, workflow) -> None:
        for i in range(5):
            await repo.create(
                workflow_id=workflow.id,
                notification_type=NotificationType.SYSTEM,
                notification_channel=NotificationChannel.IN_APP,
                recipient=f"user{i}@example.com",
                subject=f"Notification {i}",
                message=f"Message {i}.",
            )
        page1, total = await repo.list(page=1, page_size=2)
        page2, _ = await repo.list(page=2, page_size=2)
        page3, _ = await repo.list(page=3, page_size=2)
        assert total == 5
        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1

    async def test_get_by_workflow_id(self, repo: NotificationRepository, workflow, db_session: AsyncSession) -> None:
        n1 = await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.ALERT,
            notification_channel=NotificationChannel.EMAIL,
            recipient="a@example.com",
            subject="WF test",
            message="WF test message.",
        )
        w2 = await ComplaintRepository(session=db_session).create(
            title="Other", category=ComplaintCategory.GENERAL
        )
        wf2 = await WorkflowRepository(session=db_session).create(complaint_id=w2.id)
        await repo.create(
            workflow_id=wf2.id,
            notification_type=NotificationType.REMINDER,
            notification_channel=NotificationChannel.SMS,
            recipient="b@example.com",
            subject="Other WF",
            message="Other WF message.",
        )
        items = await repo.get_by_workflow_id(workflow.id)
        assert len(items) == 1
        assert items[0].id == n1.id

    async def test_get_by_complaint_id(self, repo: NotificationRepository, workflow, db_session: AsyncSession) -> None:
        n1 = await repo.create(
            workflow_id=workflow.id,
            notification_type=NotificationType.ALERT,
            notification_channel=NotificationChannel.EMAIL,
            recipient="a@example.com",
            subject="Complaint test",
            message="Complaint test message.",
            complaint_id=workflow.complaint_id,
        )
        c2 = await ComplaintRepository(session=db_session).create(
            title="Other", category=ComplaintCategory.GENERAL
        )
        wf2 = await WorkflowRepository(session=db_session).create(complaint_id=c2.id)
        await repo.create(
            workflow_id=wf2.id,
            notification_type=NotificationType.REMINDER,
            notification_channel=NotificationChannel.SMS,
            recipient="b@example.com",
            subject="Other",
            message="Other message.",
            complaint_id=c2.id,
        )
        items = await repo.get_by_complaint_id(workflow.complaint_id)
        assert len(items) == 1
        assert items[0].id == n1.id
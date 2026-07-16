"""Notification domain integration flow tests."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.complaint.constants.complaint_constants import ComplaintCategory
from domains.workflow.repositories.workflow_repository import WorkflowRepository
from domains.notification.constants.notification_constants import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
    MAX_DELIVERY_ATTEMPTS,
)
from domains.notification.repositories.notification_repository import NotificationRepository
from domains.notification.schemas.notification_schemas import NotificationCreate
from domains.notification.services.notification_service import NotificationService


@pytest.mark.asyncio
class TestNotificationFlow:
    """End-to-end flow through the notification layer."""

    async def _create_workflow(self, db_session: AsyncSession):
        complaint_repo = ComplaintRepository(session=db_session)
        complaint = await complaint_repo.create(
            title="Flow complaint", category=ComplaintCategory.SERVICE
        )
        workflow_repo = WorkflowRepository(session=db_session)
        return await workflow_repo.create(complaint_id=complaint.id)

    async def test_create_and_retrieve_flow(self, db_session: AsyncSession) -> None:
        workflow = await self._create_workflow(db_session)
        notification_repo = NotificationRepository(session=db_session)
        workflow_repo = WorkflowRepository(session=db_session)
        service = NotificationService(
            repository=notification_repo,
            workflow_repository=workflow_repo,
        )

        notification, events = await service.create_notification(
            NotificationCreate(
                workflow_id=workflow.id,
                notification_type=NotificationType.ALERT,
                channel=NotificationChannel.EMAIL,
                recipient="flow@example.com",
                subject="Flow test",
                message_body="Flow test message.",
            )
        )
        assert notification.id is not None
        assert notification.workflow_id == workflow.id
        assert notification.notification_status == NotificationStatus.PENDING
        assert notification.notification_type == NotificationType.ALERT
        assert notification.notification_channel == NotificationChannel.EMAIL
        assert notification.priority == NotificationPriority.MEDIUM
        assert notification.retry_count == 0
        assert len(events) == 1

        fetched = await service.get_notification(notification.id)
        assert fetched.id == notification.id

        by_workflow = await notification_repo.get_by_workflow_id(workflow.id)
        assert len(by_workflow) == 1
        assert by_workflow[0].id == notification.id

    async def test_full_queue_send_deliver_archive_flow(
        self, db_session: AsyncSession
    ) -> None:
        workflow = await self._create_workflow(db_session)
        notification_repo = NotificationRepository(session=db_session)
        workflow_repo = WorkflowRepository(session=db_session)
        service = NotificationService(
            repository=notification_repo,
            workflow_repository=workflow_repo,
        )

        created, _ = await service.create_notification(
            NotificationCreate(
                workflow_id=workflow.id,
                notification_type=NotificationType.ALERT,
                channel=NotificationChannel.EMAIL,
                recipient="flow@example.com",
                subject="Full lifecycle",
                message_body="Full lifecycle message.",
            )
        )
        assert created.notification_status == NotificationStatus.PENDING

        queued, events = await service.queue_notification(created.id)
        assert queued.notification_status == NotificationStatus.QUEUED
        assert len(events) == 1

        sent, events = await service.send_notification(queued.id)
        assert sent.notification_status == NotificationStatus.SENT
        assert sent.sent_at is not None
        assert len(events) == 1

        delivered, events = await service.mark_delivered(sent.id)
        assert delivered.notification_status == NotificationStatus.DELIVERED
        assert delivered.delivered_at is not None
        assert len(events) == 1

        archived, events = await service.archive_notification(delivered.id)
        assert archived.notification_status == NotificationStatus.ARCHIVED
        assert len(events) == 1

    async def test_fail_and_retry_flow(self, db_session: AsyncSession) -> None:
        workflow = await self._create_workflow(db_session)
        notification_repo = NotificationRepository(session=db_session)
        workflow_repo = WorkflowRepository(session=db_session)
        service = NotificationService(
            repository=notification_repo,
            workflow_repository=workflow_repo,
        )

        created, _ = await service.create_notification(
            NotificationCreate(
                workflow_id=workflow.id,
                notification_type=NotificationType.ALERT,
                channel=NotificationChannel.EMAIL,
                recipient="retry@example.com",
                subject="Retry test",
                message_body="Retry test message.",
            )
        )

        await service.queue_notification(created.id)
        await service.send_notification(created.id)

        failed, events = await service.mark_failed(
            created.id, reason="Connection timeout"
        )
        assert failed.notification_status == NotificationStatus.FAILED
        assert failed.failure_reason == "Connection timeout"
        assert len(events) == 1

        retried, events = await service.retry_notification(created.id)
        assert retried.notification_status == NotificationStatus.RETRYING
        assert retried.retry_count == 1
        assert len(events) == 1

        await service.mark_failed(created.id, reason="Second timeout")

        retried_again, events = await service.retry_notification(created.id)
        assert retried_again.retry_count == 2
        assert len(events) == 1

    async def test_max_retry_limit_enforced(self, db_session: AsyncSession) -> None:
        workflow = await self._create_workflow(db_session)
        notification_repo = NotificationRepository(session=db_session)
        workflow_repo = WorkflowRepository(session=db_session)
        service = NotificationService(
            repository=notification_repo,
            workflow_repository=workflow_repo,
        )

        created, _ = await service.create_notification(
            NotificationCreate(
                workflow_id=workflow.id,
                notification_type=NotificationType.ALERT,
                channel=NotificationChannel.EMAIL,
                recipient="maxretry@example.com",
                subject="Max retry",
                message_body="Max retry test.",
            )
        )

        await service.queue_notification(created.id)
        await service.send_notification(created.id)

        for _ in range(MAX_DELIVERY_ATTEMPTS):
            await service.mark_failed(created.id, reason="Timeout")
            await service.retry_notification(created.id)

        await service.mark_failed(created.id, reason="Final timeout")
        with pytest.raises(Exception):
            await service.retry_notification(created.id)

    async def test_full_api_flow(self, client: AsyncClient) -> None:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "API notification flow", "category": "service"},
        )
        assert complaint_resp.status_code == 201
        complaint_id = complaint_resp.json()["data"]["id"]

        wf_resp = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id},
        )
        assert wf_resp.status_code == 201
        workflow_id = wf_resp.json()["data"]["id"]

        notif_resp = await client.post(
            "/api/v1/notifications",
            json={
                "workflow_id": workflow_id,
                "notification_type": "alert",
                "channel": "email",
                "recipient": "api@example.com",
                "subject": "API flow",
                "message_body": "API flow message.",
            },
        )
        assert notif_resp.status_code == 201
        notification_id = notif_resp.json()["data"]["id"]
        assert notif_resp.json()["data"]["workflow_id"] == workflow_id

        get_resp = await client.get(f"/api/v1/notifications/{notification_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["notification_status"] == "pending"

        queue_resp = await client.post(
            f"/api/v1/notifications/{notification_id}/queue"
        )
        assert queue_resp.status_code == 200
        assert queue_resp.json()["data"]["notification_status"] == "queued"

        send_resp = await client.post(
            f"/api/v1/notifications/{notification_id}/send"
        )
        assert send_resp.status_code == 200
        assert send_resp.json()["data"]["notification_status"] == "sent"

        deliver_resp = await client.post(
            f"/api/v1/notifications/{notification_id}/deliver"
        )
        assert deliver_resp.status_code == 200
        assert deliver_resp.json()["data"]["notification_status"] == "delivered"

        list_resp = await client.get(
            "/api/v1/notifications?notification_status=delivered"
        )
        assert list_resp.status_code == 200
        ids = [item["id"] for item in list_resp.json()["data"]]
        assert notification_id in ids

        archive_resp = await client.post(
            f"/api/v1/notifications/{notification_id}/archive"
        )
        assert archive_resp.status_code == 200
        assert archive_resp.json()["data"]["notification_status"] == "archived"
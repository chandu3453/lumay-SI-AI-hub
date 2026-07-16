"""Notification REST API unit tests."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestNotificationAPI:
    async def _create_workflow(self, client: AsyncClient) -> str:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Notification API", "category": "service"},
        )
        complaint_id = complaint_resp.json()["data"]["id"]
        wf_resp = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id},
        )
        return wf_resp.json()["data"]["id"]

    async def test_create_notification_201(self, client: AsyncClient) -> None:
        workflow_id = await self._create_workflow(client)
        response = await client.post(
            "/api/v1/notifications",
            json={
                "workflow_id": workflow_id,
                "notification_type": "alert",
                "channel": "email",
                "recipient": "user@example.com",
                "subject": "Test alert",
                "message_body": "This is a test alert.",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["workflow_id"] == workflow_id
        assert body["data"]["notification_type"] == "alert"
        assert body["data"]["notification_channel"] == "email"
        assert body["data"]["notification_status"] == "pending"
        assert body["data"]["priority"] == "medium"
        assert body["data"]["retry_count"] == 0

    async def test_create_notification_minimal_201(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/notifications",
            json={
                "notification_type": "system",
                "channel": "in_app",
                "recipient": "user@example.com",
                "subject": "System notice",
                "message_body": "System notification.",
            },
        )
        assert response.status_code == 201
        assert response.json()["success"] is True

    async def test_create_notification_missing_workflow_422(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(
            "/api/v1/notifications",
            json={
                "workflow_id": str(uuid.uuid4()),
                "notification_type": "alert",
                "channel": "email",
                "recipient": "user@example.com",
                "subject": "Test",
                "message_body": "Test message.",
            },
        )
        assert response.status_code == 422
        assert response.json()["error_code"] == "NOTIFICATION__VALIDATION_ERROR"

    async def test_get_notification_200(self, client: AsyncClient) -> None:
        workflow_id = await self._create_workflow(client)
        create_resp = await client.post(
            "/api/v1/notifications",
            json={
                "workflow_id": workflow_id,
                "notification_type": "reminder",
                "channel": "sms",
                "recipient": "user@example.com",
                "subject": "Reminder",
                "message_body": "This is a reminder.",
            },
        )
        notification_id = create_resp.json()["data"]["id"]

        response = await client.get(f"/api/v1/notifications/{notification_id}")
        assert response.status_code == 200
        assert response.json()["data"]["id"] == notification_id

    async def test_get_notification_404(self, client: AsyncClient) -> None:
        response = await client.get(f"/api/v1/notifications/{uuid.uuid4()}")
        assert response.status_code == 404
        assert response.json()["error_code"] == "NOTIFICATION__NOT_FOUND"

    async def test_list_notifications_200(self, client: AsyncClient) -> None:
        wf1 = await self._create_workflow(client)
        wf2 = await self._create_workflow(client)
        await client.post(
            "/api/v1/notifications",
            json={
                "workflow_id": wf1,
                "notification_type": "alert",
                "channel": "email",
                "recipient": "a@example.com",
                "subject": "A",
                "message_body": "A message.",
            },
        )
        await client.post(
            "/api/v1/notifications",
            json={
                "workflow_id": wf2,
                "notification_type": "reminder",
                "channel": "sms",
                "recipient": "b@example.com",
                "subject": "B",
                "message_body": "B message.",
            },
        )

        response = await client.get("/api/v1/notifications")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert body["total"] == 2

    async def test_list_notifications_with_filters(
        self, client: AsyncClient
    ) -> None:
        wf = await self._create_workflow(client)
        await client.post(
            "/api/v1/notifications",
            json={
                "workflow_id": wf,
                "notification_type": "alert",
                "channel": "email",
                "recipient": "a@example.com",
                "subject": "Alert",
                "message_body": "Alert message.",
            },
        )
        response = await client.get(
            "/api/v1/notifications?notification_type=alert"
        )
        assert response.status_code == 200
        assert all(
            item["notification_type"] == "alert"
            for item in response.json()["data"]
        )

    async def test_update_notification_200(self, client: AsyncClient) -> None:
        wf = await self._create_workflow(client)
        create_resp = await client.post(
            "/api/v1/notifications",
            json={
                "workflow_id": wf,
                "notification_type": "alert",
                "channel": "email",
                "recipient": "old@example.com",
                "subject": "Old",
                "message_body": "Old message.",
            },
        )
        notification_id = create_resp.json()["data"]["id"]

        response = await client.patch(
            f"/api/v1/notifications/{notification_id}",
            json={"recipient": "new@example.com", "priority": "high"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["recipient"] == "new@example.com"
        assert response.json()["data"]["priority"] == "high"

    async def test_update_nonexistent_notification_404(
        self, client: AsyncClient
    ) -> None:
        response = await client.patch(
            f"/api/v1/notifications/{uuid.uuid4()}",
            json={"priority": "low"},
        )
        assert response.status_code == 404

    async def test_queue_notification_200(self, client: AsyncClient) -> None:
        wf = await self._create_workflow(client)
        create_resp = await client.post(
            "/api/v1/notifications",
            json={
                "workflow_id": wf,
                "notification_type": "alert",
                "channel": "email",
                "recipient": "user@example.com",
                "subject": "Queue test",
                "message_body": "Queue test message.",
            },
        )
        notification_id = create_resp.json()["data"]["id"]

        response = await client.post(
            f"/api/v1/notifications/{notification_id}/queue"
        )
        assert response.status_code == 200
        assert response.json()["data"]["notification_status"] == "queued"

    async def test_queue_and_send_lifecycle(self, client: AsyncClient) -> None:
        wf = await self._create_workflow(client)
        create_resp = await client.post(
            "/api/v1/notifications",
            json={
                "workflow_id": wf,
                "notification_type": "alert",
                "channel": "email",
                "recipient": "user@example.com",
                "subject": "Lifecycle",
                "message_body": "Lifecycle test.",
            },
        )
        nid = create_resp.json()["data"]["id"]

        queue_resp = await client.post(f"/api/v1/notifications/{nid}/queue")
        assert queue_resp.status_code == 200

        send_resp = await client.post(f"/api/v1/notifications/{nid}/send")
        assert send_resp.status_code == 200
        assert send_resp.json()["data"]["notification_status"] == "sent"

        deliver_resp = await client.post(
            f"/api/v1/notifications/{nid}/deliver"
        )
        assert deliver_resp.status_code == 200
        assert deliver_resp.json()["data"]["notification_status"] == "delivered"

        archive_resp = await client.post(
            f"/api/v1/notifications/{nid}/archive"
        )
        assert archive_resp.status_code == 200
        assert archive_resp.json()["data"]["notification_status"] == "archived"

    async def test_fail_and_retry_lifecycle(self, client: AsyncClient) -> None:
        wf = await self._create_workflow(client)
        create_resp = await client.post(
            "/api/v1/notifications",
            json={
                "workflow_id": wf,
                "notification_type": "alert",
                "channel": "email",
                "recipient": "user@example.com",
                "subject": "Fail retry",
                "message_body": "Fail retry test.",
            },
        )
        nid = create_resp.json()["data"]["id"]

        await client.post(f"/api/v1/notifications/{nid}/queue")
        await client.post(f"/api/v1/notifications/{nid}/send")

        fail_resp = await client.post(
            f"/api/v1/notifications/{nid}/fail",
            json={"reason": "SMTP timeout"},
        )
        assert fail_resp.status_code == 200
        assert fail_resp.json()["data"]["notification_status"] == "failed"
        assert fail_resp.json()["data"]["failure_reason"] == "SMTP timeout"

        retry_resp = await client.post(
            f"/api/v1/notifications/{nid}/retry"
        )
        assert retry_resp.status_code == 200
        assert retry_resp.json()["data"]["notification_status"] == "retrying"
        assert retry_resp.json()["data"]["retry_count"] == 1

    async def test_archive_archived_notification_422(
        self, client: AsyncClient
    ) -> None:
        wf = await self._create_workflow(client)
        create_resp = await client.post(
            "/api/v1/notifications",
            json={
                "workflow_id": wf,
                "notification_type": "alert",
                "channel": "email",
                "recipient": "user@example.com",
                "subject": "Double archive",
                "message_body": "Double archive test.",
            },
        )
        nid = create_resp.json()["data"]["id"]

        await client.post(f"/api/v1/notifications/{nid}/queue")
        await client.post(f"/api/v1/notifications/{nid}/send")
        await client.post(f"/api/v1/notifications/{nid}/deliver")
        await client.post(f"/api/v1/notifications/{nid}/archive")

        archive_resp = await client.post(
            f"/api/v1/notifications/{nid}/archive"
        )
        assert archive_resp.status_code == 422
        assert archive_resp.json()["error_code"] == "NOTIFICATION__VALIDATION_ERROR"

    async def test_invalid_transition_422(self, client: AsyncClient) -> None:
        wf = await self._create_workflow(client)
        create_resp = await client.post(
            "/api/v1/notifications",
            json={
                "workflow_id": wf,
                "notification_type": "alert",
                "channel": "email",
                "recipient": "user@example.com",
                "subject": "Invalid transition",
                "message_body": "Invalid transition test.",
            },
        )
        nid = create_resp.json()["data"]["id"]

        response = await client.post(f"/api/v1/notifications/{nid}/send")
        assert response.status_code == 422
        assert response.json()["error_code"] == "NOTIFICATION__VALIDATION_ERROR"
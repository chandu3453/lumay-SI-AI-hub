"""Auth enforcement on employee-only mutating actions (Sprint 30).

Scope decision: only the genuinely employee-only admin/lifecycle actions are
locked (assign/escalate/resolve/close/etc.) — list/read endpoints and the
handful of endpoints the customer portal itself calls unauthenticated
(complaints list, notifications list, conversation typing) are left open to
avoid regressing the customer portal, which has no real backend session.
"""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestEmployeeAuthEnforcement:
    async def test_close_conversation_requires_auth(self, unauthenticated_client: AsyncClient) -> None:
        response = await unauthenticated_client.post(
            f"/api/v1/conversations/{uuid.uuid4()}/close"
        )
        assert response.status_code == 401

    async def test_close_conversation_succeeds_with_auth(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/conversations", json={"current_channel": "web_chat"})
        conversation_id = create_resp.json()["data"]["id"]
        response = await client.post(f"/api/v1/conversations/{conversation_id}/close")
        assert response.status_code == 200

    async def test_assign_complaint_requires_auth(self, unauthenticated_client: AsyncClient) -> None:
        response = await unauthenticated_client.post(
            f"/api/v1/complaints/{uuid.uuid4()}/assign", json={"agent_id": str(uuid.uuid4())}
        )
        assert response.status_code == 401

    async def test_archive_workflow_requires_auth(self, unauthenticated_client: AsyncClient) -> None:
        response = await unauthenticated_client.post(f"/api/v1/workflows/{uuid.uuid4()}/archive")
        assert response.status_code == 401

    async def test_create_notification_requires_auth(self, unauthenticated_client: AsyncClient) -> None:
        response = await unauthenticated_client.post(
            "/api/v1/notifications",
            json={"notification_type": "email", "notification_channel": "email", "recipient": "a@b.com", "subject": "x", "message": "y"},
        )
        assert response.status_code == 401

    async def test_list_complaints_stays_open_for_customer_portal(
        self, unauthenticated_client: AsyncClient
    ) -> None:
        # The customer dashboard calls this unauthenticated today — must not regress.
        response = await unauthenticated_client.get("/api/v1/complaints")
        assert response.status_code == 200

    async def test_list_notifications_stays_open_for_customer_portal(
        self, unauthenticated_client: AsyncClient
    ) -> None:
        response = await unauthenticated_client.get("/api/v1/notifications")
        assert response.status_code == 200

    async def test_conversation_typing_stays_open_for_customer_webchat(
        self, unauthenticated_client: AsyncClient
    ) -> None:
        create_resp = await unauthenticated_client.post(
            "/api/v1/conversations", json={"current_channel": "web_chat"}
        )
        conversation_id = create_resp.json()["data"]["id"]
        response = await unauthenticated_client.post(
            f"/api/v1/conversations/{conversation_id}/typing",
            json={"participant_type": "customer", "is_typing": True},
        )
        assert response.status_code == 200

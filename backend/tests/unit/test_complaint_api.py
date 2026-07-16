"""Complaint REST API unit tests."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestComplaintAPI:
    async def test_create_complaint_201(self, client: AsyncClient) -> None:
        payload = {
            "title": "Billing discrepancy",
            "description": "Premium amount is incorrect.",
            "category": "billing",
            "priority": "high",
            "severity": "major",
        }
        response = await client.post("/api/v1/complaints", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["title"] == "Billing discrepancy"
        assert body["data"]["category"] == "billing"
        assert body["data"]["status"] == "submitted"

    async def test_create_complaint_missing_title_422(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.post(
            "/api/v1/complaints",
            json={"category": "billing"},
        )
        assert response.status_code == 422
        assert response.json()["error_code"] == "VALIDATION_ERROR"

    async def test_create_complaint_invalid_customer_422(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.post(
            "/api/v1/complaints",
            json={
                "customer_id": str(uuid.uuid4()),
                "title": "Bad customer reference",
                "category": "service",
            },
        )
        assert response.status_code == 422
        assert response.json()["error_code"] == "COMPLAINT__VALIDATION_ERROR"

    async def test_get_complaint_200(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Get me", "category": "general"},
        )
        complaint_id = create_resp.json()["data"]["id"]

        response = await client.get(f"/api/v1/complaints/{complaint_id}")
        assert response.status_code == 200
        assert response.json()["data"]["id"] == complaint_id

    async def test_get_complaint_404(self, client: AsyncClient) -> None:
        response = await client.get(f"/api/v1/complaints/{uuid.uuid4()}")
        assert response.status_code == 404
        assert response.json()["error_code"] == "COMPLAINT__NOT_FOUND"

    async def test_list_complaints_200(self, client: AsyncClient) -> None:
        await client.post(
            "/api/v1/complaints",
            json={"title": "List A", "category": "general"},
        )
        await client.post(
            "/api/v1/complaints",
            json={"title": "List B", "category": "service"},
        )

        response = await client.get("/api/v1/complaints")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert body["total"] == 2
        assert body["page"] == 1
        assert body["page_size"] == 20
        assert body["total_pages"] == 1

    async def test_list_complaints_with_filters(
        self,
        client: AsyncClient,
    ) -> None:
        await client.post(
            "/api/v1/complaints",
            json={"title": "Service complaint", "category": "service"},
        )
        await client.post(
            "/api/v1/complaints",
            json={"title": "Claims complaint", "category": "claims"},
        )

        response = await client.get("/api/v1/complaints?category=service")
        assert response.status_code == 200
        assert all(item["category"] == "service" for item in response.json()["data"])

    async def test_update_complaint_200(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Original", "category": "general"},
        )
        complaint_id = create_resp.json()["data"]["id"]

        response = await client.patch(
            f"/api/v1/complaints/{complaint_id}",
            json={"title": "Updated"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Updated"

    async def test_update_nonexistent_complaint_404(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.patch(
            f"/api/v1/complaints/{uuid.uuid4()}",
            json={"title": "Nope"},
        )
        assert response.status_code == 404

    async def test_assign_complaint_200(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Assign me", "category": "service"},
        )
        complaint_id = create_resp.json()["data"]["id"]
        agent_id = str(uuid.uuid4())

        response = await client.post(
            f"/api/v1/complaints/{complaint_id}/assign",
            json={"agent_id": agent_id, "queue": "tier-2"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["assigned_agent_id"] == agent_id
        assert response.json()["data"]["assigned_queue"] == "tier-2"

    async def test_assign_complaint_validation_error_422(
        self,
        client: AsyncClient,
    ) -> None:
        create_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Assign invalid", "category": "service"},
        )
        complaint_id = create_resp.json()["data"]["id"]

        response = await client.post(
            f"/api/v1/complaints/{complaint_id}/assign",
            json={"queue": "tier-2"},
        )
        assert response.status_code == 422
        assert response.json()["error_code"] == "VALIDATION_ERROR"

    async def test_escalate_resolve_close_archive_lifecycle(
        self,
        client: AsyncClient,
    ) -> None:
        create_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Lifecycle", "category": "claims"},
        )
        complaint_id = create_resp.json()["data"]["id"]

        escalate_resp = await client.post(f"/api/v1/complaints/{complaint_id}/escalate")
        assert escalate_resp.status_code == 200
        assert escalate_resp.json()["data"]["status"] == "escalated"

        resolve_resp = await client.post(f"/api/v1/complaints/{complaint_id}/resolve")
        assert resolve_resp.status_code == 200
        assert resolve_resp.json()["data"]["status"] == "resolved"

        close_resp = await client.post(f"/api/v1/complaints/{complaint_id}/close")
        assert close_resp.status_code == 200
        assert close_resp.json()["data"]["status"] == "closed"

        archive_resp = await client.post(f"/api/v1/complaints/{complaint_id}/archive")
        assert archive_resp.status_code == 422
        assert archive_resp.json()["error_code"] == "COMPLAINT__VALIDATION_ERROR"

    async def test_update_closed_complaint_422(
        self,
        client: AsyncClient,
    ) -> None:
        create_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Closed update", "category": "general"},
        )
        complaint_id = create_resp.json()["data"]["id"]
        await client.post(f"/api/v1/complaints/{complaint_id}/close")

        response = await client.patch(
            f"/api/v1/complaints/{complaint_id}",
            json={"title": "Nope"},
        )
        assert response.status_code == 422
        assert response.json()["error_code"] == "COMPLAINT__VALIDATION_ERROR"


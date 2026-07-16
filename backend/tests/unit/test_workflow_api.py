"""Workflow REST API unit tests."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestWorkflowAPI:
    async def test_create_workflow_201(self, client: AsyncClient) -> None:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Workflow API", "category": "service"},
        )
        complaint_id = complaint_resp.json()["data"]["id"]

        response = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id, "priority": "high"},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["complaint_id"] == complaint_id
        assert body["data"]["workflow_status"] == "active"
        assert body["data"]["workflow_stage"] == "initiated"
        assert body["data"]["sla_status"] == "within_sla"
        assert body["data"]["escalation_level"] == "level_0"
        assert body["data"]["approval_status"] == "not_required"

    async def test_create_workflow_missing_complaint_422(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": str(uuid.uuid4())},
        )
        assert response.status_code == 422
        assert response.json()["error_code"] == "WORKFLOW__VALIDATION_ERROR"

    async def test_create_workflow_duplicate_active_422(
        self,
        client: AsyncClient,
    ) -> None:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Dup workflow", "category": "billing"},
        )
        complaint_id = complaint_resp.json()["data"]["id"]
        await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id},
        )
        response = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id},
        )
        assert response.status_code == 422
        assert response.json()["error_code"] == "WORKFLOW__VALIDATION_ERROR"

    async def test_get_workflow_200(self, client: AsyncClient) -> None:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Get workflow", "category": "claims"},
        )
        complaint_id = complaint_resp.json()["data"]["id"]
        create_resp = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id},
        )
        workflow_id = create_resp.json()["data"]["id"]

        response = await client.get(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 200
        assert response.json()["data"]["id"] == workflow_id

    async def test_get_workflow_404(self, client: AsyncClient) -> None:
        response = await client.get(f"/api/v1/workflows/{uuid.uuid4()}")
        assert response.status_code == 404
        assert response.json()["error_code"] == "WORKFLOW__NOT_FOUND"

    async def test_list_workflows_200(self, client: AsyncClient) -> None:
        c1 = await client.post(
            "/api/v1/complaints",
            json={"title": "List A", "category": "general"},
        )
        c2 = await client.post(
            "/api/v1/complaints",
            json={"title": "List B", "category": "service"},
        )
        await client.post(
            "/api/v1/workflows",
            json={"complaint_id": c1.json()["data"]["id"]},
        )
        await client.post(
            "/api/v1/workflows",
            json={"complaint_id": c2.json()["data"]["id"]},
        )

        response = await client.get("/api/v1/workflows")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert body["total"] == 2

    async def test_list_workflows_with_filters(
        self,
        client: AsyncClient,
    ) -> None:
        c = await client.post(
            "/api/v1/complaints",
            json={"title": "Filter", "category": "general"},
        )
        await client.post(
            "/api/v1/workflows",
            json={"complaint_id": c.json()["data"]["id"]},
        )
        response = await client.get("/api/v1/workflows?workflow_status=active")
        assert response.status_code == 200
        assert all(
            item["workflow_status"] == "active" for item in response.json()["data"]
        )

    async def test_assign_workflow_200(self, client: AsyncClient) -> None:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Assign workflow", "category": "service"},
        )
        complaint_id = complaint_resp.json()["data"]["id"]
        wf_resp = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id},
        )
        workflow_id = wf_resp.json()["data"]["id"]
        agent_id = str(uuid.uuid4())

        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/assign",
            json={"agent_id": agent_id, "team": "claims", "queue": "tier-2"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["assigned_agent_id"] == agent_id
        assert response.json()["data"]["workflow_stage"] == "assigned"

    async def test_assign_workflow_missing_agent_422(
        self,
        client: AsyncClient,
    ) -> None:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Assign invalid", "category": "service"},
        )
        complaint_id = complaint_resp.json()["data"]["id"]
        wf_resp = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id},
        )
        workflow_id = wf_resp.json()["data"]["id"]

        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/assign",
            json={"queue": "tier-2"},
        )
        assert response.status_code == 422
        assert response.json()["error_code"] == "VALIDATION_ERROR"

    async def test_transfer_workflow_200(self, client: AsyncClient) -> None:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Transfer", "category": "claims"},
        )
        complaint_id = complaint_resp.json()["data"]["id"]
        wf_resp = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id},
        )
        workflow_id = wf_resp.json()["data"]["id"]
        agent_id = str(uuid.uuid4())
        await client.post(
            f"/api/v1/workflows/{workflow_id}/assign",
            json={"agent_id": agent_id},
        )
        new_agent = str(uuid.uuid4())

        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/transfer",
            json={"agent_id": new_agent, "team": "billing"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["assigned_agent_id"] == new_agent

    async def test_transfer_unassigned_workflow_422(
        self,
        client: AsyncClient,
    ) -> None:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Transfer no assign", "category": "claims"},
        )
        complaint_id = complaint_resp.json()["data"]["id"]
        wf_resp = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id},
        )
        workflow_id = wf_resp.json()["data"]["id"]

        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/transfer",
            json={"agent_id": str(uuid.uuid4())},
        )
        assert response.status_code == 422

    async def test_escalate_workflow_200(self, client: AsyncClient) -> None:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Escalate", "category": "general"},
        )
        complaint_id = complaint_resp.json()["data"]["id"]
        wf_resp = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id},
        )
        workflow_id = wf_resp.json()["data"]["id"]

        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/escalate",
            json={"reason": "Customer complaint urgent"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["escalation_level"] == "level_1"
        assert response.json()["data"]["sla_status"] == "at_risk"

    async def test_approve_reject_complete_archive_lifecycle(
        self,
        client: AsyncClient,
    ) -> None:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Lifecycle", "category": "claims"},
        )
        complaint_id = complaint_resp.json()["data"]["id"]
        wf_resp = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id},
        )
        workflow_id = wf_resp.json()["data"]["id"]
        agent_id = str(uuid.uuid4())
        approver_id = str(uuid.uuid4())

        await client.post(
            f"/api/v1/workflows/{workflow_id}/assign",
            json={"agent_id": agent_id, "team": "claims"},
        )

        await client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={"workflow_stage": "in_progress"},
        )
        await client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={"workflow_stage": "review"},
        )
        await client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={"workflow_stage": "approval"},
        )

        approve_resp = await client.post(
            f"/api/v1/workflows/{workflow_id}/approve",
            json={"approved_by": approver_id},
        )
        assert approve_resp.status_code == 200
        assert approve_resp.json()["data"]["approval_status"] == "approved"

        complete_resp = await client.post(
            f"/api/v1/workflows/{workflow_id}/complete"
        )
        assert complete_resp.status_code == 200
        assert complete_resp.json()["data"]["workflow_status"] == "completed"
        assert complete_resp.json()["data"]["workflow_stage"] == "completed"

        archive_resp = await client.post(
            f"/api/v1/workflows/{workflow_id}/archive"
        )
        assert archive_resp.status_code == 200
        assert archive_resp.json()["data"]["workflow_status"] == "archived"

    async def test_reject_workflow_200(self, client: AsyncClient) -> None:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Reject", "category": "claims"},
        )
        complaint_id = complaint_resp.json()["data"]["id"]
        wf_resp = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id},
        )
        workflow_id = wf_resp.json()["data"]["id"]
        rejector_id = str(uuid.uuid4())

        await client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={"workflow_stage": "in_progress"},
        )
        await client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={"workflow_stage": "review"},
        )
        await client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={"workflow_stage": "approval", "approval_status": "pending"},
        )

        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/reject",
            json={"rejected_by": rejector_id, "reason": "Insufficient evidence"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["approval_status"] == "rejected"

    async def test_update_workflow_200(self, client: AsyncClient) -> None:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "Update", "category": "general"},
        )
        complaint_id = complaint_resp.json()["data"]["id"]
        wf_resp = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id},
        )
        workflow_id = wf_resp.json()["data"]["id"]

        response = await client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={"priority": "critical", "workflow_stage": "assigned"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["priority"] == "critical"

    async def test_update_nonexistent_workflow_404(
        self,
        client: AsyncClient,
    ) -> None:
        response = await client.patch(
            f"/api/v1/workflows/{uuid.uuid4()}",
            json={"priority": "low"},
        )
        assert response.status_code == 404

    async def test_complete_without_approval_422(
        self,
        client: AsyncClient,
    ) -> None:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "No approval", "category": "claims"},
        )
        complaint_id = complaint_resp.json()["data"]["id"]
        wf_resp = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id},
        )
        workflow_id = wf_resp.json()["data"]["id"]

        await client.patch(
            f"/api/v1/workflows/{workflow_id}",
            json={"approval_status": "pending"},
        )

        response = await client.post(
            f"/api/v1/workflows/{workflow_id}/complete"
        )
        assert response.status_code == 422
        assert response.json()["error_code"] == "WORKFLOW__VALIDATION_ERROR"
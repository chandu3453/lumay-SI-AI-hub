"""Workflow domain integration flow tests."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.complaint.constants.complaint_constants import ComplaintCategory
from domains.workflow.constants.workflow_constants import (
    ApprovalStatus,
    EscalationLevel,
    SLAStatus,
    WorkflowStage,
    WorkflowStatus,
)
from domains.workflow.repositories.workflow_repository import WorkflowRepository
from domains.workflow.schemas.workflow_schemas import WorkflowCreate, WorkflowUpdate
from domains.workflow.services.workflow_service import WorkflowService


@pytest.mark.asyncio
class TestWorkflowFlow:
    """End-to-end flow through the workflow layer."""

    async def test_create_and_retrieve_flow(self, db_session: AsyncSession) -> None:
        complaint_repo = ComplaintRepository(session=db_session)
        workflow_repo = WorkflowRepository(session=db_session)
        service = WorkflowService(
            repository=workflow_repo,
            complaint_repository=complaint_repo,
        )

        complaint = await complaint_repo.create(
            title="Flow complaint",
            category=ComplaintCategory.SERVICE,
        )

        workflow, events = await service.create_workflow(
            WorkflowCreate(complaint_id=complaint.id, priority="high")
        )
        assert workflow.id is not None
        assert workflow.complaint_id == complaint.id
        assert workflow.workflow_status == WorkflowStatus.ACTIVE
        assert workflow.workflow_stage == WorkflowStage.INITIATED
        assert workflow.sla_status == SLAStatus.WITHIN_SLA
        assert workflow.escalation_level == EscalationLevel.LEVEL_0
        assert workflow.approval_status == ApprovalStatus.NOT_REQUIRED
        assert workflow.priority == "high"
        assert len(events) == 1

        fetched = await service.get_workflow(workflow.id)
        assert fetched.id == workflow.id

        by_complaint = await workflow_repo.get_by_complaint_id(complaint.id)
        assert len(by_complaint) == 1
        assert by_complaint[0].id == workflow.id

    async def test_full_lifecycle_flow(self, db_session: AsyncSession) -> None:
        complaint_repo = ComplaintRepository(session=db_session)
        workflow_repo = WorkflowRepository(session=db_session)
        service = WorkflowService(
            repository=workflow_repo,
            complaint_repository=complaint_repo,
        )

        complaint = await complaint_repo.create(
            title="Lifecycle complaint",
            category=ComplaintCategory.CLAIMS,
        )
        created, _ = await service.create_workflow(
            WorkflowCreate(complaint_id=complaint.id)
        )
        assert created.workflow_status == WorkflowStatus.ACTIVE

        assigned, events = await service.assign_workflow(
            created.id,
            agent_id=uuid.uuid4(),
            team="claims",
            queue="tier-2",
        )
        assert assigned.workflow_stage == WorkflowStage.ASSIGNED
        assert len(events) == 1

        in_progress, _ = await service.update_workflow(
            assigned.id, WorkflowUpdate(workflow_stage=WorkflowStage.IN_PROGRESS)
        )
        assert in_progress.workflow_stage == WorkflowStage.IN_PROGRESS

        reviewed, _ = await service.update_workflow(
            in_progress.id, WorkflowUpdate(workflow_stage=WorkflowStage.REVIEW)
        )
        assert reviewed.workflow_stage == WorkflowStage.REVIEW

        approval, _ = await service.update_workflow(
            reviewed.id, WorkflowUpdate(workflow_stage=WorkflowStage.APPROVAL)
        )
        assert approval.workflow_stage == WorkflowStage.APPROVAL

        approved, _ = await service.approve_workflow(
            approval.id, approved_by=uuid.uuid4()
        )
        assert approved.approval_status == ApprovalStatus.APPROVED

        completed, events = await service.complete_workflow(approved.id)
        assert completed.workflow_status == WorkflowStatus.COMPLETED
        assert completed.completed_at is not None
        assert len(events) == 1

        archived, events = await service.archive_workflow(completed.id)
        assert archived.workflow_status == WorkflowStatus.ARCHIVED
        assert len(events) == 1

    async def test_reject_and_retry_flow(self, db_session: AsyncSession) -> None:
        complaint_repo = ComplaintRepository(session=db_session)
        workflow_repo = WorkflowRepository(session=db_session)
        service = WorkflowService(
            repository=workflow_repo,
            complaint_repository=complaint_repo,
        )

        complaint = await complaint_repo.create(
            title="Reject retry complaint",
            category=ComplaintCategory.GENERAL,
        )
        created, _ = await service.create_workflow(
            WorkflowCreate(complaint_id=complaint.id)
        )

        await service.update_workflow(
            created.id, WorkflowUpdate(workflow_stage=WorkflowStage.ASSIGNED)
        )
        await service.update_workflow(
            created.id, WorkflowUpdate(workflow_stage=WorkflowStage.IN_PROGRESS)
        )
        await service.update_workflow(
            created.id, WorkflowUpdate(workflow_stage=WorkflowStage.REVIEW)
        )
        await service.update_workflow(
            created.id, WorkflowUpdate(workflow_stage=WorkflowStage.APPROVAL)
        )
        rejector = uuid.uuid4()
        rejected, _ = await service.reject_workflow(
            created.id, rejected_by=rejector, reason="Needs more data"
        )
        assert rejected.approval_status == ApprovalStatus.REJECTED
        assert rejected.workflow_stage == WorkflowStage.REVIEW

    async def test_full_api_flow(self, client: AsyncClient) -> None:
        complaint_resp = await client.post(
            "/api/v1/complaints",
            json={"title": "API workflow flow", "category": "service"},
        )
        assert complaint_resp.status_code == 201
        complaint_id = complaint_resp.json()["data"]["id"]

        wf_resp = await client.post(
            "/api/v1/workflows",
            json={"complaint_id": complaint_id, "priority": "high"},
        )
        assert wf_resp.status_code == 201
        workflow_id = wf_resp.json()["data"]["id"]
        assert wf_resp.json()["data"]["complaint_id"] == complaint_id

        get_resp = await client.get(f"/api/v1/workflows/{workflow_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["priority"] == "high"

        agent_id = str(uuid.uuid4())
        assign_resp = await client.post(
            f"/api/v1/workflows/{workflow_id}/assign",
            json={"agent_id": agent_id, "team": "claims", "queue": "tier-1"},
        )
        assert assign_resp.status_code == 200
        assert assign_resp.json()["data"]["assigned_agent_id"] == agent_id

        escalate_resp = await client.post(
            f"/api/v1/workflows/{workflow_id}/escalate",
            json={"reason": "Escalating for review"},
        )
        assert escalate_resp.status_code == 200
        assert escalate_resp.json()["data"]["escalation_level"] == "level_1"

        list_resp = await client.get("/api/v1/workflows?workflow_status=active")
        assert list_resp.status_code == 200
        ids = [item["id"] for item in list_resp.json()["data"]]
        assert workflow_id in ids
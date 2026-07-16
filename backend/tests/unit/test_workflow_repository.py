"""Workflow repository unit tests."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from domains.complaint.constants.complaint_constants import ComplaintCategory
from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.workflow.constants.workflow_constants import (
    ApprovalStatus,
    EscalationLevel,
    SLAStatus,
    WorkflowStage,
    WorkflowStatus,
)
from domains.workflow.repositories.workflow_repository import WorkflowRepository


@pytest.fixture
async def repo(db_session: AsyncSession) -> WorkflowRepository:
    return WorkflowRepository(session=db_session)


@pytest.fixture
async def complaint(db_session: AsyncSession):
    return await ComplaintRepository(session=db_session).create(
        title="Workflow complaint",
        category=ComplaintCategory.SERVICE,
    )


@pytest.mark.asyncio
class TestWorkflowRepository:
    async def test_create_workflow(self, repo: WorkflowRepository, complaint) -> None:
        workflow = await repo.create(complaint_id=complaint.id)
        assert workflow.id is not None
        assert workflow.complaint_id == complaint.id
        assert workflow.workflow_status == WorkflowStatus.PENDING
        assert workflow.workflow_stage == WorkflowStage.INITIATED
        assert workflow.sla_status == SLAStatus.WITHIN_SLA
        assert workflow.escalation_level == EscalationLevel.LEVEL_0
        assert workflow.approval_status == ApprovalStatus.NOT_REQUIRED

    async def test_get_by_id_found(self, repo: WorkflowRepository, complaint) -> None:
        created = await repo.create(complaint_id=complaint.id)
        fetched = await repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.complaint_id == complaint.id

    async def test_get_by_id_not_found(self, repo: WorkflowRepository) -> None:
        fetched = await repo.get_by_id(uuid.uuid4())
        assert fetched is None

    async def test_update_workflow(self, repo: WorkflowRepository, complaint) -> None:
        created = await repo.create(complaint_id=complaint.id)
        updated = await repo.update(
            created.id,
            current_queue="tier-2",
            priority="high",
        )
        assert updated is not None
        assert updated.current_queue == "tier-2"
        assert updated.priority == "high"

    async def test_update_not_found(self, repo: WorkflowRepository) -> None:
        updated = await repo.update(uuid.uuid4(), priority="low")
        assert updated is None

    async def test_delete_workflow(self, repo: WorkflowRepository, complaint) -> None:
        created = await repo.create(complaint_id=complaint.id)
        result = await repo.delete(created.id)
        assert result is True
        fetched = await repo.get_by_id(created.id)
        assert fetched is None

    async def test_delete_not_found(self, repo: WorkflowRepository) -> None:
        result = await repo.delete(uuid.uuid4())
        assert result is False

    async def test_list_without_filters(
        self, repo: WorkflowRepository, complaint
    ) -> None:
        await repo.create(complaint_id=complaint.id)
        w2_id = await ComplaintRepository(session=repo._session).create(
            title="Second", category=ComplaintCategory.GENERAL
        )
        await repo.create(complaint_id=w2_id.id)
        items, total = await repo.list()
        assert total == 2
        assert len(items) == 2

    async def test_list_filters_by_status(
        self, repo: WorkflowRepository, complaint
    ) -> None:
        await repo.create(complaint_id=complaint.id)
        w2_id = await ComplaintRepository(session=repo._session).create(
            title="Second", category=ComplaintCategory.BILLING
        )
        await repo.create(complaint_id=w2_id.id, workflow_status=WorkflowStatus.COMPLETED)
        items, total = await repo.list(workflow_status=WorkflowStatus.PENDING)
        assert total == 1
        assert all(item.workflow_status == WorkflowStatus.PENDING for item in items)

    async def test_list_filters_by_stage(
        self, repo: WorkflowRepository, complaint
    ) -> None:
        await repo.create(complaint_id=complaint.id)
        w2_id = await ComplaintRepository(session=repo._session).create(
            title="Second", category=ComplaintCategory.CLAIMS
        )
        await repo.create(
            complaint_id=w2_id.id, workflow_stage=WorkflowStage.ASSIGNED
        )
        items, total = await repo.list(workflow_stage=WorkflowStage.INITIATED)
        assert total == 1
        assert all(item.workflow_stage == WorkflowStage.INITIATED for item in items)

    async def test_list_filters_by_team(
        self, repo: WorkflowRepository, complaint
    ) -> None:
        await repo.create(complaint_id=complaint.id, assigned_team="claims")
        w2_id = await ComplaintRepository(session=repo._session).create(
            title="Second", category=ComplaintCategory.TECHNICAL
        )
        await repo.create(complaint_id=w2_id.id, assigned_team="billing")
        items, total = await repo.list(assigned_team="claims")
        assert total == 1
        assert all(item.assigned_team == "claims" for item in items)

    async def test_list_filters_by_sla(
        self, repo: WorkflowRepository, complaint
    ) -> None:
        await repo.create(complaint_id=complaint.id)
        w2_id = await ComplaintRepository(session=repo._session).create(
            title="Second", category=ComplaintCategory.GENERAL
        )
        await repo.create(
            complaint_id=w2_id.id, sla_status=SLAStatus.BREACHED
        )
        items, total = await repo.list(sla_status=SLAStatus.WITHIN_SLA)
        assert total == 1
        assert all(item.sla_status == SLAStatus.WITHIN_SLA for item in items)

    async def test_list_filters_by_escalation(
        self, repo: WorkflowRepository, complaint
    ) -> None:
        await repo.create(complaint_id=complaint.id)
        w2_id = await ComplaintRepository(session=repo._session).create(
            title="Second", category=ComplaintCategory.GENERAL
        )
        await repo.create(
            complaint_id=w2_id.id, escalation_level=EscalationLevel.LEVEL_2
        )
        items, total = await repo.list(escalation_level=EscalationLevel.LEVEL_0)
        assert total == 1
        assert all(item.escalation_level == EscalationLevel.LEVEL_0 for item in items)

    async def test_list_pagination(self, repo: WorkflowRepository, complaint) -> None:
        for _ in range(5):
            c = await ComplaintRepository(session=repo._session).create(
                title=f"Complaint {uuid.uuid4()}", category=ComplaintCategory.GENERAL
            )
            await repo.create(complaint_id=c.id)
        page1, total = await repo.list(page=1, page_size=2)
        page2, _ = await repo.list(page=2, page_size=2)
        page3, _ = await repo.list(page=3, page_size=2)
        assert total == 5
        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1

    async def test_get_by_complaint_id(
        self, repo: WorkflowRepository, complaint
    ) -> None:
        w1 = await repo.create(complaint_id=complaint.id)
        w2_c = await ComplaintRepository(session=repo._session).create(
            title="Other", category=ComplaintCategory.GENERAL
        )
        await repo.create(complaint_id=w2_c.id)
        items = await repo.get_by_complaint_id(complaint.id)
        assert len(items) == 1
        assert items[0].id == w1.id

    async def test_get_active_by_complaint_id(
        self, repo: WorkflowRepository, complaint
    ) -> None:
        created = await repo.create(complaint_id=complaint.id)
        active = await repo.get_active_by_complaint_id(complaint.id)
        assert active is not None
        assert active.id == created.id
"""Workflow service unit tests."""

import uuid

import pytest

from domains.workflow.constants.workflow_constants import (
    ApprovalStatus,
    EscalationLevel,
    SLAStatus,
    WorkflowStage,
    WorkflowStatus,
)
from domains.workflow.events.workflow_events import (
    WorkflowApproved,
    WorkflowArchived,
    WorkflowAssigned,
    WorkflowCompleted,
    WorkflowEscalated,
    WorkflowRejected,
    WorkflowStarted,
)
from domains.workflow.exceptions.workflow_exceptions import (
    WorkflowNotFoundError,
    WorkflowValidationError,
)
from domains.workflow.schemas.workflow_schemas import WorkflowCreate, WorkflowUpdate
from domains.workflow.services.workflow_service import WorkflowService


@pytest.fixture
def active_workflow_kwargs() -> dict:
    return dict(
        id=uuid.uuid4(),
        complaint_id=uuid.uuid4(),
        current_queue=None,
        assigned_team=None,
        assigned_agent_id=None,
        workflow_status=WorkflowStatus.ACTIVE,
        workflow_stage=WorkflowStage.INITIATED,
        priority=None,
        sla_status=SLAStatus.WITHIN_SLA,
        escalation_level=EscalationLevel.LEVEL_0,
        approval_status=ApprovalStatus.NOT_REQUIRED,
        started_at=None,
        due_at=None,
        completed_at=None,
    )


@pytest.fixture
def completed_workflow_kwargs(active_workflow_kwargs: dict) -> dict:
    kwargs = dict(active_workflow_kwargs)
    kwargs["workflow_status"] = WorkflowStatus.COMPLETED
    kwargs["workflow_stage"] = WorkflowStage.COMPLETED
    return kwargs


@pytest.fixture
def archived_workflow_kwargs(active_workflow_kwargs: dict) -> dict:
    kwargs = dict(active_workflow_kwargs)
    kwargs["workflow_status"] = WorkflowStatus.ARCHIVED
    return kwargs


@pytest.fixture
async def service(mocker, active_workflow_kwargs: dict) -> WorkflowService:
    mock_repo = mocker.AsyncMock()
    mock_complaint_repo = mocker.AsyncMock()

    mock_repo.get_by_id.return_value = mocker.Mock(**active_workflow_kwargs)
    mock_repo.create.return_value = mocker.Mock(**active_workflow_kwargs)
    mock_repo.update.return_value = mocker.Mock(**active_workflow_kwargs)
    mock_repo.get_active_by_complaint_id.return_value = None
    mock_complaint_repo.get_by_id.return_value = object()

    return WorkflowService(
        repository=mock_repo,
        complaint_repository=mock_complaint_repo,
    )


@pytest.mark.asyncio
class TestWorkflowService:
    async def test_create_workflow_returns_entity_and_event(
        self,
        service: WorkflowService,
    ) -> None:
        data = WorkflowCreate(complaint_id=uuid.uuid4())
        service._repository.create.return_value.complaint_id = data.complaint_id
        workflow, events = await service.create_workflow(data)
        assert workflow is not None
        assert len(events) == 1
        assert isinstance(events[0], WorkflowStarted)
        assert events[0].complaint_id == data.complaint_id

    async def test_create_workflow_missing_complaint_raises(
        self,
        service: WorkflowService,
    ) -> None:
        service._complaint_repository.get_by_id.return_value = None
        data = WorkflowCreate(complaint_id=uuid.uuid4())
        with pytest.raises(WorkflowValidationError):
            await service.create_workflow(data)

    async def test_create_workflow_duplicate_active_raises(
        self,
        service: WorkflowService,
        mocker,
        active_workflow_kwargs: dict,
    ) -> None:
        service._repository.get_active_by_complaint_id.return_value = mocker.Mock(**active_workflow_kwargs)
        data = WorkflowCreate(complaint_id=uuid.uuid4())
        with pytest.raises(WorkflowValidationError):
            await service.create_workflow(data)

    async def test_get_workflow_found(
        self,
        service: WorkflowService,
    ) -> None:
        workflow = await service.get_workflow(uuid.uuid4())
        assert workflow is not None
        assert workflow.workflow_status == WorkflowStatus.ACTIVE

    async def test_get_workflow_not_found_raises(
        self,
        service: WorkflowService,
    ) -> None:
        service._repository.get_by_id.return_value = None
        with pytest.raises(WorkflowNotFoundError):
            await service.get_workflow(uuid.uuid4())

    async def test_list_workflows(
        self,
        service: WorkflowService,
    ) -> None:
        service._repository.list.return_value = ([], 0)
        items, total = await service.list_workflows()
        assert items == []
        assert total == 0

    async def test_assign_workflow_returns_entity_and_event(
        self,
        service: WorkflowService,
    ) -> None:
        agent_id = uuid.uuid4()
        workflow, events = await service.assign_workflow(
            uuid.uuid4(), agent_id=agent_id, team="claims", queue="tier-2"
        )
        assert workflow is not None
        assert len(events) == 1
        assert isinstance(events[0], WorkflowAssigned)
        assert events[0].assigned_agent_id == agent_id
        assert events[0].assigned_team == "claims"
        assert events[0].queue == "tier-2"

    async def test_assign_archived_workflow_raises(
        self,
        service: WorkflowService,
        mocker,
        archived_workflow_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**archived_workflow_kwargs)
        with pytest.raises(WorkflowValidationError):
            await service.assign_workflow(uuid.uuid4(), agent_id=uuid.uuid4())

    async def test_transfer_workflow_returns_entity_and_event(
        self,
        service: WorkflowService,
        mocker,
        active_workflow_kwargs: dict,
    ) -> None:
        kwargs = dict(active_workflow_kwargs)
        kwargs["assigned_agent_id"] = uuid.uuid4()
        service._repository.get_by_id.return_value = mocker.Mock(**kwargs)
        new_agent = uuid.uuid4()
        workflow, events = await service.transfer_workflow(
            uuid.uuid4(), agent_id=new_agent, team="billing"
        )
        assert workflow is not None
        assert len(events) == 1
        assert isinstance(events[0], WorkflowAssigned)

    async def test_transfer_unassigned_workflow_raises(
        self,
        service: WorkflowService,
    ) -> None:
        service._repository.get_by_id.return_value.assigned_agent_id = None
        with pytest.raises(WorkflowValidationError):
            await service.transfer_workflow(uuid.uuid4(), agent_id=uuid.uuid4())

    async def test_escalate_workflow_returns_entity_and_event(
        self,
        service: WorkflowService,
        mocker,
        active_workflow_kwargs: dict,
    ) -> None:
        workflow, events = await service.escalate_workflow(uuid.uuid4(), reason="Urgent")
        assert len(events) == 1
        assert isinstance(events[0], WorkflowEscalated)
        assert events[0].reason == "Urgent"
        assert events[0].escalation_level == EscalationLevel.LEVEL_1.value

    async def test_escalate_max_level_raises(
        self,
        service: WorkflowService,
        mocker,
        active_workflow_kwargs: dict,
    ) -> None:
        kwargs = dict(active_workflow_kwargs)
        kwargs["escalation_level"] = EscalationLevel.LEVEL_3
        service._repository.get_by_id.return_value = mocker.Mock(**kwargs)
        with pytest.raises(WorkflowValidationError):
            await service.escalate_workflow(uuid.uuid4())

    async def test_escalate_completed_workflow_raises(
        self,
        service: WorkflowService,
        mocker,
        completed_workflow_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**completed_workflow_kwargs)
        with pytest.raises(WorkflowValidationError):
            await service.escalate_workflow(uuid.uuid4())

    async def test_approve_workflow_returns_entity_and_event(
        self,
        service: WorkflowService,
        mocker,
        active_workflow_kwargs: dict,
    ) -> None:
        kwargs = dict(active_workflow_kwargs)
        kwargs["approval_status"] = ApprovalStatus.PENDING
        service._repository.get_by_id.return_value = mocker.Mock(**kwargs)
        approver = uuid.uuid4()
        workflow, events = await service.approve_workflow(uuid.uuid4(), approved_by=approver)
        assert len(events) == 1
        assert isinstance(events[0], WorkflowApproved)
        assert events[0].approved_by == approver

    async def test_approve_already_approved_raises(
        self,
        service: WorkflowService,
        mocker,
        active_workflow_kwargs: dict,
    ) -> None:
        kwargs = dict(active_workflow_kwargs)
        kwargs["approval_status"] = ApprovalStatus.APPROVED
        service._repository.get_by_id.return_value = mocker.Mock(**kwargs)
        with pytest.raises(WorkflowValidationError):
            await service.approve_workflow(uuid.uuid4(), approved_by=uuid.uuid4())

    async def test_reject_workflow_returns_entity_and_event(
        self,
        service: WorkflowService,
        mocker,
        active_workflow_kwargs: dict,
    ) -> None:
        kwargs = dict(active_workflow_kwargs)
        kwargs["approval_status"] = ApprovalStatus.PENDING
        service._repository.get_by_id.return_value = mocker.Mock(**kwargs)
        rejector = uuid.uuid4()
        workflow, events = await service.reject_workflow(
            uuid.uuid4(), rejected_by=rejector, reason="Insufficient info"
        )
        assert len(events) == 1
        assert isinstance(events[0], WorkflowRejected)
        assert events[0].rejected_by == rejector
        assert events[0].reason == "Insufficient info"

    async def test_reject_already_rejected_raises(
        self,
        service: WorkflowService,
        mocker,
        active_workflow_kwargs: dict,
    ) -> None:
        kwargs = dict(active_workflow_kwargs)
        kwargs["approval_status"] = ApprovalStatus.REJECTED
        service._repository.get_by_id.return_value = mocker.Mock(**kwargs)
        with pytest.raises(WorkflowValidationError):
            await service.reject_workflow(uuid.uuid4(), rejected_by=uuid.uuid4())

    async def test_complete_workflow_returns_entity_and_event(
        self,
        service: WorkflowService,
        mocker,
        active_workflow_kwargs: dict,
    ) -> None:
        kwargs = dict(active_workflow_kwargs)
        kwargs["approval_status"] = ApprovalStatus.APPROVED
        service._repository.get_by_id.return_value = mocker.Mock(**kwargs)
        workflow, events = await service.complete_workflow(uuid.uuid4())
        assert len(events) == 1
        assert isinstance(events[0], WorkflowCompleted)
        assert events[0].complaint_id == workflow.complaint_id

    async def test_complete_without_approval_raises(
        self,
        service: WorkflowService,
    ) -> None:
        service._repository.get_by_id.return_value.approval_status = ApprovalStatus.PENDING
        with pytest.raises(WorkflowValidationError):
            await service.complete_workflow(uuid.uuid4())

    async def test_complete_archived_workflow_raises(
        self,
        service: WorkflowService,
        mocker,
        archived_workflow_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**archived_workflow_kwargs)
        with pytest.raises(WorkflowValidationError):
            await service.complete_workflow(uuid.uuid4())

    async def test_archive_completed_workflow_returns_entity_and_event(
        self,
        service: WorkflowService,
        mocker,
        completed_workflow_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**completed_workflow_kwargs)
        workflow, events = await service.archive_workflow(uuid.uuid4())
        assert len(events) == 1
        assert isinstance(events[0], WorkflowArchived)

    async def test_archive_active_workflow_raises(
        self,
        service: WorkflowService,
    ) -> None:
        with pytest.raises(WorkflowValidationError):
            await service.archive_workflow(uuid.uuid4())

    async def test_archive_archived_workflow_raises(
        self,
        service: WorkflowService,
        mocker,
        archived_workflow_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**archived_workflow_kwargs)
        with pytest.raises(WorkflowValidationError):
            await service.archive_workflow(uuid.uuid4())

    async def test_logging_integration_on_create(
        self,
        service: WorkflowService,
        mocker,
    ) -> None:
        service._logger = mocker.Mock()
        data = WorkflowCreate(complaint_id=uuid.uuid4())
        await service.create_workflow(data)
        assert service._logger.info.call_count == 2

    async def test_invalid_stage_transition_raises(
        self,
        service: WorkflowService,
        mocker,
        active_workflow_kwargs: dict,
    ) -> None:
        data = WorkflowUpdate(workflow_stage=WorkflowStage.COMPLETED)
        with pytest.raises(WorkflowValidationError):
            await service.update_workflow(uuid.uuid4(), data)
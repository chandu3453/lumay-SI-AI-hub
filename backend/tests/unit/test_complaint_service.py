"""Complaint service unit tests."""

import uuid

import pytest

from domains.complaint.constants.complaint_constants import (
    ComplaintCategory,
    ComplaintPriority,
    ComplaintSeverity,
    ComplaintStatus,
)
from domains.complaint.events.complaint_events import (
    ComplaintArchivedEvent,
    ComplaintAssignedEvent,
    ComplaintClosedEvent,
    ComplaintCreatedEvent,
    ComplaintEscalatedEvent,
    ComplaintResolvedEvent,
    ComplaintUpdatedEvent,
)
from domains.complaint.exceptions.complaint_exceptions import (
    ComplaintNotFoundError,
    ComplaintValidationError,
)
from domains.complaint.schemas.complaint_schemas import (
    ComplaintCreate,
    ComplaintUpdate,
)
from domains.complaint.services.complaint_service import ComplaintService


@pytest.fixture
def submitted_complaint_kwargs() -> dict:
    return dict(
        id=uuid.uuid4(),
        title="Claim dispute",
        description="Investigation needed",
        category=ComplaintCategory.CLAIMS,
        priority=ComplaintPriority.MEDIUM,
        severity=ComplaintSeverity.MODERATE,
        status=ComplaintStatus.SUBMITTED,
        assigned_queue=None,
        assigned_agent_id=None,
        resolution_summary=None,
        closure_reason=None,
    )


@pytest.fixture
def closed_complaint_kwargs(submitted_complaint_kwargs: dict) -> dict:
    kwargs = dict(submitted_complaint_kwargs)
    kwargs["status"] = ComplaintStatus.CLOSED
    return kwargs


@pytest.fixture
def archived_complaint_kwargs(submitted_complaint_kwargs: dict) -> dict:
    kwargs = dict(submitted_complaint_kwargs)
    kwargs["status"] = ComplaintStatus.ARCHIVED
    return kwargs


@pytest.fixture
async def service(mocker, submitted_complaint_kwargs: dict) -> ComplaintService:
    mock_repo = mocker.AsyncMock()
    mock_customer_repo = mocker.AsyncMock()
    mock_interaction_repo = mocker.AsyncMock()

    mock_repo.get_by_id.return_value = mocker.Mock(**submitted_complaint_kwargs)
    mock_repo.create.return_value = mocker.Mock(**submitted_complaint_kwargs)
    mock_repo.update.return_value = mocker.Mock(**submitted_complaint_kwargs)
    mock_customer_repo.get_by_id.return_value = None
    mock_interaction_repo.get_by_id.return_value = None

    return ComplaintService(
        repository=mock_repo,
        customer_repository=mock_customer_repo,
        interaction_repository=mock_interaction_repo,
    )


@pytest.mark.asyncio
class TestComplaintService:
    async def test_create_complaint_returns_entity_and_event(
        self,
        service: ComplaintService,
    ) -> None:
        customer_id = uuid.uuid4()
        interaction_id = uuid.uuid4()
        service._customer_repository.get_by_id.return_value = object()
        service._interaction_repository.get_by_id.return_value = object()
        data = ComplaintCreate(
            customer_id=customer_id,
            interaction_id=interaction_id,
            title="Complaint created",
            category=ComplaintCategory.CLAIMS,
        )

        complaint, events = await service.create_complaint(data)

        assert complaint is not None
        assert len(events) == 1
        assert isinstance(events[0], ComplaintCreatedEvent)
        assert events[0].complaint_id == complaint.id
        assert events[0].customer_id == customer_id
        assert events[0].category == ComplaintCategory.CLAIMS

    async def test_create_complaint_without_customer_keeps_event_unlinked(
        self,
        service: ComplaintService,
    ) -> None:
        data = ComplaintCreate(
            title="Anonymous complaint",
            category=ComplaintCategory.GENERAL,
        )

        _, events = await service.create_complaint(data)

        assert events[0].customer_id is None

    async def test_create_complaint_missing_customer_raises(
        self,
        service: ComplaintService,
    ) -> None:
        data = ComplaintCreate(
            customer_id=uuid.uuid4(),
            title="Invalid customer",
            category=ComplaintCategory.GENERAL,
        )

        with pytest.raises(ComplaintValidationError):
            await service.create_complaint(data)

    async def test_create_complaint_missing_interaction_raises(
        self,
        service: ComplaintService,
    ) -> None:
        data = ComplaintCreate(
            interaction_id=uuid.uuid4(),
            title="Invalid interaction",
            category=ComplaintCategory.GENERAL,
        )

        with pytest.raises(ComplaintValidationError):
            await service.create_complaint(data)

    async def test_get_complaint_found(
        self,
        service: ComplaintService,
    ) -> None:
        complaint = await service.get_complaint(uuid.uuid4())
        assert complaint is not None
        assert complaint.title == "Claim dispute"

    async def test_get_complaint_not_found_raises(
        self,
        service: ComplaintService,
    ) -> None:
        service._repository.get_by_id.return_value = None
        with pytest.raises(ComplaintNotFoundError):
            await service.get_complaint(uuid.uuid4())

    async def test_list_complaints(
        self,
        service: ComplaintService,
    ) -> None:
        service._repository.list.return_value = ([], 0)
        items, total = await service.list_complaints()
        assert items == []
        assert total == 0

    async def test_update_complaint_returns_entity_and_event(
        self,
        service: ComplaintService,
    ) -> None:
        data = ComplaintUpdate(title="Updated title")
        complaint, events = await service.update_complaint(uuid.uuid4(), data)
        assert complaint is not None
        assert len(events) == 1
        assert isinstance(events[0], ComplaintUpdatedEvent)

    async def test_update_complaint_invalid_transition_raises(
        self,
        service: ComplaintService,
    ) -> None:
        data = ComplaintUpdate(status=ComplaintStatus.UNDER_REVIEW)
        service._repository.get_by_id.return_value.status = ComplaintStatus.RESOLVED
        with pytest.raises(ComplaintValidationError):
            await service.update_complaint(uuid.uuid4(), data)

    async def test_update_closed_complaint_raises(
        self,
        service: ComplaintService,
        mocker,
        closed_complaint_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**closed_complaint_kwargs)
        with pytest.raises(ComplaintValidationError):
            await service.update_complaint(uuid.uuid4(), ComplaintUpdate(title="Nope"))

    async def test_assign_complaint_returns_entity_and_event(
        self,
        service: ComplaintService,
    ) -> None:
        agent_id = uuid.uuid4()
        complaint, events = await service.assign_complaint(
            uuid.uuid4(),
            agent_id=agent_id,
            queue="tier-2",
        )
        assert complaint is not None
        assert len(events) == 1
        assert isinstance(events[0], ComplaintAssignedEvent)
        assert events[0].agent_id == agent_id
        assert events[0].queue == "tier-2"

    async def test_assign_archived_complaint_raises(
        self,
        service: ComplaintService,
        mocker,
        archived_complaint_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**archived_complaint_kwargs)
        with pytest.raises(ComplaintValidationError):
            await service.assign_complaint(uuid.uuid4(), agent_id=uuid.uuid4())

    async def test_escalate_complaint_returns_entity_and_event(
        self,
        service: ComplaintService,
        mocker,
        submitted_complaint_kwargs: dict,
    ) -> None:
        service._repository.update.return_value = mocker.Mock(
            **{**submitted_complaint_kwargs, "status": ComplaintStatus.ESCALATED}
        )
        complaint, events = await service.escalate_complaint(uuid.uuid4(), reason="Urgent")
        assert complaint.status == ComplaintStatus.ESCALATED
        assert len(events) == 1
        assert isinstance(events[0], ComplaintEscalatedEvent)
        assert events[0].reason == "Urgent"

    async def test_escalate_resolved_complaint_raises(
        self,
        service: ComplaintService,
        mocker,
        submitted_complaint_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            **{**submitted_complaint_kwargs, "status": ComplaintStatus.RESOLVED}
        )
        with pytest.raises(ComplaintValidationError):
            await service.escalate_complaint(uuid.uuid4())

    async def test_resolve_complaint_returns_entity_and_event(
        self,
        service: ComplaintService,
        mocker,
        submitted_complaint_kwargs: dict,
    ) -> None:
        service._repository.update.return_value = mocker.Mock(
            **{
                **submitted_complaint_kwargs,
                "status": ComplaintStatus.RESOLVED,
                "resolution_summary": "Handled",
            }
        )
        complaint, events = await service.resolve_complaint(
            uuid.uuid4(),
            resolution_summary="Handled",
        )
        assert complaint.status == ComplaintStatus.RESOLVED
        assert len(events) == 1
        assert isinstance(events[0], ComplaintResolvedEvent)
        assert events[0].resolution_summary == "Handled"

    async def test_resolve_archived_complaint_raises(
        self,
        service: ComplaintService,
        mocker,
        archived_complaint_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**archived_complaint_kwargs)
        with pytest.raises(ComplaintValidationError):
            await service.resolve_complaint(uuid.uuid4())

    async def test_close_complaint_returns_entity_and_event(
        self,
        service: ComplaintService,
        mocker,
        submitted_complaint_kwargs: dict,
    ) -> None:
        service._repository.update.return_value = mocker.Mock(
            **{
                **submitted_complaint_kwargs,
                "status": ComplaintStatus.CLOSED,
                "closure_reason": "Confirmed complete",
            }
        )
        complaint, events = await service.close_complaint(
            uuid.uuid4(),
            closure_reason="Confirmed complete",
        )
        assert complaint.status == ComplaintStatus.CLOSED
        assert len(events) == 1
        assert isinstance(events[0], ComplaintClosedEvent)
        assert events[0].closure_reason == "Confirmed complete"

    async def test_close_already_closed_complaint_raises(
        self,
        service: ComplaintService,
        mocker,
        closed_complaint_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**closed_complaint_kwargs)
        with pytest.raises(ComplaintValidationError):
            await service.close_complaint(uuid.uuid4())

    async def test_archive_complaint_returns_entity_and_event(
        self,
        service: ComplaintService,
        mocker,
        submitted_complaint_kwargs: dict,
    ) -> None:
        service._repository.update.return_value = mocker.Mock(
            **{**submitted_complaint_kwargs, "status": ComplaintStatus.ARCHIVED}
        )
        complaint, events = await service.archive_complaint(uuid.uuid4())
        assert complaint.status == ComplaintStatus.ARCHIVED
        assert len(events) == 1
        assert isinstance(events[0], ComplaintArchivedEvent)

    async def test_archive_archived_complaint_raises(
        self,
        service: ComplaintService,
        mocker,
        archived_complaint_kwargs: dict,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(**archived_complaint_kwargs)
        with pytest.raises(ComplaintValidationError):
            await service.archive_complaint(uuid.uuid4())

    async def test_logging_integration_on_create(
        self,
        service: ComplaintService,
        mocker,
    ) -> None:
        service._logger = mocker.Mock()
        data = ComplaintCreate(
            title="Logged complaint",
            category=ComplaintCategory.SERVICE,
        )

        await service.create_complaint(data)

        assert service._logger.info.call_count == 2


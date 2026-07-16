"""Interaction service unit tests."""

import uuid

import pytest

from domains.interaction.constants.interaction_constants import (
    InteractionChannel,
    InteractionDirection,
    InteractionStatus,
)
from domains.interaction.events.interaction_events import (
    InteractionArchivedEvent,
    InteractionCompletedEvent,
    InteractionReceivedEvent,
    InteractionUpdatedEvent,
)
from domains.interaction.exceptions.interaction_exceptions import (
    InteractionAlreadyProcessedError,
    InteractionNotFoundError,
    InvalidInteractionChannelError,
)
from domains.interaction.schemas.interaction_schemas import (
    InteractionCreate,
    InteractionUpdate,
)
from domains.interaction.services.interaction_service import InteractionService


@pytest.fixture
async def service(mocker) -> InteractionService:
    mock_repo = mocker.AsyncMock()
    mock_repo.create.return_value = mocker.Mock(
        id=uuid.uuid4(), channel=InteractionChannel.EMAIL,
        direction=InteractionDirection.INBOUND, status=InteractionStatus.RECEIVED,
        customer_ref=None, subject=None, transcript=None, attachments=None,
        created_at=None, updated_at=None,
    )
    mock_repo.get_by_id.return_value = mocker.Mock(
        id=uuid.uuid4(), channel=InteractionChannel.VOICE,
        direction=InteractionDirection.INBOUND, status=InteractionStatus.RECEIVED,
        customer_ref=None, subject=None, transcript=None, attachments=None,
        created_at=None, updated_at=None,
    )
    mock_repo.update.return_value = mocker.Mock(
        id=uuid.uuid4(), channel=InteractionChannel.VOICE,
        direction=InteractionDirection.INBOUND, status=InteractionStatus.COMPLETED,
        customer_ref=None, subject=None, transcript=None, attachments=None,
        created_at=None, updated_at=None,
    )
    return InteractionService(repository=mock_repo)


@pytest.mark.asyncio
class TestInteractionService:
    async def test_create_interaction_returns_entity_and_event(
        self, service: InteractionService,
    ) -> None:
        data = InteractionCreate(channel=InteractionChannel.EMAIL)
        interaction, events = await service.create_interaction(data)
        assert interaction is not None
        assert len(events) == 1
        assert isinstance(events[0], InteractionReceivedEvent)

    async def test_get_interaction_found(self, service: InteractionService) -> None:
        interaction = await service.get_interaction(uuid.uuid4())
        assert interaction is not None

    async def test_get_interaction_not_found_raises(
        self, service: InteractionService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = None
        with pytest.raises(InteractionNotFoundError):
            await service.get_interaction(uuid.uuid4())

    async def test_update_interaction_returns_entity_and_event(
        self, service: InteractionService,
    ) -> None:
        data = InteractionUpdate(subject="New subject")
        interaction, events = await service.update_interaction(uuid.uuid4(), data)
        assert interaction is not None
        assert len(events) == 1
        assert isinstance(events[0], InteractionUpdatedEvent)

    async def test_update_archived_interaction_raises(
        self, service: InteractionService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            status=InteractionStatus.ARCHIVED,
            id=uuid.uuid4(), channel=InteractionChannel.VOICE,
        )
        data = InteractionUpdate(subject="Nope")
        with pytest.raises(InteractionAlreadyProcessedError):
            await service.update_interaction(uuid.uuid4(), data)

    async def test_update_completed_interaction_raises(
        self, service: InteractionService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            status=InteractionStatus.COMPLETED,
            id=uuid.uuid4(), channel=InteractionChannel.VOICE,
        )
        data = InteractionUpdate(subject="Nope")
        with pytest.raises(InteractionAlreadyProcessedError):
            await service.update_interaction(uuid.uuid4(), data)

    async def test_update_failed_interaction_raises(
        self, service: InteractionService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            status=InteractionStatus.FAILED,
            id=uuid.uuid4(), channel=InteractionChannel.VOICE,
        )
        data = InteractionUpdate(subject="Nope")
        with pytest.raises(InteractionAlreadyProcessedError):
            await service.update_interaction(uuid.uuid4(), data)

    async def test_update_invalid_status_transition_raises(
        self, service: InteractionService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            status=InteractionStatus.RECEIVED,
            id=uuid.uuid4(), channel=InteractionChannel.VOICE,
        )
        data = InteractionUpdate(status=InteractionStatus.LINKED)
        with pytest.raises(InvalidInteractionChannelError):
            await service.update_interaction(uuid.uuid4(), data)

    async def test_close_interaction_returns_entity_and_event(
        self, service: InteractionService,
    ) -> None:
        interaction, events = await service.close_interaction(uuid.uuid4())
        assert interaction is not None
        assert len(events) == 1
        assert isinstance(events[0], InteractionCompletedEvent)

    async def test_close_already_completed_raises(
        self, service: InteractionService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            status=InteractionStatus.COMPLETED,
            id=uuid.uuid4(), channel=InteractionChannel.VOICE,
        )
        with pytest.raises(InteractionAlreadyProcessedError):
            await service.close_interaction(uuid.uuid4())

    async def test_archive_interaction_returns_entity_and_event(
        self, service: InteractionService,
    ) -> None:
        interaction, events = await service.archive_interaction(uuid.uuid4())
        assert interaction is not None
        assert len(events) == 1
        assert isinstance(events[0], InteractionArchivedEvent)

    async def test_archive_already_archived_raises(
        self, service: InteractionService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            status=InteractionStatus.ARCHIVED,
            id=uuid.uuid4(), channel=InteractionChannel.VOICE,
        )
        with pytest.raises(InteractionAlreadyProcessedError):
            await service.archive_interaction(uuid.uuid4())

    async def test_list_interactions(self, service: InteractionService) -> None:
        service._repository.list.return_value = ([], 0)
        items, total = await service.list_interactions()
        assert items == []
        assert total == 0

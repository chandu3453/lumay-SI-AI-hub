"""Interaction domain service — business orchestration layer."""

import uuid
from collections.abc import Sequence

from domains.interaction.constants.interaction_constants import InteractionStatus
from domains.interaction.events.interaction_events import (
    DomainEvent,
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
from domains.interaction.models.interaction import Interaction
from domains.interaction.repositories.interaction_repository import InteractionRepository
from domains.interaction.schemas.interaction_schemas import InteractionCreate, InteractionUpdate
from app.platform.logging import get_logger
from shared.base_service import BaseService

_ALLOWED_TRANSITIONS: dict[InteractionStatus, set[InteractionStatus]] = {
    InteractionStatus.RECEIVED: {
        InteractionStatus.PROCESSING,
        InteractionStatus.COMPLETED,
        InteractionStatus.FAILED,
        InteractionStatus.ARCHIVED,
    },
    InteractionStatus.PROCESSING: {
        InteractionStatus.CLASSIFIED,
        InteractionStatus.FAILED,
        InteractionStatus.ARCHIVED,
    },
    InteractionStatus.CLASSIFIED: {
        InteractionStatus.LINKED,
        InteractionStatus.FAILED,
        InteractionStatus.ARCHIVED,
    },
    InteractionStatus.LINKED: {
        InteractionStatus.COMPLETED,
        InteractionStatus.FAILED,
        InteractionStatus.ARCHIVED,
    },
    InteractionStatus.COMPLETED: {
        InteractionStatus.ARCHIVED,
    },
    InteractionStatus.FAILED: set(),
    InteractionStatus.ARCHIVED: set(),
}

_IMMUTABLE_STATUSES = {
    InteractionStatus.COMPLETED,
    InteractionStatus.FAILED,
    InteractionStatus.ARCHIVED,
}


class InteractionService(BaseService):
    def __init__(self, repository: InteractionRepository) -> None:
        self._repository = repository
        self._logger = get_logger(__name__)

    async def create_interaction(
        self, data: InteractionCreate
    ) -> tuple[Interaction, list[DomainEvent]]:
        self._logger.info("interaction_create_requested", channel=data.channel)
        interaction = await self._repository.create(**data.model_dump())
        events: list[DomainEvent] = [
            InteractionReceivedEvent(interaction_id=interaction.id)
        ]
        self._logger.info(
            "interaction_created",
            interaction_id=str(interaction.id),
            channel=interaction.channel,
        )
        return interaction, events

    async def get_interaction(self, interaction_id: uuid.UUID) -> Interaction:
        interaction = await self._repository.get_by_id(interaction_id)
        if interaction is None:
            raise InteractionNotFoundError(
                context={"interaction_id": str(interaction_id)}
            )
        return interaction

    async def list_interactions(
        self,
        *,
        channel=None,
        status=None,
        direction=None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[Interaction], int]:
        self._logger.debug(
            "interaction_list_requested",
            channel=channel,
            status=status,
            direction=direction,
            page=page,
            page_size=page_size,
        )
        return await self._repository.list(
            channel=channel,
            status=status,
            direction=direction,
            page=page,
            page_size=page_size,
        )

    async def update_interaction(
        self, interaction_id: uuid.UUID, data: InteractionUpdate
    ) -> tuple[Interaction, list[DomainEvent]]:
        interaction = await self.get_interaction(interaction_id)
        self._assert_mutable(interaction)

        new_status = data.status
        if new_status is not None and new_status != interaction.status:
            self._validate_transition(interaction.status, new_status)

        updated = await self._repository.update(
            interaction_id, **data.model_dump(exclude_none=True)
        )
        events: list[DomainEvent] = [
            InteractionUpdatedEvent(interaction_id=interaction.id)
        ]
        self._logger.info(
            "interaction_updated",
            interaction_id=str(interaction_id),
        )
        return updated, events

    async def close_interaction(
        self, interaction_id: uuid.UUID
    ) -> tuple[Interaction, list[DomainEvent]]:
        interaction = await self.get_interaction(interaction_id)

        if interaction.status == InteractionStatus.COMPLETED:
            raise InteractionAlreadyProcessedError(
                context={"interaction_id": str(interaction_id)},
            )

        self._validate_transition(interaction.status, InteractionStatus.COMPLETED)

        updated = await self._repository.update(
            interaction_id, status=InteractionStatus.COMPLETED
        )
        events: list[DomainEvent] = [
            InteractionCompletedEvent(interaction_id=interaction.id)
        ]
        self._logger.info(
            "interaction_completed",
            interaction_id=str(interaction_id),
        )
        return updated, events

    async def archive_interaction(
        self, interaction_id: uuid.UUID
    ) -> tuple[Interaction, list[DomainEvent]]:
        interaction = await self.get_interaction(interaction_id)

        if interaction.status == InteractionStatus.ARCHIVED:
            raise InteractionAlreadyProcessedError(
                message="Interaction is already archived.",
                context={"interaction_id": str(interaction_id)},
            )

        self._validate_transition(interaction.status, InteractionStatus.ARCHIVED)

        updated = await self._repository.update(
            interaction_id, status=InteractionStatus.ARCHIVED
        )
        events: list[DomainEvent] = [
            InteractionArchivedEvent(interaction_id=interaction.id)
        ]
        self._logger.info(
            "interaction_archived",
            interaction_id=str(interaction_id),
        )
        return updated, events

    def _assert_mutable(self, interaction: Interaction) -> None:
        if interaction.status in _IMMUTABLE_STATUSES:
            raise InteractionAlreadyProcessedError(
                message=f"Cannot modify interaction in status '{interaction.status}'.",
                context={
                    "interaction_id": str(interaction.id),
                    "current_status": interaction.status,
                },
            )

    @staticmethod
    def _validate_transition(
        current: InteractionStatus, target: InteractionStatus
    ) -> None:
        allowed = _ALLOWED_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise InvalidInteractionChannelError(
                message=f"Cannot transition from '{current}' to '{target}'.",
                context={
                    "current_status": current,
                    "target_status": target,
                },
            )

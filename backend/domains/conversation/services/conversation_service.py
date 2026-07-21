"""Conversation domain service — centralizes the conversation lifecycle state machine."""

import uuid
from collections.abc import Sequence
from datetime import datetime

from domains.conversation.constants.conversation_constants import (
    ConversationPriority,
    ConversationStatus,
)
from domains.conversation.events.conversation_events import (
    ConversationAssignedEvent,
    ConversationClosedEvent,
    ConversationCreatedEvent,
    ConversationStatusChangedEvent,
    DomainEvent,
)
from domains.conversation.exceptions.conversation_exceptions import (
    ConversationNotFoundError,
    InvalidConversationTransitionError,
)
from domains.conversation.models.conversation import Conversation
from domains.conversation.repositories.conversation_repository import ConversationRepository
from domains.conversation.schemas.conversation_schemas import ConversationCreate
from app.platform.logging import get_logger
from shared.base_service import BaseService

_ALLOWED_TRANSITIONS: dict[ConversationStatus, set[ConversationStatus]] = {
    ConversationStatus.NEW: {
        ConversationStatus.ACTIVE,
        ConversationStatus.AI_HANDLING,
        ConversationStatus.HUMAN_HANDLING,  # employee takes over before any AI turn
        ConversationStatus.CLOSED,
    },
    ConversationStatus.ACTIVE: {
        ConversationStatus.WAITING_FOR_CUSTOMER,
        ConversationStatus.WAITING_FOR_AGENT,
        ConversationStatus.AI_HANDLING,
        ConversationStatus.HUMAN_HANDLING,
        ConversationStatus.ESCALATED,
        ConversationStatus.RESOLVED,
        ConversationStatus.CLOSED,
    },
    ConversationStatus.WAITING_FOR_CUSTOMER: {
        ConversationStatus.ACTIVE,
        ConversationStatus.AI_HANDLING,
        ConversationStatus.HUMAN_HANDLING,
        ConversationStatus.ESCALATED,
        ConversationStatus.RESOLVED,
        ConversationStatus.CLOSED,
    },
    ConversationStatus.WAITING_FOR_AGENT: {
        ConversationStatus.ACTIVE,
        ConversationStatus.HUMAN_HANDLING,
        ConversationStatus.ESCALATED,
        ConversationStatus.RESOLVED,
        ConversationStatus.CLOSED,
    },
    ConversationStatus.AI_HANDLING: {
        ConversationStatus.WAITING_FOR_CUSTOMER,
        ConversationStatus.HUMAN_HANDLING,
        ConversationStatus.ESCALATED,
        ConversationStatus.RESOLVED,
        ConversationStatus.CLOSED,
    },
    ConversationStatus.HUMAN_HANDLING: {
        ConversationStatus.WAITING_FOR_CUSTOMER,
        ConversationStatus.WAITING_FOR_AGENT,
        ConversationStatus.AI_HANDLING,  # employee releases back to AI
        ConversationStatus.ESCALATED,
        ConversationStatus.RESOLVED,
        ConversationStatus.CLOSED,
    },
    ConversationStatus.ESCALATED: {
        ConversationStatus.HUMAN_HANDLING,
        ConversationStatus.RESOLVED,
        ConversationStatus.CLOSED,
    },
    ConversationStatus.RESOLVED: {
        ConversationStatus.CLOSED,
        ConversationStatus.ACTIVE,  # reopen
    },
    ConversationStatus.CLOSED: {
        ConversationStatus.ACTIVE,  # reopen (Phase 3 — "Reopen Conversation" employee action)
    },
}

# Entering these statuses auto-sets the ai_handling/human_handling flags.
_HANDLING_FLAGS: dict[ConversationStatus, tuple[bool, bool]] = {
    ConversationStatus.AI_HANDLING: (True, False),
    ConversationStatus.HUMAN_HANDLING: (False, True),
}


class ConversationService(BaseService):
    def __init__(self, repository: ConversationRepository) -> None:
        self._repository = repository
        self._logger = get_logger(__name__)

    async def create_conversation(
        self, data: ConversationCreate
    ) -> tuple[Conversation, list[DomainEvent]]:
        conversation = await self._repository.create(**data.model_dump())
        events: list[DomainEvent] = [
            ConversationCreatedEvent(
                conversation_id=conversation.id,
                customer_id=conversation.customer_id,
                channel=conversation.current_channel,
            )
        ]
        self._logger.info(
            "conversation_created",
            conversation_id=str(conversation.id),
            channel=conversation.current_channel,
        )
        return conversation, events

    async def get_conversation(self, conversation_id: uuid.UUID) -> Conversation:
        conversation = await self._repository.get_by_id(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(context={"conversation_id": str(conversation_id)})
        return conversation

    async def get_by_complaint_id(self, complaint_id: uuid.UUID) -> Conversation | None:
        return await self._repository.get_by_complaint_id(complaint_id)

    async def list_conversations(
        self,
        *,
        customer_id=None,
        status=None,
        channel=None,
        assigned_employee_id: uuid.UUID | None = None,
        complaint_id: uuid.UUID | None = None,
        priority: ConversationPriority | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[Conversation], int]:
        return await self._repository.list(
            customer_id=customer_id,
            status=status,
            channel=channel,
            assigned_employee_id=assigned_employee_id,
            complaint_id=complaint_id,
            priority=priority,
            date_from=date_from,
            date_to=date_to,
            search=search,
            page=page,
            page_size=page_size,
        )

    async def update_status(
        self, conversation_id: uuid.UUID, new_status: ConversationStatus
    ) -> tuple[Conversation, list[DomainEvent]]:
        conversation = await self.get_conversation(conversation_id)
        previous_status = conversation.current_status
        if new_status != previous_status:
            self._validate_transition(previous_status, new_status)

        update_kwargs: dict = {"current_status": new_status}
        flags = _HANDLING_FLAGS.get(new_status)
        if flags is not None:
            update_kwargs["ai_handling"], update_kwargs["human_handling"] = flags

        updated = await self._repository.update(conversation_id, **update_kwargs)
        events: list[DomainEvent] = [
            ConversationStatusChangedEvent(
                conversation_id=conversation.id,
                previous_status=previous_status,
                new_status=new_status,
            )
        ]
        self._logger.info(
            "conversation_status_changed",
            conversation_id=str(conversation_id),
            previous_status=previous_status,
            new_status=new_status,
        )
        return updated, events

    async def assign_employee(
        self, conversation_id: uuid.UUID, employee_id: uuid.UUID
    ) -> tuple[Conversation, list[DomainEvent]]:
        await self.get_conversation(conversation_id)
        updated = await self._repository.update(
            conversation_id, assigned_employee_id=employee_id
        )
        events: list[DomainEvent] = [
            ConversationAssignedEvent(conversation_id=conversation_id, employee_id=employee_id)
        ]
        self._logger.info(
            "conversation_assigned",
            conversation_id=str(conversation_id),
            employee_id=str(employee_id),
        )
        return updated, events

    async def release_employee(self, conversation_id: uuid.UUID) -> Conversation:
        """The Human→AI handoff's state change — explicitly nulls
        `assigned_employee_id` (see `ConversationRepository.clear_assigned_employee`)."""
        await self.get_conversation(conversation_id)
        updated = await self._repository.clear_assigned_employee(conversation_id)
        self._logger.info("conversation_employee_released", conversation_id=str(conversation_id))
        return updated

    async def set_priority(
        self, conversation_id: uuid.UUID, priority: ConversationPriority
    ) -> Conversation:
        await self.get_conversation(conversation_id)
        updated = await self._repository.update(conversation_id, priority=priority)
        self._logger.info(
            "conversation_priority_set", conversation_id=str(conversation_id), priority=priority
        )
        return updated

    async def link_complaint(
        self, conversation_id: uuid.UUID, complaint_id: uuid.UUID
    ) -> Conversation:
        await self.get_conversation(conversation_id)
        return await self._repository.update(conversation_id, complaint_id=complaint_id)

    async def set_current_channel(
        self, conversation_id: uuid.UUID, channel
    ) -> Conversation:
        await self.get_conversation(conversation_id)
        return await self._repository.update(conversation_id, current_channel=channel)

    async def close_conversation(
        self, conversation_id: uuid.UUID
    ) -> tuple[Conversation, list[DomainEvent]]:
        conversation = await self.get_conversation(conversation_id)
        self._validate_transition(conversation.current_status, ConversationStatus.CLOSED)
        updated = await self._repository.update(
            conversation_id, current_status=ConversationStatus.CLOSED
        )
        events: list[DomainEvent] = [ConversationClosedEvent(conversation_id=conversation_id)]
        self._logger.info("conversation_closed", conversation_id=str(conversation_id))
        return updated, events

    @staticmethod
    def _validate_transition(current: ConversationStatus, target: ConversationStatus) -> None:
        allowed = _ALLOWED_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise InvalidConversationTransitionError(
                message=f"Cannot transition from '{current}' to '{target}'.",
                context={"current_status": current, "target_status": target},
            )

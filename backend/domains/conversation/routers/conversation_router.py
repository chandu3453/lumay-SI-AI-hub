"""Conversation REST API — foundation endpoints for the unified omnichannel
conversation (Sprint 28 Phase 1). No employee UI consumes these yet; they exist
to validate the schema/service layer end-to-end and for future phases to build on.
"""

import asyncio
import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request, status
from sse_starlette.sse import EventSourceResponse

from app.dependencies.auth import CurrentUser, get_current_active_user, get_current_user
from app.dependencies.conversation import (
    get_conversation_channel_repository,
    get_conversation_event_repository,
    get_conversation_event_service,
    get_conversation_participant_repository,
    get_conversation_participant_service,
    get_conversation_service,
    get_message_service,
)
from domains.conversation.constants.conversation_constants import (
    TERMINAL_CONVERSATION_STATUSES,
    ConversationChannel,
    ConversationMessageType,
    ConversationParticipantType,
    ConversationPriority,
    ConversationStatus,
)
from domains.conversation.event_bus import ConversationEventBus, publish_conversation_event
from domains.conversation.exceptions.conversation_exceptions import ConversationNotFoundError
from domains.conversation.models.conversation import Conversation
from domains.conversation.presence import get_presence_registry
from domains.conversation.repositories.channel_repository import ConversationChannelRepository
from domains.conversation.repositories.event_repository import ConversationEventRepository
from domains.conversation.repositories.participant_repository import (
    ConversationParticipantRepository,
)
from domains.conversation.schemas.conversation_schemas import (
    AssignEmployeeRequest,
    ChannelLinkResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationStatusResponse,
    ConversationSummary,
    EventCreate,
    EventResponse,
    MessageCreate,
    MessageResponse,
    MessageUpdateRequest,
    ParticipantResponse,
    PresenceSnapshotResponse,
    PresenceUpdateRequest,
    SetPriorityRequest,
    SupervisorActionRequest,
    TimelineItem,
    TypingUpdateRequest,
    UpdateStatusRequest,
)
from domains.conversation.services.conversation_service import ConversationService
from domains.conversation.services.event_service import ConversationEventService
from domains.conversation.services.message_service import MessageService
from domains.conversation.services.participant_service import ConversationParticipantService
from app.platform.logging import get_logger
from shared.response_schemas import PaginatedResponse, SuccessResponse

# Ownership-related event_type strings — the set GET /{id}/assignment-history
# filters to (also the Phase 4 "new timeline event types" the spec calls out).
_OWNERSHIP_EVENT_TYPES = {
    "conversation_assigned",
    "conversation_transferred",
    "conversation_released",
    "conversation_accepted",
    "ai_handed_over",
    "employee_joined",
    "employee_left",
    "supervisor_joined",
    "supervisor_left",
}

router = APIRouter(prefix="/conversations", tags=["Conversations"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=SuccessResponse[ConversationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a conversation",
    description="Directly creates a conversation. Most real traffic goes through "
    "ConversationFactory via the existing channel entry points instead.",
)
async def create_conversation(
    body: ConversationCreate,
    service: ConversationService = Depends(get_conversation_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ConversationResponse]:
    conversation, _ = await service.create_conversation(body)
    return SuccessResponse(data=ConversationResponse.model_validate(conversation))


@router.get(
    "",
    response_model=PaginatedResponse[ConversationSummary],
    summary="List conversations",
)
async def list_conversations(
    customer_id: uuid.UUID | None = Query(None, description="Filter by customer"),
    status: ConversationStatus | None = Query(None, description="Filter by status"),
    channel: ConversationChannel | None = Query(None, description="Filter by channel"),
    assigned_employee_id: uuid.UUID | None = Query(None, description="Filter by assigned employee"),
    complaint_id: uuid.UUID | None = Query(None, description="Filter by linked complaint"),
    priority: ConversationPriority | None = Query(None, description="Filter by priority"),
    date_from: datetime | None = Query(None, description="Filter by last-activity lower bound"),
    date_to: datetime | None = Query(None, description="Filter by last-activity upper bound"),
    search: str | None = Query(
        None,
        description="Matches customer name, conversation id, complaint id/policy number, or message text",
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: ConversationService = Depends(get_conversation_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> PaginatedResponse[ConversationSummary]:
    items, total = await service.list_conversations(
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
    # Batched enrichment (2 extra queries total, not one per card) for the
    # queue card's "Customer Name" / "Last Message Preview" fields, which
    # aren't columns on Conversation itself.
    conversation_ids = [item.id for item in items]
    customer_ids = [item.customer_id for item in items if item.customer_id is not None]
    preview_map = await service._repository.get_last_message_preview_map(conversation_ids)
    name_map = await service._repository.get_customer_name_map(customer_ids)

    data = [
        ConversationSummary(
            id=item.id,
            customer_id=item.customer_id,
            complaint_id=item.complaint_id,
            current_status=item.current_status,
            current_channel=item.current_channel,
            assigned_employee_id=item.assigned_employee_id,
            priority=item.priority,
            updated_at=item.updated_at,
            customer_name=name_map.get(item.customer_id) if item.customer_id else None,
            last_message_preview=preview_map.get(item.id),
        )
        for item in items
    ]
    return PaginatedResponse(
        data=data,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get(
    "/by-external-ref",
    response_model=SuccessResponse[ConversationResponse],
    summary="Resolve a conversation from a channel-adapter external ref",
    description="Reverse lookup via ConversationChannelLink (e.g. ref_type=interaction_id) — "
    "lets a channel UI that only knows its own interaction/session id (not the "
    "conversation id) reach conversation-level endpoints like presence/typing. "
    "Registered before /{conversation_id} so 'by-external-ref' is matched as a "
    "literal path, not a UUID.",
)
async def get_conversation_by_external_ref(
    ref_type: str = Query(..., description="e.g. 'interaction_id', 'voice_room', 'complaint_id'"),
    ref_id: str = Query(...),
    channel_repository: ConversationChannelRepository = Depends(get_conversation_channel_repository),
    service: ConversationService = Depends(get_conversation_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ConversationResponse]:
    link = await channel_repository.get_by_external_ref(ref_type, ref_id)
    if link is None:
        raise ConversationNotFoundError(context={"ref_type": ref_type, "ref_id": ref_id})
    conversation = await service.get_conversation(link.conversation_id)
    return SuccessResponse(data=ConversationResponse.model_validate(conversation))


@router.get(
    "/stream",
    summary="Live stream of all conversation updates (SSE)",
    description="Push-based via asyncio.Queue, modeled on GET /demo/events — "
    "every message/event/status-change/assignment across every conversation, "
    "unfiltered. Registered before /{conversation_id} so 'stream' is matched "
    "as a literal path, not a UUID.",
)
async def stream_all_conversations(
    request: Request, _current_user: CurrentUser | None = Depends(get_current_user)
) -> EventSourceResponse:
    q = ConversationEventBus.subscribe()

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(q.get(), timeout=30.0)
                    yield {"event": event.event_type, "data": json.dumps(event.to_dict())}
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "keepalive"}
        finally:
            ConversationEventBus.unsubscribe(q)

    return EventSourceResponse(event_generator())


@router.get(
    "/{conversation_id}",
    response_model=SuccessResponse[ConversationResponse],
    summary="Get conversation by ID",
)
async def get_conversation(
    conversation_id: uuid.UUID,
    service: ConversationService = Depends(get_conversation_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ConversationResponse]:
    conversation = await service.get_conversation(conversation_id)
    return SuccessResponse(data=ConversationResponse.model_validate(conversation))


@router.patch(
    "/{conversation_id}/status",
    response_model=SuccessResponse[ConversationResponse],
    summary="Transition conversation status",
    description="Centralized lifecycle transition — validated against the allowed-transitions state machine.",
)
async def update_conversation_status(
    conversation_id: uuid.UUID,
    body: UpdateStatusRequest,
    service: ConversationService = Depends(get_conversation_service),
    event_service: ConversationEventService = Depends(get_conversation_event_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ConversationResponse]:
    conversation, _ = await service.update_status(conversation_id, body.status)
    payload = {"current_status": conversation.current_status}
    # Persist, not just broadcast — before Phase 4 this only reached live SSE
    # subscribers; anyone opening the timeline later never saw the change.
    await event_service.record_event(conversation_id, "status_changed", "conversation", payload)
    publish_conversation_event(str(conversation_id), "status_changed", payload)
    return SuccessResponse(data=ConversationResponse.model_validate(conversation))


@router.post(
    "/{conversation_id}/assign",
    response_model=SuccessResponse[ConversationResponse],
    summary="Assign an employee to a conversation",
)
async def assign_conversation(
    conversation_id: uuid.UUID,
    body: AssignEmployeeRequest,
    service: ConversationService = Depends(get_conversation_service),
    participant_service: ConversationParticipantService = Depends(
        get_conversation_participant_service
    ),
    event_service: ConversationEventService = Depends(get_conversation_event_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ConversationResponse]:
    previous_employee_id = (await service.get_conversation(conversation_id)).assigned_employee_id
    conversation, _ = await service.assign_employee(conversation_id, body.employee_id)
    # "Employee later joins" (Phase 2, scenario 4) — de-duplicated by
    # ensure_participant, so reassigning the same employee is a no-op.
    await participant_service.ensure_participant(
        conversation_id, ConversationParticipantType.EMPLOYEE, str(body.employee_id)
    )
    payload = {
        "assigned_employee_id": str(body.employee_id),
        "previous_employee_id": str(previous_employee_id) if previous_employee_id else None,
    }
    await event_service.record_event(conversation_id, "conversation_assigned", "conversation", payload)
    publish_conversation_event(str(conversation_id), "assigned", payload)
    return SuccessResponse(data=ConversationResponse.model_validate(conversation))


@router.post(
    "/{conversation_id}/take-over",
    response_model=SuccessResponse[ConversationResponse],
    summary="Employee takes over from AI",
    description="AI→Human handoff: AI stops auto-responding, the employee becomes "
    "owner, and the customer is told a human has joined. Timeline records both "
    "'employee_joined' and 'ai_handed_over'.",
)
async def take_over_conversation(
    conversation_id: uuid.UUID,
    body: AssignEmployeeRequest,
    service: ConversationService = Depends(get_conversation_service),
    participant_service: ConversationParticipantService = Depends(
        get_conversation_participant_service
    ),
    message_service: MessageService = Depends(get_message_service),
    event_service: ConversationEventService = Depends(get_conversation_event_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ConversationResponse]:
    conversation = await service.get_conversation(conversation_id)
    conversation, _ = await service.assign_employee(conversation_id, body.employee_id)
    conversation, _ = await service.update_status(conversation_id, ConversationStatus.HUMAN_HANDLING)
    await participant_service.ensure_participant(
        conversation_id, ConversationParticipantType.EMPLOYEE, str(body.employee_id)
    )
    # Customer-visible handoff notice — same message/timeline path any other
    # system notification uses, not a new mechanism.
    await message_service.add_message(
        conversation_id,
        ConversationParticipantType.SYSTEM,
        conversation.current_channel,
        "You are now connected with one of our insurance specialists.",
        message_type=ConversationMessageType.SYSTEM_NOTIFICATION,
    )
    payload = {"employee_id": str(body.employee_id), "direction": "ai_to_human"}
    for event_type in ("employee_joined", "ai_handed_over"):
        await event_service.record_event(conversation_id, event_type, "conversation", payload)
        publish_conversation_event(str(conversation_id), event_type, payload)
    await service._repository.touch(conversation_id)
    return SuccessResponse(data=ConversationResponse.model_validate(conversation))


@router.post(
    "/{conversation_id}/release",
    response_model=SuccessResponse[ConversationResponse],
    summary="Employee releases the conversation back to AI",
    description="Human→AI handoff: clears the assignment and resumes AI handling. "
    "Timeline records 'employee_left' and 'ai_handed_over'.",
)
async def release_conversation(
    conversation_id: uuid.UUID,
    service: ConversationService = Depends(get_conversation_service),
    event_service: ConversationEventService = Depends(get_conversation_event_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ConversationResponse]:
    conversation = await service.get_conversation(conversation_id)
    previous_employee_id = conversation.assigned_employee_id
    await service.update_status(conversation_id, ConversationStatus.AI_HANDLING)
    conversation = await service.release_employee(conversation_id)
    payload = {
        "employee_id": str(previous_employee_id) if previous_employee_id else None,
        "direction": "human_to_ai",
    }
    for event_type in ("employee_left", "ai_handed_over"):
        await event_service.record_event(conversation_id, event_type, "conversation", payload)
        publish_conversation_event(str(conversation_id), event_type, payload)
    await service._repository.touch(conversation_id)
    return SuccessResponse(data=ConversationResponse.model_validate(conversation))


@router.post(
    "/{conversation_id}/transfer",
    response_model=SuccessResponse[ConversationResponse],
    summary="Transfer to a different employee",
    description="Human→Human handoff — stays HUMAN_HANDLING, records "
    "'conversation_transferred' with the previous and new owner.",
)
async def transfer_conversation(
    conversation_id: uuid.UUID,
    body: AssignEmployeeRequest,
    service: ConversationService = Depends(get_conversation_service),
    participant_service: ConversationParticipantService = Depends(
        get_conversation_participant_service
    ),
    event_service: ConversationEventService = Depends(get_conversation_event_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ConversationResponse]:
    previous_employee_id = (await service.get_conversation(conversation_id)).assigned_employee_id
    conversation, _ = await service.assign_employee(conversation_id, body.employee_id)
    await participant_service.ensure_participant(
        conversation_id, ConversationParticipantType.EMPLOYEE, str(body.employee_id)
    )
    payload = {
        "previous_owner": str(previous_employee_id) if previous_employee_id else None,
        "new_owner": str(body.employee_id),
    }
    await event_service.record_event(conversation_id, "conversation_transferred", "conversation", payload)
    publish_conversation_event(str(conversation_id), "conversation_transferred", payload)
    return SuccessResponse(data=ConversationResponse.model_validate(conversation))


@router.post(
    "/{conversation_id}/accept",
    response_model=SuccessResponse[ConversationResponse],
    summary="Employee accepts an assignment",
    description="Lightweight acknowledgment — records 'conversation_accepted' without "
    "changing ownership (assign/transfer/take-over already set the owner).",
)
async def accept_conversation(
    conversation_id: uuid.UUID,
    body: AssignEmployeeRequest,
    service: ConversationService = Depends(get_conversation_service),
    event_service: ConversationEventService = Depends(get_conversation_event_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ConversationResponse]:
    conversation = await service.get_conversation(conversation_id)
    payload = {"employee_id": str(body.employee_id)}
    await event_service.record_event(conversation_id, "conversation_accepted", "conversation", payload)
    publish_conversation_event(str(conversation_id), "conversation_accepted", payload)
    return SuccessResponse(data=ConversationResponse.model_validate(conversation))


@router.post(
    "/{conversation_id}/supervisor/join",
    response_model=SuccessResponse[ParticipantResponse],
    summary="Supervisor joins to monitor",
    description="Registers the supervisor as a participant — never touches "
    "assigned_employee_id or status (monitoring only). Not exposed to customers.",
)
async def supervisor_join(
    conversation_id: uuid.UUID,
    body: SupervisorActionRequest,
    service: ConversationService = Depends(get_conversation_service),
    participant_service: ConversationParticipantService = Depends(
        get_conversation_participant_service
    ),
    event_service: ConversationEventService = Depends(get_conversation_event_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ParticipantResponse]:
    await service.get_conversation(conversation_id)  # 404s if missing
    participant = await participant_service.ensure_participant(
        conversation_id, ConversationParticipantType.SUPERVISOR, str(body.supervisor_id)
    )
    payload = {"supervisor_id": str(body.supervisor_id)}
    await event_service.record_event(conversation_id, "supervisor_joined", "conversation", payload)
    publish_conversation_event(str(conversation_id), "supervisor_joined", payload)
    return SuccessResponse(data=ParticipantResponse.model_validate(participant))


@router.post(
    "/{conversation_id}/supervisor/leave",
    response_model=SuccessResponse[ConversationResponse],
    summary="Supervisor stops monitoring",
)
async def supervisor_leave(
    conversation_id: uuid.UUID,
    body: SupervisorActionRequest,
    service: ConversationService = Depends(get_conversation_service),
    event_service: ConversationEventService = Depends(get_conversation_event_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ConversationResponse]:
    conversation = await service.get_conversation(conversation_id)
    payload = {"supervisor_id": str(body.supervisor_id)}
    await event_service.record_event(conversation_id, "supervisor_left", "conversation", payload)
    publish_conversation_event(str(conversation_id), "supervisor_left", payload)
    return SuccessResponse(data=ConversationResponse.model_validate(conversation))


@router.get(
    "/{conversation_id}/assignment-history",
    response_model=SuccessResponse[list[EventResponse]],
    summary="Ownership/assignment history for a conversation",
    description="Filters the conversation's event log to assignment/handoff/"
    "supervisor event types — current owner is still `assigned_employee_id` "
    "on GET /{id}; this is the 'previous owner' + full transfer history.",
)
async def get_assignment_history(
    conversation_id: uuid.UUID,
    repository: ConversationEventRepository = Depends(get_conversation_event_repository),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[list[EventResponse]]:
    events, _total = await repository.list_by_conversation(conversation_id, page=1, page_size=500)
    ownership_events = [e for e in events if e.event_type in _OWNERSHIP_EVENT_TYPES]
    return SuccessResponse(data=[EventResponse.model_validate(e) for e in ownership_events])


@router.post(
    "/{conversation_id}/close",
    response_model=SuccessResponse[ConversationResponse],
    summary="Close a conversation",
)
async def close_conversation(
    conversation_id: uuid.UUID,
    service: ConversationService = Depends(get_conversation_service),
    event_service: ConversationEventService = Depends(get_conversation_event_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ConversationResponse]:
    conversation, _ = await service.close_conversation(conversation_id)
    payload = {"current_status": conversation.current_status}
    # Same persist-then-broadcast fix already applied to assign/status
    # (Sprint 28 Phase 4) — close was missed, leaving closures invisible to
    # anyone not watching live (surfaced by Sprint 29's activity timeline).
    await event_service.record_event(conversation_id, "status_changed", "conversation", payload)
    publish_conversation_event(str(conversation_id), "status_changed", payload)
    return SuccessResponse(data=ConversationResponse.model_validate(conversation))


@router.patch(
    "/{conversation_id}/priority",
    response_model=SuccessResponse[ConversationResponse],
    summary="Set conversation priority",
    description="The 'Mark Priority' employee action.",
)
async def set_conversation_priority(
    conversation_id: uuid.UUID,
    body: SetPriorityRequest,
    service: ConversationService = Depends(get_conversation_service),
    event_service: ConversationEventService = Depends(get_conversation_event_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[ConversationResponse]:
    conversation = await service.set_priority(conversation_id, body.priority)
    payload = {"priority": conversation.priority}
    # Same persist-then-broadcast fix as close_conversation — priority was
    # SSE-only, leaving it invisible to the activity timeline/reconnects.
    await event_service.record_event(conversation_id, "priority_changed", "conversation", payload)
    publish_conversation_event(str(conversation_id), "priority_changed", payload)
    return SuccessResponse(data=ConversationResponse.model_validate(conversation))


@router.post(
    "/{conversation_id}/messages",
    response_model=SuccessResponse[MessageResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add a message to a conversation",
)
async def add_message(
    conversation_id: uuid.UUID,
    body: MessageCreate,
    conversation_service: ConversationService = Depends(get_conversation_service),
    message_service: MessageService = Depends(get_message_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[MessageResponse]:
    await conversation_service.get_conversation(conversation_id)  # 404s if missing
    message = await message_service.add_message(
        conversation_id,
        body.sender_type,
        body.channel,
        body.content,
        message_type=body.message_type,
        metadata=body.metadata,
    )
    publish_conversation_event(
        str(conversation_id),
        "message",
        {
            "id": str(message.id),
            "sender_type": message.sender_type,
            "channel": message.channel,
            "message_type": message.message_type,
            "content": message.content,
            "message_metadata": message.message_metadata,
        },
    )
    return SuccessResponse(data=MessageResponse.model_validate(message))


@router.get(
    "/{conversation_id}/messages",
    response_model=PaginatedResponse[MessageResponse],
    summary="List messages in a conversation (chronological)",
)
async def list_messages(
    conversation_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    message_service: MessageService = Depends(get_message_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> PaginatedResponse[MessageResponse]:
    items, total = await message_service.list_messages(
        conversation_id, page=page, page_size=page_size
    )
    return PaginatedResponse(
        data=[MessageResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.patch(
    "/{conversation_id}/messages/{message_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Edit an internal note",
    description="Only messages with metadata.internal=true are editable — "
    "customer-visible messages are immutable once sent (422 otherwise).",
)
async def update_message(
    conversation_id: uuid.UUID,
    message_id: uuid.UUID,
    body: MessageUpdateRequest,
    message_service: MessageService = Depends(get_message_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[MessageResponse]:
    message = await message_service.update_message(message_id, body.content)
    publish_conversation_event(
        str(conversation_id),
        "internal_note_updated",
        {"message_id": str(message_id), "content": message.content},
    )
    return SuccessResponse(data=MessageResponse.model_validate(message))


@router.delete(
    "/{conversation_id}/messages/{message_id}",
    response_model=SuccessResponse[MessageResponse],
    summary="Delete an internal note",
    description="Soft delete (metadata.deleted=true) — the row is kept for audit "
    "(author/timestamp survive); only internal notes are deletable (422 otherwise).",
)
async def delete_message(
    conversation_id: uuid.UUID,
    message_id: uuid.UUID,
    message_service: MessageService = Depends(get_message_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[MessageResponse]:
    message = await message_service.delete_message(message_id)
    publish_conversation_event(
        str(conversation_id), "internal_note_deleted", {"message_id": str(message_id)}
    )
    return SuccessResponse(data=MessageResponse.model_validate(message))


@router.get(
    "/{conversation_id}/channels",
    response_model=SuccessResponse[list[ChannelLinkResponse]],
    summary="List channel touchpoints for a conversation",
)
async def list_channel_links(
    conversation_id: uuid.UUID,
    repository: ConversationChannelRepository = Depends(get_conversation_channel_repository),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[list[ChannelLinkResponse]]:
    items = await repository.list_by_conversation(conversation_id)
    return SuccessResponse(data=[ChannelLinkResponse.model_validate(item) for item in items])


@router.get(
    "/{conversation_id}/events",
    response_model=PaginatedResponse[EventResponse],
    summary="List recorded events for a conversation",
)
async def list_conversation_events(
    conversation_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    repository: ConversationEventRepository = Depends(get_conversation_event_repository),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> PaginatedResponse[EventResponse]:
    items, total = await repository.list_by_conversation(
        conversation_id, page=page, page_size=page_size
    )
    return PaginatedResponse(
        data=[EventResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get(
    "/{conversation_id}/participants",
    response_model=SuccessResponse[list[ParticipantResponse]],
    summary="List participants in a conversation",
)
async def list_participants(
    conversation_id: uuid.UUID,
    repository: ConversationParticipantRepository = Depends(
        get_conversation_participant_repository
    ),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[list[ParticipantResponse]]:
    items = await repository.list_by_conversation(conversation_id)
    return SuccessResponse(data=[ParticipantResponse.model_validate(item) for item in items])


@router.get(
    "/{conversation_id}/status",
    response_model=SuccessResponse[ConversationStatusResponse],
    summary="Get conversation status",
    description="Lightweight status-only projection (status/handling flags/assignee).",
)
async def get_conversation_status(
    conversation_id: uuid.UUID,
    service: ConversationService = Depends(get_conversation_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ConversationStatusResponse]:
    conversation = await service.get_conversation(conversation_id)
    return SuccessResponse(data=ConversationStatusResponse.model_validate(conversation))


@router.post(
    "/{conversation_id}/events",
    response_model=SuccessResponse[EventResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Append an event to a conversation",
    description="Publishes a ConversationEvent directly — for manual/system-injected events.",
)
async def add_event(
    conversation_id: uuid.UUID,
    body: EventCreate,
    conversation_service: ConversationService = Depends(get_conversation_service),
    event_service: ConversationEventService = Depends(get_conversation_event_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[EventResponse]:
    await conversation_service.get_conversation(conversation_id)  # 404s if missing
    event = await event_service.record_event(
        conversation_id, body.event_type, body.source_domain, body.payload
    )
    publish_conversation_event(
        str(conversation_id),
        "event",
        {
            "id": str(event.id),
            "event_type": event.event_type,
            "source_domain": event.source_domain,
            "payload": event.payload,
        },
    )
    return SuccessResponse(data=EventResponse.model_validate(event))


@router.get(
    "/{conversation_id}/timeline",
    response_model=PaginatedResponse[TimelineItem],
    summary="Get the merged chronological timeline",
    description="Merges messages + events into one timestamp-sorted view. "
    "Merges up to 1000 of each source before paginating — a foundation-phase "
    "limitation, not a silent cap: very high-volume conversations would need "
    "a DB-level merge query, out of scope for this phase.",
)
async def get_conversation_timeline(
    conversation_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    conversation_service: ConversationService = Depends(get_conversation_service),
    message_service: MessageService = Depends(get_message_service),
    event_repository: ConversationEventRepository = Depends(get_conversation_event_repository),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> PaginatedResponse[TimelineItem]:
    await conversation_service.get_conversation(conversation_id)  # 404s if missing

    messages, message_total = await message_service.list_messages(
        conversation_id, page=1, page_size=1000
    )
    events, event_total = await event_repository.list_by_conversation(
        conversation_id, page=1, page_size=1000
    )

    items: list[TimelineItem] = [
        TimelineItem(
            type="message",
            id=m.id,
            timestamp=m.created_at,
            sender_type=m.sender_type,
            channel=m.channel,
            message_type=m.message_type,
            content=m.content,
            # Reuses the same `payload` field events use, rather than adding a
            # new one — this is how the frontend tells an internal note
            # (metadata={"internal": true}) apart from a customer-visible reply.
            payload=m.message_metadata,
        )
        for m in messages
    ] + [
        TimelineItem(
            type="event",
            id=e.id,
            timestamp=e.created_at,
            event_type=e.event_type,
            source_domain=e.source_domain,
            payload=e.payload,
        )
        for e in events
    ]
    items.sort(key=lambda item: item.timestamp)

    total = message_total + event_total
    offset = (page - 1) * page_size
    page_items = items[offset : offset + page_size]

    return PaginatedResponse(
        data=page_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get(
    "/{conversation_id}/stream",
    summary="Live stream of updates for one conversation (SSE)",
    description="Same ConversationEventBus as GET /conversations/stream, filtered "
    "to this conversation_id — used while an employee has a conversation open.",
)
async def stream_conversation(
    conversation_id: uuid.UUID,
    request: Request,
    conversation_service: ConversationService = Depends(get_conversation_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> EventSourceResponse:
    await conversation_service.get_conversation(conversation_id)  # 404s if missing
    target_id = str(conversation_id)
    q = ConversationEventBus.subscribe()

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(q.get(), timeout=30.0)
                    if event.conversation_id != target_id:
                        continue
                    yield {"event": event.event_type, "data": json.dumps(event.to_dict())}
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": "keepalive"}
        finally:
            ConversationEventBus.unsubscribe(q)

    return EventSourceResponse(event_generator())


@router.get(
    "/{conversation_id}/stream/history",
    response_model=SuccessResponse[list[dict]],
    summary="Recent realtime events for one conversation (reconnect catch-up)",
)
async def get_conversation_stream_history(
    conversation_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[list[dict]]:
    return SuccessResponse(data=ConversationEventBus.get_recent(str(conversation_id), limit=limit))


@router.post(
    "/{conversation_id}/presence",
    response_model=SuccessResponse[PresenceSnapshotResponse],
    summary="Report a participant's online/offline presence",
    description="Ephemeral, in-process only — never persisted to conversation_events. "
    "Broadcasts the updated snapshot over SSE so other viewers stay in sync.",
)
async def update_presence(
    conversation_id: uuid.UUID,
    body: PresenceUpdateRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[PresenceSnapshotResponse]:
    conversation = await conversation_service.get_conversation(conversation_id)
    registry = get_presence_registry()
    await registry.set_presence(
        str(conversation_id), body.participant_type, body.participant_ref, body.status
    )
    publish_conversation_event(
        str(conversation_id),
        "presence",
        {
            "participant_type": body.participant_type,
            "participant_ref": body.participant_ref,
            "status": body.status,
        },
    )
    return SuccessResponse(data=_build_presence_snapshot(conversation_id, conversation, registry))


@router.get(
    "/{conversation_id}/presence",
    response_model=SuccessResponse[PresenceSnapshotResponse],
    summary="Current presence/typing snapshot",
    description="For initial load before the SSE connection catches up.",
)
async def get_presence(
    conversation_id: uuid.UUID,
    conversation_service: ConversationService = Depends(get_conversation_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[PresenceSnapshotResponse]:
    conversation = await conversation_service.get_conversation(conversation_id)
    registry = get_presence_registry()
    snapshot = _build_presence_snapshot(conversation_id, conversation, registry)
    return SuccessResponse(data=snapshot)


@router.post(
    "/{conversation_id}/typing",
    response_model=SuccessResponse[PresenceSnapshotResponse],
    summary="Report a participant's typing state",
    description="Ephemeral, auto-expires client-side after a few seconds of "
    "silence — never persisted to conversation_events.",
)
async def update_typing(
    conversation_id: uuid.UUID,
    body: TypingUpdateRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[PresenceSnapshotResponse]:
    conversation = await conversation_service.get_conversation(conversation_id)
    registry = get_presence_registry()
    await registry.set_typing(str(conversation_id), body.participant_type, body.is_typing)
    publish_conversation_event(
        str(conversation_id),
        "typing",
        {"participant_type": body.participant_type, "is_typing": body.is_typing},
    )
    return SuccessResponse(data=_build_presence_snapshot(conversation_id, conversation, registry))


def _build_presence_snapshot(
    conversation_id: uuid.UUID,
    conversation: Conversation,
    registry,
) -> PresenceSnapshotResponse:
    snap = registry.get_snapshot(str(conversation_id))
    return PresenceSnapshotResponse(
        presence=snap["presence"],
        typing=snap["typing"],
        ai_active=bool(conversation.ai_handling),
        conversation_live=conversation.current_status not in TERMINAL_CONVERSATION_STATUSES,
        voice_active=(
            conversation.current_channel == ConversationChannel.VOICE
            and conversation.current_status not in TERMINAL_CONVERSATION_STATUSES
        ),
    )

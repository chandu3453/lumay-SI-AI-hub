"""Interaction REST API — endpoints for omnichannel interaction management."""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import CurrentUser, get_current_user
from app.dependencies.interaction import get_interaction_service
from domains.interaction.constants.interaction_constants import (
    InteractionChannel,
    InteractionDirection,
    InteractionStatus,
)
from domains.interaction.schemas.interaction_schemas import (
    InteractionCreate,
    InteractionResponse,
    InteractionSummary,
    InteractionUpdate,
)
from domains.interaction.services.interaction_service import InteractionService
from domains.interaction.models.interaction import Interaction
from app.platform.logging import get_logger
from datetime import datetime, timezone
import json
from ai.gateway.ai_gateway import get_ai_gateway
from ai.models import ChatMessage
from ai.intelligence.service import ComplaintIntelligenceService
from knowledge.service import KnowledgeService
from app.dependencies.complaint import get_complaint_service
from app.dependencies.workflow import get_workflow_service
from app.dependencies.notification import get_notification_service
from domains.interaction.schemas.interaction_schemas import (
    ChatStartRequest,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatResponsePayload,
)
from shared.response_schemas import PaginatedResponse, SuccessResponse

router = APIRouter(prefix="/interactions", tags=["Interactions"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=SuccessResponse[InteractionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create an interaction",
    description="Creates a new omnichannel customer interaction.",
)
async def create_interaction(
    body: InteractionCreate,
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[InteractionResponse]:
    interaction, _ = await service.create_interaction(body)
    return SuccessResponse(data=InteractionResponse.model_validate(interaction))


@router.get(
    "",
    response_model=PaginatedResponse[InteractionSummary],
    summary="List interactions",
    description="Returns a paginated list of interactions with optional filters.",
)
async def list_interactions(
    channel: InteractionChannel | None = Query(None, description="Filter by channel"),
    status: InteractionStatus | None = Query(None, description="Filter by status"),
    direction: InteractionDirection | None = Query(None, description="Filter by direction"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> PaginatedResponse[InteractionSummary]:
    items, total = await service.list_interactions(
        channel=channel,
        status=status,
        direction=direction,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        data=[InteractionSummary.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


# ==========================================
# Sprint 16 — AI Customer Chat endpoints
# ==========================================

_ENTERPRISE_SYSTEM_PROMPT = """You are the official AI assistant representing LuMay Insurance, Oman.
Your goal is to assist customers professionally and empathetic with their insurance policies, claims, renewals, payments, and complaint intake.

GUIDELINES:
1. POLICY QUESTIONS: Answer questions about policy coverage, rules, deductibles, and benefits using the provided Knowledge Service context.
2. CLAIMS: Guide users on how to submit claims, check claim status, and upload documents.
3. RENEWALS & PAYMENTS: Help with renewal periods, calculating rates, and processing premium payment queries.
4. COMPLAINT INTAKE: If the customer expresses dissatisfaction, gather details about their complaint (e.g. policy number, claim ID, failure reason) and explain that a complaint officer will review it.
5. NO HALLUCINATION: Never hallucinate or make up policy rules, limits, or dates. If the context does not contain the answer, say "I don't have that specific policy detail, but let me transfer you to a human agent who can check."
6. CLARIFICATION: Ask clarifying questions if the customer's query is vague.
7. HUMAN ESCALATION: Escalate to a human agent immediately if the user requests human support, is highly angry, or if your knowledge confidence is low.
8. Tone: Professional, polite, clear, and reassuring.
"""


def get_message_history(interaction: Interaction) -> list[dict]:
    if not interaction.transcript:
        return []
    try:
        return json.loads(interaction.transcript)
    except json.JSONDecodeError:
        # Fallback for plain text transcripts
        return [{
            "role": "user",
            "content": interaction.transcript,
            "timestamp": interaction.created_at.isoformat() if interaction.created_at else datetime.now(timezone.utc).isoformat()
        }]


@router.post(
    "/chat/start",
    response_model=SuccessResponse[InteractionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Start AI customer chat",
)
async def start_chat(
    body: ChatStartRequest,
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[InteractionResponse]:
    # Creates an interaction record with "[]" transcript array
    transcript_data = []
    if body.complaint_id:
        transcript_data.append({
            "role": "system",
            "content": f"Customer is continuing conversation for complaint_id: {body.complaint_id}. Please reference this complaint in your context.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    data = InteractionCreate(
        customer_ref=body.customer_ref,
        channel=body.channel,
        direction=InteractionDirection.INBOUND,
        subject=f"AI Chat Session (Complaint: {body.complaint_id})" if body.complaint_id else "AI Chat Session",
        transcript=json.dumps(transcript_data),
        status=InteractionStatus.RECEIVED,
    )
    interaction, _ = await service.create_interaction(data)

    from domains.conversation import integration_hooks as conversation_hooks

    await conversation_hooks.on_interaction_started(
        service._repository._session,
        body.customer_ref,
        body.channel,
        interaction.id,
        complaint_id=body.complaint_id,
    )

    return SuccessResponse(data=InteractionResponse.model_validate(interaction))


@router.post(
    "/chat/message",
    response_model=SuccessResponse[ChatResponsePayload],
    summary="Send message and generate AI response",
)
async def chat_message(
    body: ChatMessageRequest,
    interaction_service: InteractionService = Depends(get_interaction_service),
    complaint_service = Depends(get_complaint_service),
    workflow_service = Depends(get_workflow_service),
    notification_service = Depends(get_notification_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ChatResponsePayload]:
    from domains.interaction.services.conversation_engine import process_conversation
    result = await process_conversation(
        interaction_id=body.interaction_id,
        message=body.message,
        interaction_service=interaction_service,
        complaint_service=complaint_service,
        workflow_service=workflow_service,
        notification_service=notification_service,
    )
    return SuccessResponse(data=ChatResponsePayload.model_validate(result))


# ==========================================
# Sprint 15 — Omnichannel REST APIs
# ==========================================

@router.post(
    "/conversations/start",
    response_model=SuccessResponse[InteractionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Start a new customer conversation",
)
async def conversations_start(
    body: ChatStartRequest,
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[InteractionResponse]:
    return await start_chat(body, service)


@router.post(
    "/conversations/message",
    response_model=SuccessResponse[ChatResponsePayload],
    summary="Post a message to an active conversation",
)
async def conversations_message(
    body: ChatMessageRequest,
    interaction_service: InteractionService = Depends(get_interaction_service),
    complaint_service = Depends(get_complaint_service),
    workflow_service = Depends(get_workflow_service),
    notification_service = Depends(get_notification_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ChatResponsePayload]:
    return await chat_message(
        body,
        interaction_service=interaction_service,
        complaint_service=complaint_service,
        workflow_service=workflow_service,
        notification_service=notification_service,
    )


@router.get(
    "/conversations",
    response_model=PaginatedResponse[InteractionSummary],
    summary="List all conversations",
)
async def conversations_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> PaginatedResponse[InteractionSummary]:
    from sqlalchemy import select, func
    from domains.interaction.models.interaction import Interaction
    
    query = select(Interaction)
    count_query = select(func.count(Interaction.id))
    
    total_result = await service._repository._session.execute(count_query)
    total = total_result.scalar_one()
    
    offset = (page - 1) * page_size
    query = query.order_by(Interaction.created_at.desc()).offset(offset).limit(page_size)
    result = await service._repository._session.execute(query)
    items = result.scalars().all()
    
    return PaginatedResponse(
        data=[InteractionSummary.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=SuccessResponse[list[ChatMessageResponse]],
    summary="Get conversation history details",
)
async def conversations_get(
    conversation_id: uuid.UUID,
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[list[ChatMessageResponse]]:
    return await get_chat_conversation(conversation_id, service)


@router.post(
    "/conversations/end",
    response_model=SuccessResponse[InteractionResponse],
    summary="End an active conversation",
)
async def conversations_end(
    body: ChatMessageRequest,
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[InteractionResponse]:
    return await end_chat(body, service)


@router.get(
    "/customer/{customer_id}/history",
    response_model=SuccessResponse[list[InteractionSummary]],
    summary="Get customer interaction history",
)
async def get_customer_history(
    customer_id: uuid.UUID,
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[list[InteractionSummary]]:
    from sqlalchemy import select
    from domains.interaction.models.interaction import Interaction
    
    stmt = select(Interaction).where(
        Interaction.customer_ref == str(customer_id)
    ).order_by(Interaction.created_at.desc())
    
    result = await service._repository._session.execute(stmt)
    items = result.scalars().all()
    
    return SuccessResponse(data=[InteractionSummary.model_validate(item) for item in items])


@router.post(
    "/voice/process",
    response_model=SuccessResponse[ChatResponsePayload],
    summary="Process voice message transcript",
)
async def process_voice_message(
    body: ChatMessageRequest,
    interaction_service: InteractionService = Depends(get_interaction_service),
    complaint_service = Depends(get_complaint_service),
    workflow_service = Depends(get_workflow_service),
    notification_service = Depends(get_notification_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ChatResponsePayload]:
    return await chat_message(
        body,
        interaction_service=interaction_service,
        complaint_service=complaint_service,
        workflow_service=workflow_service,
        notification_service=notification_service,
    )


@router.post(
    "/email/process",
    response_model=SuccessResponse[ChatResponsePayload],
    summary="Process incoming/outgoing email",
)
async def process_email_message(
    body: ChatMessageRequest,
    interaction_service: InteractionService = Depends(get_interaction_service),
    complaint_service = Depends(get_complaint_service),
    workflow_service = Depends(get_workflow_service),
    notification_service = Depends(get_notification_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ChatResponsePayload]:
    return await chat_message(
        body,
        interaction_service=interaction_service,
        complaint_service=complaint_service,
        workflow_service=workflow_service,
        notification_service=notification_service,
    )


@router.post(
    "/whatsapp/process",
    response_model=SuccessResponse[ChatResponsePayload],
    summary="Process WhatsApp message",
)
async def process_whatsapp_message(
    body: ChatMessageRequest,
    interaction_service: InteractionService = Depends(get_interaction_service),
    complaint_service = Depends(get_complaint_service),
    workflow_service = Depends(get_workflow_service),
    notification_service = Depends(get_notification_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[ChatResponsePayload]:
    return await chat_message(
        body,
        interaction_service=interaction_service,
        complaint_service=complaint_service,
        workflow_service=workflow_service,
        notification_service=notification_service,
    )


@router.get(
    "/chat/history",
    response_model=PaginatedResponse[InteractionSummary],
    summary="List chat session history",
)
async def list_chat_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> PaginatedResponse[InteractionSummary]:
    from sqlalchemy import select, func, or_
    from domains.interaction.models.interaction import Interaction
    
    query = select(Interaction).where(
        or_(
            Interaction.channel == InteractionChannel.WHATSAPP,
            Interaction.channel == InteractionChannel.WEB_FORM
        )
    )
    count_query = select(func.count(Interaction.id)).where(
        or_(
            Interaction.channel == InteractionChannel.WHATSAPP,
            Interaction.channel == InteractionChannel.WEB_FORM
        )
    )
    
    total_result = await service._repository._session.execute(count_query)
    total = total_result.scalar_one()
    
    offset = (page - 1) * page_size
    query = query.order_by(Interaction.created_at.desc()).offset(offset).limit(page_size)
    result = await service._repository._session.execute(query)
    items = result.scalars().all()
    
    return PaginatedResponse(
        data=[InteractionSummary.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get(
    "/chat/{conversation_id}",
    response_model=SuccessResponse[list[ChatMessageResponse]],
    summary="Get conversation history details",
)
async def get_chat_conversation(
    conversation_id: uuid.UUID,
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[list[ChatMessageResponse]]:
    interaction = await service.get_interaction(conversation_id)
    history = get_message_history(interaction)
    output_messages = []
    for msg in history:
        try:
            ts = datetime.fromisoformat(msg["timestamp"])
        except (ValueError, KeyError):
            ts = datetime.now(timezone.utc)
        output_messages.append(ChatMessageResponse(role=msg["role"], content=msg["content"], timestamp=ts))
    return SuccessResponse(data=output_messages)


@router.post(
    "/chat/end",
    response_model=SuccessResponse[InteractionResponse],
    summary="End AI chat session",
)
async def end_chat(
    body: ChatMessageRequest,
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[InteractionResponse]:
    interaction = await service.get_interaction(body.interaction_id)
    updated = await service._repository.update(interaction.id, status=InteractionStatus.COMPLETED)
    return SuccessResponse(data=InteractionResponse.model_validate(updated))


@router.get(
    "/{interaction_id}",
    response_model=SuccessResponse[InteractionResponse],
    summary="Get interaction by ID",
    description="Returns a single interaction by its unique identifier.",
)
async def get_interaction(
    interaction_id: uuid.UUID,
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[InteractionResponse]:
    interaction = await service.get_interaction(interaction_id)
    return SuccessResponse(data=InteractionResponse.model_validate(interaction))


@router.patch(
    "/{interaction_id}",
    response_model=SuccessResponse[InteractionResponse],
    summary="Update an interaction",
    description="Updates an existing interaction. Terminal-status interactions are read-only.",
)
async def update_interaction(
    interaction_id: uuid.UUID,
    body: InteractionUpdate,
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[InteractionResponse]:
    interaction, _ = await service.update_interaction(interaction_id, body)
    return SuccessResponse(data=InteractionResponse.model_validate(interaction))


@router.post(
    "/{interaction_id}/close",
    response_model=SuccessResponse[InteractionResponse],
    summary="Close an interaction",
    description="Transitions an interaction to COMPLETED status.",
)
async def close_interaction(
    interaction_id: uuid.UUID,
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[InteractionResponse]:
    interaction, _ = await service.close_interaction(interaction_id)
    return SuccessResponse(data=InteractionResponse.model_validate(interaction))


@router.post(
    "/{interaction_id}/archive",
    response_model=SuccessResponse[InteractionResponse],
    summary="Archive an interaction",
    description="Transitions an interaction to ARCHIVED status.",
)
async def archive_interaction(
    interaction_id: uuid.UUID,
    service: InteractionService = Depends(get_interaction_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[InteractionResponse]:
    interaction, _ = await service.archive_interaction(interaction_id)
    return SuccessResponse(data=InteractionResponse.model_validate(interaction))


# End of Router

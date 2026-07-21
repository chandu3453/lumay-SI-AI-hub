"""Agent Assist REST API — additive-only, nested under /conversations
(Sprint 28 Phase 5). Three endpoints: read the latest insight, read the
sentiment/intent history (trend), and force a regeneration."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.agent_assist import get_agent_assist_service
from app.dependencies.auth import CurrentUser, get_current_active_user, get_current_user
from app.dependencies.conversation import get_conversation_service
from app.dependencies.database import get_db
from domains.agent_assist.schemas.agent_assist_schemas import (
    AgentAssistEmptyResponse,
    AgentAssistHistoryItem,
    AgentAssistInsightResponse,
)
from domains.agent_assist.services.agent_assist_service import (
    AgentAssistService,
    regenerate_agent_assist_insight,
)
from domains.conversation.services.conversation_service import ConversationService
from shared.response_schemas import SuccessResponse

router = APIRouter(prefix="/conversations", tags=["Agent Assist"])


@router.get(
    "/{conversation_id}/agent-assist",
    response_model=SuccessResponse[AgentAssistInsightResponse | AgentAssistEmptyResponse],
    summary="Latest AI Agent Assist insight for a conversation",
    description="Summary, intent, sentiment, next-best-action, knowledge suggestions, "
    "suggested replies, conversation insights, and alerts — regenerated automatically "
    "as the conversation evolves (throttled, not on every message). Returns an "
    "empty/not-yet-generated shape if no insight exists yet.",
)
async def get_agent_assist_insight(
    conversation_id: uuid.UUID,
    conversation_service: ConversationService = Depends(get_conversation_service),
    service: AgentAssistService = Depends(get_agent_assist_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[AgentAssistInsightResponse | AgentAssistEmptyResponse]:
    conversation = await conversation_service.get_conversation(conversation_id)  # 404s if missing
    insight = await service.get_latest(conversation)
    if insight is None:
        return SuccessResponse(data=AgentAssistEmptyResponse(conversation_id=conversation_id))
    return SuccessResponse(data=insight)


@router.get(
    "/{conversation_id}/agent-assist/history",
    response_model=SuccessResponse[list[AgentAssistHistoryItem]],
    summary="Sentiment/intent trend over time",
    description="Chronological projection of past insight generations — powers the "
    "sentiment trend and intent-change tracking in the panel.",
)
async def get_agent_assist_history(
    conversation_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    conversation_service: ConversationService = Depends(get_conversation_service),
    service: AgentAssistService = Depends(get_agent_assist_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[list[AgentAssistHistoryItem]]:
    await conversation_service.get_conversation(conversation_id)  # 404s if missing
    history = await service.get_history(conversation_id, limit=limit)
    return SuccessResponse(data=history)


@router.post(
    "/{conversation_id}/agent-assist/regenerate",
    response_model=SuccessResponse[AgentAssistInsightResponse | AgentAssistEmptyResponse],
    summary="Force-regenerate the Agent Assist insight",
    description="Employee-triggered manual refresh — bypasses the automatic throttle.",
)
async def regenerate_agent_assist(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    conversation_service: ConversationService = Depends(get_conversation_service),
    service: AgentAssistService = Depends(get_agent_assist_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[AgentAssistInsightResponse | AgentAssistEmptyResponse]:
    conversation = await conversation_service.get_conversation(conversation_id)  # 404s if missing
    await regenerate_agent_assist_insight(db, conversation_id, force=True)
    insight = await service.get_latest(conversation)
    if insight is None:
        return SuccessResponse(data=AgentAssistEmptyResponse(conversation_id=conversation_id))
    return SuccessResponse(data=insight)

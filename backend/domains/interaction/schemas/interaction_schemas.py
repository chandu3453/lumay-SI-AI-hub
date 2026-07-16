"""Interaction Pydantic schemas."""

import uuid
from datetime import datetime
from typing import Any

from shared.base_schema import AppBaseModel, EntitySchema

from domains.interaction.constants.interaction_constants import (
    InteractionChannel,
    InteractionDirection,
    InteractionStatus,
)


class InteractionCreate(AppBaseModel):
    customer_ref: str | None = None
    channel: InteractionChannel
    direction: InteractionDirection = InteractionDirection.INBOUND
    subject: str | None = None
    transcript: str | None = None
    attachments: list[str] | None = None


class InteractionUpdate(AppBaseModel):
    subject: str | None = None
    transcript: str | None = None
    attachments: list[str] | None = None
    status: InteractionStatus | None = None


class InteractionResponse(EntitySchema):
    customer_ref: str | None = None
    channel: InteractionChannel
    direction: InteractionDirection
    subject: str | None = None
    transcript: str | None = None
    attachments: list[str] | None = None
    status: InteractionStatus


class InteractionSummary(AppBaseModel):
    id: uuid.UUID
    customer_ref: str | None = None
    channel: InteractionChannel
    direction: InteractionDirection
    subject: str | None = None
    status: InteractionStatus
    created_at: datetime


class ChatStartRequest(AppBaseModel):
    customer_ref: str | None = None
    channel: InteractionChannel = InteractionChannel.WHATSAPP
    complaint_id: uuid.UUID | None = None


class ChatMessageRequest(AppBaseModel):
    interaction_id: uuid.UUID
    message: str


class ChatMessageResponse(AppBaseModel):
    role: str
    content: str
    timestamp: datetime


class ChatResponsePayload(AppBaseModel):
    answer: str
    messages: list[ChatMessageResponse]
    ai_analysis: dict[str, Any] | None = None
    context_used: bool = False
    auto_triaged: bool = False
    complaint_id: uuid.UUID | None = None
    workflow_id: uuid.UUID | None = None
    provider_used: str = "unknown"

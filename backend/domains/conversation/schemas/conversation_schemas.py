"""Conversation Pydantic schemas."""

import uuid
from datetime import datetime
from typing import Any

from shared.base_schema import AppBaseModel, EntitySchema

from domains.conversation.constants.conversation_constants import (
    ConversationChannel,
    ConversationMessageType,
    ConversationParticipantType,
    ConversationPriority,
    ConversationStatus,
)


class ConversationCreate(AppBaseModel):
    customer_id: uuid.UUID | None = None
    policy_id: uuid.UUID | None = None
    complaint_id: uuid.UUID | None = None
    current_channel: ConversationChannel
    current_status: ConversationStatus = ConversationStatus.NEW
    priority: ConversationPriority = ConversationPriority.MEDIUM


class ConversationUpdate(AppBaseModel):
    current_status: ConversationStatus | None = None
    current_channel: ConversationChannel | None = None
    assigned_employee_id: uuid.UUID | None = None
    policy_id: uuid.UUID | None = None
    complaint_id: uuid.UUID | None = None
    priority: ConversationPriority | None = None


class ConversationResponse(EntitySchema):
    customer_id: uuid.UUID | None = None
    policy_id: uuid.UUID | None = None
    complaint_id: uuid.UUID | None = None
    current_status: ConversationStatus
    current_channel: ConversationChannel
    assigned_employee_id: uuid.UUID | None = None
    ai_handling: bool
    human_handling: bool
    priority: ConversationPriority


class ConversationSummary(AppBaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID | None = None
    complaint_id: uuid.UUID | None = None
    current_status: ConversationStatus
    current_channel: ConversationChannel
    assigned_employee_id: uuid.UUID | None = None
    priority: ConversationPriority
    updated_at: datetime
    # Batched enrichment (Sprint 28 Phase 3) — not columns on Conversation
    # itself, filled in by the list endpoint from two small batched lookups.
    customer_name: str | None = None
    last_message_preview: str | None = None


class AssignEmployeeRequest(AppBaseModel):
    employee_id: uuid.UUID


class UpdateStatusRequest(AppBaseModel):
    status: ConversationStatus


class SetPriorityRequest(AppBaseModel):
    priority: ConversationPriority


class MessageCreate(AppBaseModel):
    sender_type: ConversationParticipantType
    channel: ConversationChannel
    message_type: ConversationMessageType = ConversationMessageType.TEXT
    content: str
    metadata: dict[str, Any] | None = None


class MessageResponse(EntitySchema):
    conversation_id: uuid.UUID
    sender_type: ConversationParticipantType
    channel: ConversationChannel
    message_type: ConversationMessageType
    content: str
    message_metadata: dict[str, Any] | None = None


class ParticipantResponse(EntitySchema):
    conversation_id: uuid.UUID
    participant_type: ConversationParticipantType
    participant_ref: str | None = None
    role: str | None = None
    joined_at: datetime
    left_at: datetime | None = None


class ChannelLinkResponse(EntitySchema):
    conversation_id: uuid.UUID
    channel: ConversationChannel
    external_ref_type: str
    external_ref_id: str
    is_primary: bool


class EventResponse(EntitySchema):
    conversation_id: uuid.UUID
    event_type: str
    source_domain: str
    payload: dict[str, Any] | None = None


class EventCreate(AppBaseModel):
    event_type: str
    source_domain: str = "system"
    payload: dict[str, Any] | None = None


class ConversationStatusResponse(AppBaseModel):
    id: uuid.UUID
    current_status: ConversationStatus
    ai_handling: bool
    human_handling: bool
    assigned_employee_id: uuid.UUID | None = None


class TimelineItem(AppBaseModel):
    """A merged, chronologically-sortable view over messages + events —
    `type` discriminates which of the two shapes populated the item."""

    type: str  # "message" | "event"
    id: uuid.UUID
    timestamp: datetime
    sender_type: ConversationParticipantType | None = None
    channel: ConversationChannel | None = None
    message_type: ConversationMessageType | None = None
    content: str | None = None
    event_type: str | None = None
    source_domain: str | None = None
    payload: dict[str, Any] | None = None


# ── Phase 4 — ownership, notes, presence/typing ──────────────────────────

class MessageUpdateRequest(AppBaseModel):
    content: str


class SupervisorActionRequest(AppBaseModel):
    supervisor_id: uuid.UUID


class PresenceUpdateRequest(AppBaseModel):
    participant_type: ConversationParticipantType
    participant_ref: str
    status: str  # "online" | "offline"


class TypingUpdateRequest(AppBaseModel):
    participant_type: ConversationParticipantType
    is_typing: bool


class PresenceSnapshotResponse(AppBaseModel):
    presence: dict[str, dict[str, str]]
    typing: dict[str, bool]
    ai_active: bool
    conversation_live: bool
    voice_active: bool

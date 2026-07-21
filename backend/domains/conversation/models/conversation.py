"""Conversation ORM model — the unified parent entity for all customer channels."""

import uuid

from sqlalchemy import Boolean, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.database.base import AuditModel
from domains.conversation.constants.conversation_constants import (
    ConversationChannel,
    ConversationPriority,
    ConversationStatus,
)


class Conversation(AuditModel):
    __tablename__ = "conversations"

    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    policy_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    complaint_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    current_status: Mapped[ConversationStatus] = mapped_column(
        SAEnum(ConversationStatus, name="conversation_status", create_constraint=True),
        nullable=False,
        default=ConversationStatus.NEW,
        index=True,
    )
    current_channel: Mapped[ConversationChannel] = mapped_column(
        SAEnum(ConversationChannel, name="conversation_channel", create_constraint=True),
        nullable=False,
    )
    assigned_employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    ai_handling: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    human_handling: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    priority: Mapped[ConversationPriority] = mapped_column(
        SAEnum(ConversationPriority, name="conversation_priority", create_constraint=True),
        nullable=False,
        default=ConversationPriority.MEDIUM,
        index=True,
    )

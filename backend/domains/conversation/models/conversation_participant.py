"""ConversationParticipant ORM model — who has been part of a conversation."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.database.base import AuditModel
from domains.conversation.constants.conversation_constants import ConversationParticipantType


class ConversationParticipant(AuditModel):
    __tablename__ = "conversation_participants"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    participant_type: Mapped[ConversationParticipantType] = mapped_column(
        SAEnum(
            ConversationParticipantType,
            name="conversation_participant_type",
            create_constraint=True,
        ),
        nullable=False,
    )
    participant_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str | None] = mapped_column(String(50), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

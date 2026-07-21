"""ConversationMessage ORM model — every message/transcript/event inside a conversation."""

import uuid

from sqlalchemy import Enum as SAEnum, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.database.base import AuditModel
from domains.conversation.constants.conversation_constants import (
    ConversationChannel,
    ConversationMessageType,
    ConversationParticipantType,
)


class ConversationMessage(AuditModel):
    __tablename__ = "conversation_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender_type: Mapped[ConversationParticipantType] = mapped_column(
        SAEnum(
            ConversationParticipantType,
            name="conversation_message_sender_type",
            create_constraint=True,
        ),
        nullable=False,
    )
    channel: Mapped[ConversationChannel] = mapped_column(
        SAEnum(ConversationChannel, name="conversation_message_channel", create_constraint=True),
        nullable=False,
    )
    message_type: Mapped[ConversationMessageType] = mapped_column(
        SAEnum(ConversationMessageType, name="conversation_message_type", create_constraint=True),
        nullable=False,
        default=ConversationMessageType.TEXT,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

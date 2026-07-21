"""ConversationChannel ORM model — bridges a conversation to existing per-channel
records (Interaction rows, voice session ids, complaint ids) without touching
those tables. `(external_ref_type, external_ref_id)` is the reverse lookup key
every integration hook uses to resolve an existing touchpoint to its conversation.
"""

import uuid

from sqlalchemy import Boolean, Enum as SAEnum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.database.base import AuditModel
from domains.conversation.constants.conversation_constants import ConversationChannel as ChannelEnum


class ConversationChannelLink(AuditModel):
    __tablename__ = "conversation_channels"
    __table_args__ = (
        UniqueConstraint("external_ref_type", "external_ref_id", name="uq_conversation_channel_ref"),
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel: Mapped[ChannelEnum] = mapped_column(
        SAEnum(ChannelEnum, name="conversation_channel_link_channel", create_constraint=True),
        nullable=False,
    )
    external_ref_type: Mapped[str] = mapped_column(String(50), nullable=False)
    external_ref_id: Mapped[str] = mapped_column(String(255), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

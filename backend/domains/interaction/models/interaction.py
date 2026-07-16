"""Interaction ORM model."""

import uuid

import json

from sqlalchemy import Enum as SAEnum, String, Text, TypeDecorator, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from domains.interaction.constants.interaction_constants import (
    InteractionChannel,
    InteractionDirection,
    InteractionStatus,
)
from app.platform.database.base import AuditModel


class JsonStringList(TypeDecorator):
    impl = String
    cache_ok = True

    def process_result_value(self, value, dialect):  # noqa: ARG002
        if value is None:
            return None
        return json.loads(value) if isinstance(value, str) else value

    def process_bind_param(self, value, dialect):  # noqa: ARG002
        if value is None:
            return None
        return json.dumps(value)


class Interaction(AuditModel):
    __tablename__ = "interactions"

    customer_ref: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    channel: Mapped[InteractionChannel] = mapped_column(
        SAEnum(InteractionChannel, name="interaction_channel", create_constraint=True),
        nullable=False,
    )
    direction: Mapped[InteractionDirection] = mapped_column(
        SAEnum(InteractionDirection, name="interaction_direction", create_constraint=True),
        nullable=False,
        default=InteractionDirection.INBOUND,
    )
    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachments: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True, default=list
    )
    status: Mapped[InteractionStatus] = mapped_column(
        SAEnum(InteractionStatus, name="interaction_status", create_constraint=True),
        nullable=False,
        default=InteractionStatus.RECEIVED,
        index=True,
    )

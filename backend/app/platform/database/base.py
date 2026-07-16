"""
SQLAlchemy Declarative Base.

All ORM models must inherit from Base.
Provides shared column conventions (UUID PK, timestamps, soft delete).
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Declarative base class for all ORM models.
    Centralises table naming and type annotation configuration.
    """

    type_annotation_map: dict[type, type] = {
        str: String,
        uuid.UUID: UUID(as_uuid=True),
    }


class TimestampMixin:
    """Adds immutable created_at and auto-updating updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Adds logical deletion support via is_deleted flag."""

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UUIDPrimaryKeyMixin:
    """Mixin that sets a UUID v4 as the primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )


class AuditMixin(UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Composite mixin combining UUID PK and timestamps.
    Standard base for all domain entities.
    """


class AuditModel(Base, TimestampMixin):
    """
    Abstract base for all domain entity models.
    Provides UUID PK + audit timestamps.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

"""
SQLAlchemy ORM Base Model.

All domain ORM models inherit from AuditModel which provides
UUID primary key, created_at, updated_at, and soft-delete support.

This module re-exports the canonical base classes from the platform layer.
"""

from app.platform.database.base import (
    AuditModel,
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

__all__ = [
    "AuditModel",
    "Base",
    "SoftDeleteMixin",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
]

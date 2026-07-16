"""
Pydantic Base Schemas.

All domain schemas inherit from these bases.
Provides consistent serialisation config across the platform.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    """Base Pydantic model with shared configuration."""

    model_config = ConfigDict(
        from_attributes=True,      # enables ORM mode
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )


class TimestampSchema(AppBaseModel):
    """Mixin that exposes audit timestamp fields in responses."""

    created_at: datetime
    updated_at: datetime


class EntitySchema(TimestampSchema):
    """Base response schema for any entity with a UUID primary key."""

    id: uuid.UUID

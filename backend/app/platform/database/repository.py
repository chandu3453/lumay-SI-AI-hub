"""
Generic Async Repository Base.

Provides a typed, reusable base repository for all domain repositories.
Domain-specific repositories extend this class and add query methods.
Follows the Repository pattern to decouple domain logic from data access.
"""

import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Generic async repository providing basic CRUD scaffolding.

    Args:
        model: The SQLAlchemy ORM model class.
        session: An active async database session.
    """

    def __init__(self, model: type[ModelT], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def get_by_id(self, entity_id: uuid.UUID) -> ModelT | None:
        """Fetches a single entity by its primary key."""
        result = await self._session.execute(
            select(self._model).where(self._model.id == entity_id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def add(self, entity: ModelT) -> ModelT:
        """Persists a new entity to the session (does not commit)."""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity: ModelT) -> None:
        """Removes an entity from the session (does not commit)."""
        await self._session.delete(entity)
        await self._session.flush()

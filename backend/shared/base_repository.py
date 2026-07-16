"""
Generic Async Repository Base.

All domain repositories extend BaseRepository[ModelT].
Provides typed scaffolding over SQLAlchemy AsyncSession.
Domain repositories add query methods — never raw SQL outside repositories.
"""

import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.base_model import AuditModel

ModelT = TypeVar("ModelT", bound=AuditModel)


class BaseRepository(Generic[ModelT]):
    """
    Generic async CRUD base for domain repositories.

    Usage:
        class ComplaintRepository(BaseRepository[Complaint]):
            def __init__(self, session: AsyncSession) -> None:
                super().__init__(Complaint, session)
    """

    def __init__(self, model: type[ModelT], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    async def get_by_id(self, entity_id: uuid.UUID) -> ModelT | None:
        """Returns the entity with the given PK, or None."""
        result = await self._session.execute(
            select(self._model).where(self._model.id == entity_id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def add(self, entity: ModelT) -> ModelT:
        """Persists a new entity and flushes to obtain DB-generated values."""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity: ModelT) -> None:
        """Hard-deletes an entity from the session."""
        await self._session.delete(entity)
        await self._session.flush()

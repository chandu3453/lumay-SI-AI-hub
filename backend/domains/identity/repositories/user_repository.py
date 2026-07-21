"""User Repository — Identity domain."""

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.identity.models.user import User
from shared.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.email == email, User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        result = await self._session.execute(
            select(User.id).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def list_by_ids(self, ids: Sequence[uuid.UUID]) -> Sequence[User]:
        """Sprint 29 — batch name resolution for `assigned_employee_id`
        UUIDs shown throughout the Conversation/Reporting domains, which
        carry no FK to `users` (cross-domain by convention in this codebase)."""
        if not ids:
            return []
        result = await self._session.execute(select(User).where(User.id.in_(ids)))
        return result.scalars().all()

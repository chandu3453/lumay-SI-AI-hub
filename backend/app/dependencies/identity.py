"""Identity domain dependency injection."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from domains.identity.repositories.user_repository import UserRepository


async def get_user_repository(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[UserRepository, None]:
    yield UserRepository(session=db)

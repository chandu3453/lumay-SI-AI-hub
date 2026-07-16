"""Interaction domain dependency injection."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from domains.interaction.repositories.interaction_repository import InteractionRepository
from domains.interaction.services.interaction_service import InteractionService


async def get_interaction_repository(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[InteractionRepository, None]:
    yield InteractionRepository(session=db)


async def get_interaction_service(
    repository: InteractionRepository = Depends(get_interaction_repository),
) -> AsyncGenerator[InteractionService, None]:
    yield InteractionService(repository=repository)

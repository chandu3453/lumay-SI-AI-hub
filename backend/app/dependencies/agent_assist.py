"""Agent Assist domain dependency injection."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from domains.agent_assist.repositories.agent_assist_repository import AgentAssistRepository
from domains.agent_assist.services.agent_assist_service import AgentAssistService


async def get_agent_assist_repository(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[AgentAssistRepository, None]:
    yield AgentAssistRepository(session=db)


async def get_agent_assist_service(
    repository: AgentAssistRepository = Depends(get_agent_assist_repository),
) -> AsyncGenerator[AgentAssistService, None]:
    yield AgentAssistService(repository=repository)

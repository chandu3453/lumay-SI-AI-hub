"""Reporting domain dependency injection."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from domains.agent_assist.repositories.agent_assist_repository import AgentAssistRepository
from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.conversation.repositories.conversation_repository import ConversationRepository
from domains.conversation.repositories.event_repository import ConversationEventRepository
from domains.conversation.repositories.message_repository import ConversationMessageRepository
from domains.customer.repositories.customer_repository import CustomerRepository
from domains.identity.repositories.user_repository import UserRepository
from domains.reporting.services.reporting_service import ReportingService


async def get_reporting_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ReportingService, None]:
    yield ReportingService(
        conversation_repository=ConversationRepository(session=db),
        event_repository=ConversationEventRepository(session=db),
        message_repository=ConversationMessageRepository(session=db),
        agent_assist_repository=AgentAssistRepository(session=db),
        complaint_repository=ComplaintRepository(session=db),
        customer_repository=CustomerRepository(session=db),
        user_repository=UserRepository(session=db),
    )

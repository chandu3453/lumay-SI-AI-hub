"""Conversation domain dependency injection."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from domains.conversation.repositories.channel_repository import ConversationChannelRepository
from domains.conversation.repositories.conversation_repository import ConversationRepository
from domains.conversation.repositories.event_repository import ConversationEventRepository
from domains.conversation.repositories.message_repository import ConversationMessageRepository
from domains.conversation.repositories.participant_repository import (
    ConversationParticipantRepository,
)
from domains.conversation.services.conversation_factory import ConversationFactory
from domains.conversation.services.conversation_service import ConversationService
from domains.conversation.services.event_service import ConversationEventService
from domains.conversation.services.message_service import MessageService
from domains.conversation.services.participant_service import ConversationParticipantService


async def get_conversation_repository(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ConversationRepository, None]:
    yield ConversationRepository(session=db)


async def get_conversation_service(
    repository: ConversationRepository = Depends(get_conversation_repository),
) -> AsyncGenerator[ConversationService, None]:
    yield ConversationService(repository=repository)


async def get_message_repository(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ConversationMessageRepository, None]:
    yield ConversationMessageRepository(session=db)


async def get_message_service(
    repository: ConversationMessageRepository = Depends(get_message_repository),
) -> AsyncGenerator[MessageService, None]:
    yield MessageService(repository=repository)


async def get_conversation_channel_repository(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ConversationChannelRepository, None]:
    yield ConversationChannelRepository(session=db)


async def get_conversation_participant_repository(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ConversationParticipantRepository, None]:
    yield ConversationParticipantRepository(session=db)


async def get_conversation_event_repository(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ConversationEventRepository, None]:
    yield ConversationEventRepository(session=db)


async def get_conversation_event_service(
    repository: ConversationEventRepository = Depends(get_conversation_event_repository),
) -> AsyncGenerator[ConversationEventService, None]:
    yield ConversationEventService(repository=repository)


async def get_conversation_participant_service(
    repository: ConversationParticipantRepository = Depends(
        get_conversation_participant_repository
    ),
) -> AsyncGenerator[ConversationParticipantService, None]:
    yield ConversationParticipantService(repository=repository)


async def get_conversation_factory(
    conversation_repository: ConversationRepository = Depends(get_conversation_repository),
    conversation_service: ConversationService = Depends(get_conversation_service),
    channel_repository: ConversationChannelRepository = Depends(
        get_conversation_channel_repository
    ),
    participant_repository: ConversationParticipantRepository = Depends(
        get_conversation_participant_repository
    ),
) -> AsyncGenerator[ConversationFactory, None]:
    yield ConversationFactory(
        conversation_repository=conversation_repository,
        conversation_service=conversation_service,
        channel_repository=channel_repository,
        participant_repository=participant_repository,
    )

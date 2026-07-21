"""ConversationFactory — the business-rule seam for Phase 1's core goal:

    Every customer interaction must belong to ONE unified conversation,
    regardless of channel.

Merge rule (cross-channel, by customer): reuse the customer's most recently
updated conversation if it is not in a terminal status (RESOLVED/CLOSED) and
was touched within `DEFAULT_INACTIVITY_WINDOW_MINUTES`. Otherwise start a new
conversation. A customer moving from webchat to a voice call within the window
attaches to the same conversation; the channel touchpoint is always recorded
via `ConversationChannelLink` so the origin of every message stays traceable.
"""

import uuid
from datetime import UTC, datetime, timedelta

from domains.conversation.constants.conversation_constants import (
    ConversationChannel,
    ConversationParticipantType,
    ConversationStatus,
    DEFAULT_INACTIVITY_WINDOW_MINUTES,
)
from domains.conversation.models.conversation import Conversation
from domains.conversation.repositories.channel_repository import ConversationChannelRepository
from domains.conversation.repositories.conversation_repository import ConversationRepository
from domains.conversation.repositories.participant_repository import (
    ConversationParticipantRepository,
)
from domains.conversation.schemas.conversation_schemas import ConversationCreate
from domains.conversation.services.conversation_service import ConversationService
from app.platform.logging import get_logger
from shared.base_service import BaseService

logger = get_logger(__name__)


class ConversationFactory(BaseService):
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        conversation_service: ConversationService,
        channel_repository: ConversationChannelRepository,
        participant_repository: ConversationParticipantRepository,
        inactivity_window_minutes: int = DEFAULT_INACTIVITY_WINDOW_MINUTES,
    ) -> None:
        self._conversation_repository = conversation_repository
        self._conversation_service = conversation_service
        self._channel_repository = channel_repository
        self._participant_repository = participant_repository
        self._inactivity_window_minutes = inactivity_window_minutes

    async def get_or_create(
        self,
        *,
        customer_id: uuid.UUID | None,
        channel: ConversationChannel,
        policy_id: uuid.UUID | None = None,
        complaint_id: uuid.UUID | None = None,
        external_ref_type: str | None = None,
        external_ref_id: str | None = None,
    ) -> tuple[Conversation, bool]:
        now = datetime.now(UTC)
        existing: Conversation | None = None
        if customer_id is not None:
            since = now - timedelta(minutes=self._inactivity_window_minutes)
            existing = await self._conversation_repository.get_active_by_customer(
                customer_id, since=since
            )

        created = False
        if existing is not None:
            conversation = existing
            if channel != conversation.current_channel:
                conversation = await self._conversation_service.set_current_channel(
                    conversation.id, channel
                )
            if complaint_id is not None and conversation.complaint_id is None:
                conversation = await self._conversation_service.link_complaint(
                    conversation.id, complaint_id
                )
        else:
            data = ConversationCreate(
                customer_id=customer_id,
                policy_id=policy_id,
                complaint_id=complaint_id,
                current_channel=channel,
                current_status=ConversationStatus.NEW,
            )
            conversation, _ = await self._conversation_service.create_conversation(data)
            created = True
            await self._seed_participants(conversation.id, customer_id, now)
            logger.info(
                "conversation_factory_created_new",
                conversation_id=str(conversation.id),
                customer_id=str(customer_id) if customer_id else None,
                channel=channel,
            )

        if external_ref_type and external_ref_id:
            await self._ensure_channel_link(
                conversation.id, channel, external_ref_type, external_ref_id, is_primary=created
            )

        return conversation, created

    async def _seed_participants(
        self, conversation_id: uuid.UUID, customer_id: uuid.UUID | None, joined_at: datetime
    ) -> None:
        await self._participant_repository.create(
            conversation_id=conversation_id,
            participant_type=ConversationParticipantType.CUSTOMER,
            participant_ref=str(customer_id) if customer_id else None,
            joined_at=joined_at,
        )
        await self._participant_repository.create(
            conversation_id=conversation_id,
            participant_type=ConversationParticipantType.AI,
            participant_ref="ai-system",
            joined_at=joined_at,
        )

    async def _ensure_channel_link(
        self,
        conversation_id: uuid.UUID,
        channel: ConversationChannel,
        external_ref_type: str,
        external_ref_id: str,
        *,
        is_primary: bool,
    ) -> None:
        existing_link = await self._channel_repository.get_by_external_ref(
            external_ref_type, external_ref_id
        )
        if existing_link is None:
            await self._channel_repository.create(
                conversation_id=conversation_id,
                channel=channel,
                external_ref_type=external_ref_type,
                external_ref_id=external_ref_id,
                is_primary=is_primary,
            )

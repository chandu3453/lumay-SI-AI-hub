"""ConversationFactory unit tests — the cross-channel merge business rule."""

import uuid

import pytest

from domains.conversation.constants.conversation_constants import ConversationChannel
from domains.conversation.services.conversation_factory import ConversationFactory


@pytest.fixture
def deps(mocker):
    return {
        "conversation_repository": mocker.AsyncMock(),
        "conversation_service": mocker.AsyncMock(),
        "channel_repository": mocker.AsyncMock(),
        "participant_repository": mocker.AsyncMock(),
    }


@pytest.fixture
def factory(deps) -> ConversationFactory:
    return ConversationFactory(**deps)


@pytest.mark.asyncio
class TestConversationFactory:
    async def test_creates_new_conversation_when_none_active(
        self, factory: ConversationFactory, deps, mocker,
    ) -> None:
        customer_id = uuid.uuid4()
        deps["conversation_repository"].get_active_by_customer.return_value = None
        new_conversation = mocker.Mock(id=uuid.uuid4(), current_channel=ConversationChannel.WEB_CHAT)
        deps["conversation_service"].create_conversation.return_value = (new_conversation, [])
        deps["channel_repository"].get_by_external_ref.return_value = None

        conversation, created = await factory.get_or_create(
            customer_id=customer_id,
            channel=ConversationChannel.WEB_CHAT,
            external_ref_type="interaction_id",
            external_ref_id="abc-123",
        )

        assert created is True
        assert conversation is new_conversation
        deps["conversation_service"].create_conversation.assert_awaited_once()
        # Seeds a CUSTOMER + AI participant.
        assert deps["participant_repository"].create.await_count == 2
        deps["channel_repository"].create.assert_awaited_once()

    async def test_reuses_active_conversation_for_same_customer_cross_channel(
        self, factory: ConversationFactory, deps, mocker,
    ) -> None:
        customer_id = uuid.uuid4()
        existing = mocker.Mock(
            id=uuid.uuid4(), current_channel=ConversationChannel.WEB_CHAT, complaint_id=None,
        )
        deps["conversation_repository"].get_active_by_customer.return_value = existing
        switched = mocker.Mock(id=existing.id, current_channel=ConversationChannel.VOICE, complaint_id=None)
        deps["conversation_service"].set_current_channel.return_value = switched
        deps["channel_repository"].get_by_external_ref.return_value = None

        # Customer started on webchat, now switches to a voice call.
        conversation, created = await factory.get_or_create(
            customer_id=customer_id,
            channel=ConversationChannel.VOICE,
            external_ref_type="interaction_id",
            external_ref_id="voice-session-1",
        )

        assert created is False
        deps["conversation_service"].create_conversation.assert_not_awaited()
        deps["conversation_service"].set_current_channel.assert_awaited_once_with(
            existing.id, ConversationChannel.VOICE
        )
        assert conversation.current_channel == ConversationChannel.VOICE

    async def test_links_complaint_when_reusing_conversation_without_one(
        self, factory: ConversationFactory, deps, mocker,
    ) -> None:
        customer_id = uuid.uuid4()
        complaint_id = uuid.uuid4()
        existing = mocker.Mock(
            id=uuid.uuid4(), current_channel=ConversationChannel.COMPLAINT, complaint_id=None,
        )
        deps["conversation_repository"].get_active_by_customer.return_value = existing
        linked = mocker.Mock(id=existing.id, current_channel=ConversationChannel.COMPLAINT, complaint_id=complaint_id)
        deps["conversation_service"].link_complaint.return_value = linked
        deps["channel_repository"].get_by_external_ref.return_value = None

        conversation, created = await factory.get_or_create(
            customer_id=customer_id,
            channel=ConversationChannel.COMPLAINT,
            complaint_id=complaint_id,
        )

        assert created is False
        deps["conversation_service"].link_complaint.assert_awaited_once_with(existing.id, complaint_id)
        assert conversation.complaint_id == complaint_id

    async def test_does_not_duplicate_existing_channel_link(
        self, factory: ConversationFactory, deps, mocker,
    ) -> None:
        deps["conversation_repository"].get_active_by_customer.return_value = None
        new_conversation = mocker.Mock(id=uuid.uuid4(), current_channel=ConversationChannel.WEB_CHAT)
        deps["conversation_service"].create_conversation.return_value = (new_conversation, [])
        deps["channel_repository"].get_by_external_ref.return_value = mocker.Mock()  # already linked

        await factory.get_or_create(
            customer_id=uuid.uuid4(),
            channel=ConversationChannel.WEB_CHAT,
            external_ref_type="interaction_id",
            external_ref_id="abc-123",
        )

        deps["channel_repository"].create.assert_not_awaited()

    async def test_anonymous_customer_always_creates_new(
        self, factory: ConversationFactory, deps, mocker,
    ) -> None:
        new_conversation = mocker.Mock(id=uuid.uuid4(), current_channel=ConversationChannel.WEB_CHAT)
        deps["conversation_service"].create_conversation.return_value = (new_conversation, [])
        deps["channel_repository"].get_by_external_ref.return_value = None

        conversation, created = await factory.get_or_create(
            customer_id=None, channel=ConversationChannel.WEB_CHAT
        )

        assert created is True
        deps["conversation_repository"].get_active_by_customer.assert_not_awaited()

"""Conversation domain integration flow tests (Sprint 28 Phase 1).

Covers both halves of the foundation:
  1. The new `/api/v1/conversations` CRUD surface, standalone.
  2. The integration hooks that link existing channels (webchat, voice,
     manual complaint filing) into a unified Conversation — including the
     cross-channel merge rule and the exact gap identified earlier in this
     project (a manually-filed complaint previously had no linked transcript).
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ai.models import AIResponse, ChatMessage, ChatResponse, TokenUsage

from domains.conversation import integration_hooks as conversation_hooks
from domains.conversation.constants.conversation_constants import (
    ConversationChannel,
    ConversationMessageType,
    ConversationStatus,
)
from domains.conversation.repositories.channel_repository import ConversationChannelRepository
from domains.conversation.repositories.event_repository import ConversationEventRepository
from domains.conversation.repositories.message_repository import ConversationMessageRepository
from domains.interaction.constants.interaction_constants import (
    InteractionChannel,
    InteractionDirection,
)
from domains.interaction.repositories.interaction_repository import InteractionRepository
from domains.interaction.schemas.interaction_schemas import InteractionCreate
from domains.interaction.services.interaction_service import InteractionService


@pytest.mark.asyncio
class TestConversationApiCrudFlow:
    """The new /api/v1/conversations surface, standalone (no hooks involved)."""

    async def test_full_api_flow(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/conversations",
            json={"current_channel": "web_chat"},
        )
        assert create_resp.status_code == 201
        conversation_id = create_resp.json()["data"]["id"]
        assert create_resp.json()["data"]["current_status"] == "new"

        get_resp = await client.get(f"/api/v1/conversations/{conversation_id}")
        assert get_resp.status_code == 200

        status_resp = await client.patch(
            f"/api/v1/conversations/{conversation_id}/status",
            json={"status": "ai_handling"},
        )
        assert status_resp.status_code == 200
        assert status_resp.json()["data"]["current_status"] == "ai_handling"
        assert status_resp.json()["data"]["ai_handling"] is True

        employee_id = str(uuid.uuid4())
        assign_resp = await client.post(
            f"/api/v1/conversations/{conversation_id}/assign",
            json={"employee_id": employee_id},
        )
        assert assign_resp.status_code == 200
        assert assign_resp.json()["data"]["assigned_employee_id"] == employee_id

        message_resp = await client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={"sender_type": "customer", "channel": "web_chat", "content": "Hello there"},
        )
        assert message_resp.status_code == 201

        messages_resp = await client.get(f"/api/v1/conversations/{conversation_id}/messages")
        assert messages_resp.status_code == 200
        assert len(messages_resp.json()["data"]) == 1
        assert messages_resp.json()["data"][0]["content"] == "Hello there"

        list_resp = await client.get("/api/v1/conversations")
        assert list_resp.status_code == 200
        ids = [c["id"] for c in list_resp.json()["data"]]
        assert conversation_id in ids

        close_resp = await client.post(f"/api/v1/conversations/{conversation_id}/close")
        assert close_resp.status_code == 200
        assert close_resp.json()["data"]["current_status"] == "closed"

        events_resp = await client.get(f"/api/v1/conversations/{conversation_id}/events")
        assert events_resp.status_code == 200

        participants_resp = await client.get(f"/api/v1/conversations/{conversation_id}/participants")
        assert participants_resp.status_code == 200


@pytest.mark.asyncio
class TestIntegrationHooks:
    """Hooks that link existing (unmodified) channel flows into a Conversation."""

    async def test_webchat_start_and_message_creates_linked_conversation(
        self, db_session: AsyncSession,
    ) -> None:
        interaction_service = InteractionService(repository=InteractionRepository(session=db_session))
        interaction, _ = await interaction_service.create_interaction(
            InteractionCreate(
                customer_ref=str(uuid.uuid4()),
                channel=InteractionChannel.WEB_FORM,
                direction=InteractionDirection.INBOUND,
                transcript="[]",
            )
        )

        conversation_id = await conversation_hooks.on_interaction_started(
            db_session,
            interaction.customer_ref,
            "web_form",
            interaction.id,
        )
        assert conversation_id is not None

        await conversation_hooks.on_message(
            db_session, interaction.id, "user", "web_form", "Hello, I need help."
        )
        await conversation_hooks.on_message(
            db_session, interaction.id, "assistant", "web_form", "Sure, how can I help?"
        )

        message_repo = ConversationMessageRepository(session=db_session)
        messages, total = await message_repo.list_by_conversation(conversation_id)
        assert total == 2
        assert messages[0].content == "Hello, I need help."
        assert messages[1].content == "Sure, how can I help?"

        channel_repo = ConversationChannelRepository(session=db_session)
        link = await channel_repo.get_by_external_ref("interaction_id", str(interaction.id))
        assert link is not None
        assert link.conversation_id == conversation_id
        assert link.channel == ConversationChannel.WEB_CHAT

    async def test_cross_channel_merge_reuses_active_conversation(
        self, db_session: AsyncSession,
    ) -> None:
        """A customer moving from webchat to a voice call within the inactivity
        window attaches to the SAME conversation — the sprint's core goal."""
        interaction_service = InteractionService(repository=InteractionRepository(session=db_session))
        customer_ref = str(uuid.uuid4())

        webchat_interaction, _ = await interaction_service.create_interaction(
            InteractionCreate(
                customer_ref=customer_ref, channel=InteractionChannel.WEB_FORM, transcript="[]"
            )
        )
        webchat_conversation_id = await conversation_hooks.on_interaction_started(
            db_session, customer_ref, "web_form", webchat_interaction.id
        )

        voice_interaction, _ = await interaction_service.create_interaction(
            InteractionCreate(
                customer_ref=customer_ref, channel=InteractionChannel.VOICE, transcript="[]"
            )
        )
        voice_conversation_id = await conversation_hooks.on_interaction_started(
            db_session, customer_ref, "voice", voice_interaction.id
        )

        assert webchat_conversation_id == voice_conversation_id

        channel_repo = ConversationChannelRepository(session=db_session)
        links = await channel_repo.list_by_conversation(webchat_conversation_id)
        ref_types = {link.external_ref_id for link in links}
        assert str(webchat_interaction.id) in ref_types
        assert str(voice_interaction.id) in ref_types

    async def test_voice_transcript_segments_become_transcript_messages(
        self, db_session: AsyncSession,
    ) -> None:
        interaction_service = InteractionService(repository=InteractionRepository(session=db_session))
        interaction, _ = await interaction_service.create_interaction(
            InteractionCreate(
                customer_ref=str(uuid.uuid4()), channel=InteractionChannel.VOICE, transcript="[]"
            )
        )
        conversation_id = await conversation_hooks.on_interaction_started(
            db_session, interaction.customer_ref, "voice", interaction.id
        )
        assert conversation_id is not None

        await conversation_hooks.on_message(
            db_session,
            interaction.id,
            "user",
            "voice",
            "I'd like to check my claim status.",
            message_type=ConversationMessageType.TRANSCRIPT,
        )

        message_repo = ConversationMessageRepository(session=db_session)
        messages, total = await message_repo.list_by_conversation(conversation_id)
        assert total == 1
        assert messages[0].message_type == ConversationMessageType.TRANSCRIPT
        assert messages[0].channel == ConversationChannel.VOICE

    async def test_manual_complaint_filing_links_conversation(
        self, db_session: AsyncSession, monkeypatch, test_engine,
    ) -> None:
        """This is the exact gap identified earlier in this project: a complaint
        filed via the customer portal's raise-complaint modal (no prior
        Interaction) previously had no linked conversation/transcript at all.
        `on_complaint_filed_manually` closes it at the foundation level."""
        test_factory = async_sessionmaker(test_engine, expire_on_commit=False)
        monkeypatch.setattr(
            "app.platform.database.session.get_session_factory", lambda: test_factory
        )

        customer_id = uuid.uuid4()
        complaint_id = uuid.uuid4()

        await conversation_hooks.on_complaint_filed_manually(
            customer_id, complaint_id, "COMP-99999"
        )

        async with test_factory() as verify_session:
            from domains.conversation.repositories.conversation_repository import (
                ConversationRepository,
            )

            conversation_repo = ConversationRepository(session=verify_session)
            conversation = await conversation_repo.get_by_complaint_id(complaint_id)
            assert conversation is not None
            assert conversation.customer_id == customer_id
            assert conversation.current_channel == ConversationChannel.COMPLAINT

            event_repo = ConversationEventRepository(session=verify_session)
            events, total = await event_repo.list_by_conversation(conversation.id)
            assert total == 1
            assert events[0].event_type == "complaint.created"
            assert events[0].source_domain == "complaint"

    async def test_real_chat_http_path_creates_conversation_messages(
        self, client: AsyncClient,
    ) -> None:
        """Same request path a browser would hit — through the FastAPI DI-injected
        InteractionService, not a direct hook call — to prove the wiring inside
        `interaction_router.start_chat` and `conversation_engine.process_conversation`
        works end to end."""
        customer_ref = str(uuid.uuid4())
        start_resp = await client.post(
            "/api/v1/interactions/conversations/start",
            json={"customer_ref": customer_ref, "channel": "web_form"},
        )
        assert start_resp.status_code == 201
        interaction_id = start_resp.json()["data"]["id"]

        mock_chat_response = ChatResponse(
            message=ChatMessage(role="assistant", content="Happy to help with that."),
            finish_reason="stop",
            model="gpt-mock",
            usage=TokenUsage(prompt_tokens=5, completion_tokens=5, latency_ms=5.0),
        )
        mock_generate_response = AIResponse(
            content="Mocked RAG answer.",
            finish_reason="stop",
            model="gpt-mock",
            usage=TokenUsage(prompt_tokens=5, completion_tokens=5, latency_ms=5.0),
        )

        with patch(
            "ai.gateway.ai_gateway.AIGateway.chat", new_callable=AsyncMock
        ) as mock_chat, patch(
            "ai.gateway.ai_gateway.AIGateway.generate", new_callable=AsyncMock
        ) as mock_generate:
            mock_chat.return_value = mock_chat_response
            mock_generate.return_value = mock_generate_response

            msg_resp = await client.post(
                "/api/v1/interactions/conversations/message",
                json={"interaction_id": interaction_id, "message": "What's my policy status?"},
            )
        assert msg_resp.status_code == 200

        list_resp = await client.get(f"/api/v1/conversations?customer_id={customer_ref}")
        assert list_resp.status_code == 200
        conversations = list_resp.json()["data"]
        assert len(conversations) == 1
        conversation_id = conversations[0]["id"]

        messages_resp = await client.get(f"/api/v1/conversations/{conversation_id}/messages")
        assert messages_resp.status_code == 200
        messages = messages_resp.json()["data"]
        assert len(messages) == 2
        assert messages[0]["sender_type"] == "customer"
        assert messages[0]["content"] == "What's my policy status?"
        assert messages[1]["sender_type"] == "ai"
        assert messages[1]["content"] == "Happy to help with that."

        channels_resp = await client.get(f"/api/v1/conversations/{conversation_id}/channels")
        assert channels_resp.status_code == 200
        links = channels_resp.json()["data"]
        assert any(link["external_ref_id"] == interaction_id for link in links)

    async def test_hooks_never_raise_on_bad_input(self, db_session: AsyncSession) -> None:
        """Fail-open guarantee: a broken/unknown channel or missing conversation
        link must never propagate — it must not be able to break webchat/voice/
        complaint filing even if something in this new layer misbehaves."""
        result = await conversation_hooks.on_interaction_started(
            db_session, None, "not_a_real_channel", uuid.uuid4()
        )
        assert result is None

        # No channel link exists for this random interaction id — must no-op, not raise.
        await conversation_hooks.on_message(
            db_session, uuid.uuid4(), "user", "web_form", "orphan message"
        )

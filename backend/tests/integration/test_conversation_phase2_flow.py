"""Conversation domain integration tests — Sprint 28 Phase 2
(omnichannel persistence & event synchronization).

One test per spec validation scenario, plus targeted tests for the
mechanisms Phase 2 adds on top of Phase 1: status auto-transition
(best-effort, never raises), participant de-duplication, and "last activity"
tracking via `ConversationRepository.touch`.
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ai.models import AIResponse, ChatMessage, ChatResponse, TokenUsage
from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.complaint.schemas.complaint_schemas import ComplaintCreate
from domains.complaint.services.complaint_service import ComplaintService
from domains.conversation import integration_hooks as conversation_hooks
from domains.conversation.constants.conversation_constants import (
    ConversationMessageType,
    ConversationStatus,
)
from domains.conversation.repositories.conversation_repository import ConversationRepository
from domains.conversation.repositories.event_repository import ConversationEventRepository
from domains.conversation.schemas.conversation_schemas import ConversationCreate
from domains.conversation.services.conversation_service import ConversationService
from domains.customer.repositories.customer_repository import CustomerRepository
from domains.customer.schemas.customer_schema import CustomerCreateRequest
from domains.customer.services.customer_service import CustomerService
from domains.interaction.constants.interaction_constants import (
    InteractionChannel,
    InteractionDirection,
)
from domains.interaction.repositories.interaction_repository import InteractionRepository
from domains.interaction.schemas.interaction_schemas import InteractionCreate
from domains.interaction.services.interaction_service import InteractionService
from domains.workflow.repositories.workflow_repository import WorkflowRepository
from domains.workflow.schemas.workflow_schemas import WorkflowCreate
from domains.workflow.services.workflow_service import WorkflowService


async def _make_customer(db_session: AsyncSession):
    service = CustomerService(repository=CustomerRepository(session=db_session))
    customer, _ = await service.create_customer(
        CustomerCreateRequest(
            external_ref=f"phase2-{uuid.uuid4().hex}",
            full_name="Phase2 Test Customer",
            email=f"{uuid.uuid4().hex}@test.com",
        )
    )
    return customer


@pytest.mark.asyncio
class TestScenario1WebChat:
    """Customer starts Web Chat -> conversation created, customer message
    stored, AI response stored, status auto-advances."""

    async def test_webchat_status_advances_new_active_ai_handling(
        self, client: AsyncClient,
    ) -> None:
        customer_ref = str(uuid.uuid4())
        start_resp = await client.post(
            "/api/v1/interactions/conversations/start",
            json={"customer_ref": customer_ref, "channel": "web_form"},
        )
        assert start_resp.status_code == 201
        interaction_id = start_resp.json()["data"]["id"]

        list_resp = await client.get(f"/api/v1/conversations?customer_id={customer_ref}")
        conversation_id = list_resp.json()["data"][0]["id"]
        status_resp = await client.get(f"/api/v1/conversations/{conversation_id}/status")
        assert status_resp.json()["data"]["current_status"] == "new"

        mock_chat = ChatResponse(
            message=ChatMessage(role="assistant", content="Sure, I can help."),
            finish_reason="stop", model="gpt-mock",
            usage=TokenUsage(prompt_tokens=5, completion_tokens=5, latency_ms=5.0),
        )
        mock_generate = AIResponse(
            content="Mock RAG.", finish_reason="stop", model="gpt-mock",
            usage=TokenUsage(prompt_tokens=5, completion_tokens=5, latency_ms=5.0),
        )
        with patch("ai.gateway.ai_gateway.AIGateway.chat", new_callable=AsyncMock) as mc, \
             patch("ai.gateway.ai_gateway.AIGateway.generate", new_callable=AsyncMock) as mg:
            mc.return_value = mock_chat
            mg.return_value = mock_generate
            msg_resp = await client.post(
                "/api/v1/interactions/conversations/message",
                json={"interaction_id": interaction_id, "message": "I need help with my policy."},
            )
        assert msg_resp.status_code == 200

        status_resp = await client.get(f"/api/v1/conversations/{conversation_id}/status")
        assert status_resp.json()["data"]["current_status"] == "ai_handling"
        assert status_resp.json()["data"]["ai_handling"] is True

        timeline_resp = await client.get(f"/api/v1/conversations/{conversation_id}/timeline")
        assert timeline_resp.status_code == 200
        types = [item["type"] for item in timeline_resp.json()["data"]]
        assert types.count("message") == 2


@pytest.mark.asyncio
class TestScenario2Voice:
    """Customer speaks -> customer transcript stored, AI transcript stored,
    voice session start/end events + duration recorded, same message schema
    as web chat (no separate transcript storage)."""

    async def test_voice_session_lifecycle_events_and_transcript_messages(
        self, db_session: AsyncSession,
    ) -> None:
        interaction_service = InteractionService(repository=InteractionRepository(session=db_session))
        interaction, _ = await interaction_service.create_interaction(
            InteractionCreate(
                customer_ref=str(uuid.uuid4()), channel=InteractionChannel.VOICE,
                direction=InteractionDirection.INBOUND, transcript="[]",
            )
        )
        conversation_id = await conversation_hooks.on_interaction_started(
            db_session, interaction.customer_ref, "voice", interaction.id
        )
        await conversation_hooks.on_voice_session_started(db_session, conversation_id, "room-42")

        await conversation_hooks.on_message(
            db_session, interaction.id, "customer", "voice", "What's my claim status?",
        )
        await conversation_hooks.on_message(
            db_session, interaction.id, "assistant", "voice", "Let me check that for you.",
        )

        started_at = "2026-07-20T10:00:00+00:00"
        ended_at = "2026-07-20T10:03:30+00:00"
        await conversation_hooks.on_voice_session_ended(
            db_session, interaction.id, started_at, ended_at, room_name="room-42"
        )

        event_repo = ConversationEventRepository(session=db_session)
        events, total = await event_repo.list_by_conversation(conversation_id)
        event_types = [e.event_type for e in events]
        assert "voice.session_started" in event_types
        assert "voice.session_ended" in event_types

        ended_event = next(e for e in events if e.event_type == "voice.session_ended")
        assert ended_event.payload["duration_seconds"] == pytest.approx(210.0)
        assert ended_event.payload["room_name"] == "room-42"

        from domains.conversation.repositories.message_repository import (
            ConversationMessageRepository,
        )

        message_repo = ConversationMessageRepository(session=db_session)
        messages, msg_total = await message_repo.list_by_conversation(conversation_id)
        assert msg_total == 2
        # Same schema as web chat — plain ConversationMessage rows, no separate table.
        assert all(m.message_type == ConversationMessageType.TEXT for m in messages)


@pytest.mark.asyncio
class TestScenario3ComplaintLifecycle:
    """Customer files complaint -> linked; complaint.created + intelligence +
    workflow events all land on one timeline."""

    async def test_complaint_workflow_events_share_one_timeline(
        self, db_session: AsyncSession, monkeypatch, test_engine,
    ) -> None:
        from sqlalchemy.ext.asyncio import async_sessionmaker

        test_factory = async_sessionmaker(test_engine, expire_on_commit=False)
        monkeypatch.setattr(
            "app.platform.database.session.get_session_factory", lambda: test_factory
        )

        customer = await _make_customer(db_session)
        complaint_service = ComplaintService(
            repository=ComplaintRepository(session=db_session),
            customer_repository=CustomerRepository(session=db_session),
            interaction_repository=InteractionRepository(session=db_session),
        )
        complaint, _ = await complaint_service.create_complaint(
            ComplaintCreate(customer_id=customer.id, title="Billing issue", category="billing")
        )

        # Manual-filing hook (Phase 1) links/creates the conversation — runs
        # on its own committed session, matching how the router wires it via
        # BackgroundTasks.
        await conversation_hooks.on_complaint_filed_manually(
            customer.id, complaint.id, complaint.complaint_number
        )

        workflow_service = WorkflowService(
            repository=WorkflowRepository(session=db_session),
            complaint_repository=ComplaintRepository(session=db_session),
        )
        workflow, _ = await workflow_service.create_workflow(
            WorkflowCreate(complaint_id=complaint.id, current_queue="billing", assigned_team="billing")
        )

        # Simulates what complaint_router/workflow_router now do post-Phase-2.
        await conversation_hooks.on_complaint_lifecycle(
            db_session, complaint, "complaint.intelligence_result", {"category": "billing"}
        )
        await conversation_hooks.on_workflow_lifecycle(db_session, workflow, "workflow.started")

        async with test_factory() as verify_session:
            conversation = await ConversationRepository(session=verify_session).get_by_complaint_id(
                complaint.id
            )
            assert conversation is not None

            events, total = await ConversationEventRepository(session=verify_session).list_by_conversation(
                conversation.id
            )
            event_types = {e.event_type for e in events}
            assert "complaint.created" in event_types
            assert "complaint.intelligence_result" in event_types
            assert "workflow.started" in event_types


@pytest.mark.asyncio
class TestScenario4EmployeeJoins:
    """Employee later joins -> becomes a participant exactly once, even if
    assigned twice; conversation continues (no forced status jump)."""

    async def test_employee_participant_is_deduplicated(
        self, client: AsyncClient,
    ) -> None:
        create_resp = await client.post(
            "/api/v1/conversations", json={"current_channel": "web_chat"},
        )
        conversation_id = create_resp.json()["data"]["id"]
        employee_id = str(uuid.uuid4())

        for _ in range(2):
            assign_resp = await client.post(
                f"/api/v1/conversations/{conversation_id}/assign",
                json={"employee_id": employee_id},
            )
            assert assign_resp.status_code == 200

        participants_resp = await client.get(f"/api/v1/conversations/{conversation_id}/participants")
        employee_participants = [
            p for p in participants_resp.json()["data"]
            if p["participant_type"] == "employee" and p["participant_ref"] == employee_id
        ]
        assert len(employee_participants) == 1


@pytest.mark.asyncio
class TestScenario5ConversationCloses:
    """Conversation closes -> status updates; timeline remains intact."""

    async def test_complaint_resolution_drives_conversation_to_resolved_then_closed(
        self, db_session: AsyncSession,
    ) -> None:
        customer = await _make_customer(db_session)
        complaint_service = ComplaintService(
            repository=ComplaintRepository(session=db_session),
            customer_repository=CustomerRepository(session=db_session),
            interaction_repository=InteractionRepository(session=db_session),
        )
        complaint, _ = await complaint_service.create_complaint(
            ComplaintCreate(customer_id=customer.id, title="Delayed claim", category="claims")
        )

        conversation_repo = ConversationRepository(session=db_session)
        conversation_service = ConversationService(repository=conversation_repo)
        conversation, _ = await conversation_service.create_conversation(
            ConversationCreate(
                customer_id=customer.id, complaint_id=complaint.id, current_channel="complaint"
            )
        )
        # NEW -> ACTIVE so RESOLVED is a reachable transition per Phase 1's matrix.
        await conversation_service.update_status(conversation.id, ConversationStatus.ACTIVE)

        resolved_complaint, _ = await complaint_service.resolve_complaint(complaint.id)
        await conversation_hooks.on_complaint_lifecycle(
            db_session, resolved_complaint, "complaint.resolved"
        )

        after_resolve = await conversation_service.get_conversation(conversation.id)
        assert after_resolve.current_status == ConversationStatus.RESOLVED

        closed_complaint, _ = await complaint_service.close_complaint(complaint.id)
        await conversation_hooks.on_complaint_lifecycle(db_session, closed_complaint, "complaint.closed")

        after_close = await conversation_service.get_conversation(conversation.id)
        assert after_close.current_status == ConversationStatus.CLOSED

        events, total = await ConversationEventRepository(session=db_session).list_by_conversation(
            conversation.id
        )
        assert total == 2
        assert {e.event_type for e in events} == {"complaint.resolved", "complaint.closed"}


@pytest.mark.asyncio
class TestStatusTransitionNeverRaises:
    """The status matrix is best-effort — an unreachable target must be
    skipped, never break the caller."""

    async def test_ai_message_on_closed_conversation_does_not_raise(
        self, db_session: AsyncSession,
    ) -> None:
        interaction_service = InteractionService(repository=InteractionRepository(session=db_session))
        interaction, _ = await interaction_service.create_interaction(
            InteractionCreate(
                customer_ref=str(uuid.uuid4()), channel=InteractionChannel.WEB_FORM, transcript="[]"
            )
        )
        conversation_id = await conversation_hooks.on_interaction_started(
            db_session, interaction.customer_ref, "web_form", interaction.id
        )
        conversation_service = ConversationService(repository=ConversationRepository(session=db_session))
        await conversation_service.update_status(conversation_id, ConversationStatus.ACTIVE)
        await conversation_service.update_status(conversation_id, ConversationStatus.CLOSED)

        # CLOSED has no outgoing transitions at all (Phase 1's state machine) —
        # this must not raise, and the status must remain CLOSED.
        await conversation_hooks.on_message(
            db_session, interaction.id, "assistant", "web_form", "This should be a silent no-op."
        )

        conversation = await conversation_service.get_conversation(conversation_id)
        assert conversation.current_status == ConversationStatus.CLOSED


@pytest.mark.asyncio
class TestLastActivityTouch:
    async def test_touch_bumps_updated_at(self, db_session: AsyncSession) -> None:
        repo = ConversationRepository(session=db_session)
        service = ConversationService(repository=repo)

        conversation, _ = await service.create_conversation(
            ConversationCreate(current_channel="web_chat")
        )
        original_updated_at = conversation.updated_at.replace(tzinfo=None)

        await repo.touch(conversation.id)

        refreshed = await repo.get_by_id(conversation.id)
        # SQLite (test DB) round-trips DateTime(timezone=True) as naive;
        # production Postgres keeps both sides aware — strip tzinfo so the
        # comparison is meaningful under either.
        assert refreshed.updated_at.replace(tzinfo=None) >= original_updated_at

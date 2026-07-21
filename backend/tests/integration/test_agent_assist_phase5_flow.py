"""Agent Assist domain integration tests — Sprint 28 Phase 5
(live AI conversation intelligence: summary, intent, sentiment, next-best-action,
knowledge assist, suggested replies, insights, alerts)."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from domains.agent_assist.services.agent_assist_service import regenerate_agent_assist_insight
from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.complaint.schemas.complaint_schemas import ComplaintCreate
from domains.complaint.services.complaint_service import ComplaintService
from domains.conversation import integration_hooks as conversation_hooks
from domains.conversation.repositories.conversation_repository import ConversationRepository
from domains.customer.repositories.customer_repository import CustomerRepository
from domains.customer.schemas.customer_schema import CustomerCreateRequest
from domains.customer.services.customer_service import CustomerService
from domains.interaction.repositories.interaction_repository import InteractionRepository


@pytest.fixture(autouse=True, scope="module")
def _register_ai_prompts():
    # The test AsyncClient/ASGITransport harness never runs FastAPI's
    # startup lifespan, so app.startup.bootstrap._init_prompts() (which
    # registers complaint/* and agent_assist/* prompts) never fires —
    # register them directly, same as production startup does.
    from ai.agent_assist.prompts import register_agent_assist_prompts
    from ai.intelligence.prompts import register_complaint_prompts

    register_complaint_prompts()
    register_agent_assist_prompts()


async def _create_conversation(client: AsyncClient, channel: str = "web_chat") -> str:
    resp = await client.post("/api/v1/conversations", json={"current_channel": channel})
    return resp.json()["data"]["id"]


async def _add_customer_message(client: AsyncClient, conversation_id: str, content: str) -> None:
    await client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"sender_type": "customer", "channel": "web_chat", "content": content},
    )


async def _make_customer(db_session: AsyncSession, full_name: str):
    service = CustomerService(repository=CustomerRepository(session=db_session))
    customer, _ = await service.create_customer(
        CustomerCreateRequest(
            external_ref=f"p5-{uuid.uuid4().hex}", full_name=full_name,
            email=f"{uuid.uuid4().hex}@test.com",
        )
    )
    return customer


@pytest.mark.asyncio
class TestEmptyStateAndBasicEndpoints:
    async def test_get_before_generation_returns_empty_state(self, client: AsyncClient) -> None:
        conversation_id = await _create_conversation(client)
        resp = await client.get(f"/api/v1/conversations/{conversation_id}/agent-assist")
        assert resp.status_code == 200
        assert resp.json()["data"]["generated"] is False

    async def test_get_for_missing_conversation_404s(self, client: AsyncClient) -> None:
        resp = await client.get(f"/api/v1/conversations/{uuid.uuid4()}/agent-assist")
        assert resp.status_code == 404

    async def test_regenerate_with_no_messages_returns_empty_state(self, client: AsyncClient) -> None:
        conversation_id = await _create_conversation(client)
        resp = await client.post(f"/api/v1/conversations/{conversation_id}/agent-assist/regenerate")
        assert resp.status_code == 200
        assert resp.json()["data"]["generated"] is False

    async def test_regenerate_creates_insight_visible_via_get(self, client: AsyncClient) -> None:
        conversation_id = await _create_conversation(client)
        await _add_customer_message(client, conversation_id, "Hello, I have a question.")

        regen_resp = await client.post(f"/api/v1/conversations/{conversation_id}/agent-assist/regenerate")
        assert regen_resp.status_code == 200
        assert regen_resp.json()["data"]["id"] is not None

        get_resp = await client.get(f"/api/v1/conversations/{conversation_id}/agent-assist")
        data = get_resp.json()["data"]
        assert data.get("id") is not None
        assert data["message_count_at_generation"] == 1

    async def test_history_endpoint_returns_chronological_entries(self, client: AsyncClient) -> None:
        conversation_id = await _create_conversation(client)
        await _add_customer_message(client, conversation_id, "First message.")
        await client.post(f"/api/v1/conversations/{conversation_id}/agent-assist/regenerate")
        await _add_customer_message(client, conversation_id, "Second message, still here.")
        await client.post(f"/api/v1/conversations/{conversation_id}/agent-assist/regenerate")

        resp = await client.get(f"/api/v1/conversations/{conversation_id}/agent-assist/history")
        assert resp.status_code == 200
        history = resp.json()["data"]
        assert len(history) == 2
        # Oldest first.
        assert history[0]["created_at"] <= history[1]["created_at"]


@pytest.mark.asyncio
class TestThrottle:
    async def test_regenerate_without_force_is_throttled_immediately_after(
        self, db_session: AsyncSession, client: AsyncClient,
    ) -> None:
        conversation_id = await _create_conversation(client)
        await _add_customer_message(client, conversation_id, "Hello there.")

        first = await regenerate_agent_assist_insight(db_session, uuid.UUID(conversation_id), force=False)
        assert first is not None

        # No new messages, no time elapsed — should be throttled.
        second = await regenerate_agent_assist_insight(db_session, uuid.UUID(conversation_id), force=False)
        assert second is None

    async def test_force_bypasses_throttle(self, db_session: AsyncSession, client: AsyncClient) -> None:
        conversation_id = await _create_conversation(client)
        await _add_customer_message(client, conversation_id, "Hello there.")

        first = await regenerate_agent_assist_insight(db_session, uuid.UUID(conversation_id), force=False)
        second = await regenerate_agent_assist_insight(db_session, uuid.UUID(conversation_id), force=True)
        assert first is not None
        assert second is not None
        assert second.id != first.id


@pytest.mark.asyncio
class TestScenario1ProductInquiry:
    async def test_detects_product_inquiry_intent_and_suggests_vehicle_clarification(
        self, client: AsyncClient,
    ) -> None:
        conversation_id = await _create_conversation(client)
        await _add_customer_message(
            client, conversation_id,
            "Hi, I'm interested in motorcycle insurance. What plans do you offer and roughly how "
            "much would it cost?",
        )

        resp = await client.post(f"/api/v1/conversations/{conversation_id}/agent-assist/regenerate")
        data = resp.json()["data"]

        # Live LLM call — the exact taxonomy label can reasonably land on
        # either close category, so accept both rather than over-fitting to
        # one literal string.
        assert data["intent"] in ("Product Inquiry", "New Policy Purchase")
        assert data["intent_confidence"] > 0
        actions = [a["action"] for a in data["next_best_actions"]]
        assert "Offer Quote" in actions
        assert len(data["suggested_replies"]) > 0

    async def test_knowledge_articles_populated_for_a_matching_query(self, client: AsyncClient) -> None:
        conversation_id = await _create_conversation(client)
        # Short, deliberately matches the real "Auto Shield" product description
        # ("Complete auto insurance with...") in backend/data/products.json —
        # KnowledgeRepository does whole-string substring matching, so the
        # query must literally be contained in the target field.
        await _add_customer_message(client, conversation_id, "auto insurance")

        resp = await client.post(f"/api/v1/conversations/{conversation_id}/agent-assist/regenerate")
        articles = resp.json()["data"]["knowledge_articles"]
        assert len(articles) > 0
        assert any(a["source"] == "product" for a in articles)


@pytest.mark.asyncio
class TestScenario2EscalatingSentiment:
    async def test_escalation_alert_appears_and_history_shows_declining_trend(
        self, client: AsyncClient,
    ) -> None:
        conversation_id = await _create_conversation(client)
        await _add_customer_message(client, conversation_id, "Hi, quick question about my policy.")
        first = await client.post(f"/api/v1/conversations/{conversation_id}/agent-assist/regenerate")
        assert first.json()["data"]["sentiment"] == "neutral"

        # Explicit escalation triggers per the real complaint/escalation
        # rubric (regulatory threat, supervisor request, repeat complaints,
        # media threat) — reliably scores >=70 from the live model, unlike
        # plain frustration alone.
        await _add_customer_message(
            client, conversation_id,
            "I have complained about this THREE times before and nobody helps. If this is not "
            "fixed today I will file a complaint with the CMA regulator and post about this on "
            "social media. I want to speak to a supervisor immediately.",
        )
        second = await client.post(f"/api/v1/conversations/{conversation_id}/agent-assist/regenerate")
        data = second.json()["data"]

        assert data["sentiment"] == "escalated"
        alert_types = [a["type"] for a in data["alerts"]]
        assert "escalation_recommended" in alert_types
        assert "frustration_increasing" in alert_types

        history_resp = await client.get(f"/api/v1/conversations/{conversation_id}/agent-assist/history")
        history = history_resp.json()["data"]
        assert history[0]["sentiment"] == "neutral"
        assert history[-1]["sentiment"] == "escalated"


@pytest.mark.asyncio
class TestScenario3ContinuesAfterTakeover:
    async def test_regeneration_still_fires_after_employee_takeover(self, client: AsyncClient) -> None:
        conversation_id = await _create_conversation(client)
        employee_id = str(uuid.uuid4())
        await _add_customer_message(client, conversation_id, "I need help with my policy.")

        take_over = await client.post(
            f"/api/v1/conversations/{conversation_id}/take-over", json={"employee_id": employee_id}
        )
        assert take_over.json()["data"]["human_handling"] is True

        await _add_customer_message(client, conversation_id, "Thanks, still waiting on an update though.")
        resp = await client.post(f"/api/v1/conversations/{conversation_id}/agent-assist/regenerate")
        data = resp.json()["data"]
        assert data.get("id") is not None
        assert data["message_count_at_generation"] >= 2


@pytest.mark.asyncio
class TestScenario4ComplaintContext:
    async def test_complaint_severity_populates_on_regeneration(
        self, db_session: AsyncSession, client: AsyncClient, monkeypatch, test_engine,
    ) -> None:
        from sqlalchemy.ext.asyncio import async_sessionmaker

        test_factory = async_sessionmaker(test_engine, expire_on_commit=False)
        monkeypatch.setattr(
            "app.platform.database.session.get_session_factory", lambda: test_factory
        )

        customer = await _make_customer(db_session, "Agent Assist Complaint Customer")
        complaint_service = ComplaintService(
            repository=ComplaintRepository(session=db_session),
            customer_repository=CustomerRepository(session=db_session),
            interaction_repository=InteractionRepository(session=db_session),
        )
        complaint, _ = await complaint_service.create_complaint(
            ComplaintCreate(
                customer_id=customer.id, title="Repeated billing error",
                category="billing", priority="high",
            )
        )
        await db_session.flush()
        await conversation_hooks.on_complaint_filed_manually(
            customer.id, complaint.id, complaint.complaint_number
        )

        async with test_factory() as verify_session:
            conversation_repo = ConversationRepository(session=verify_session)
            conversation = await conversation_repo.get_by_complaint_id(complaint.id)
            assert conversation is not None

            await _add_customer_message(client, str(conversation.id), "Any update on my complaint?")
            insight = await regenerate_agent_assist_insight(verify_session, conversation.id, force=True)

            assert insight is not None
            assert insight.complaint_severity_at_generation == str(complaint.severity)


@pytest.mark.asyncio
class TestOnMessageHookWiring:
    async def test_on_message_triggers_regeneration_via_background_hook(
        self, db_session: AsyncSession, monkeypatch, test_engine,
    ) -> None:
        from sqlalchemy.ext.asyncio import async_sessionmaker

        from domains.interaction.constants.interaction_constants import InteractionChannel
        from domains.interaction.repositories.interaction_repository import InteractionRepository
        from domains.interaction.schemas.interaction_schemas import InteractionCreate
        from domains.interaction.services.interaction_service import InteractionService
        from domains.agent_assist.repositories.agent_assist_repository import AgentAssistRepository

        test_factory = async_sessionmaker(test_engine, expire_on_commit=False)
        monkeypatch.setattr(
            "app.platform.database.session.get_session_factory", lambda: test_factory
        )

        interaction_service = InteractionService(repository=InteractionRepository(session=db_session))
        interaction, _ = await interaction_service.create_interaction(
            InteractionCreate(
                customer_ref=str(uuid.uuid4()), channel=InteractionChannel.WEB_FORM, transcript="[]"
            )
        )
        conversation_id = await conversation_hooks.on_interaction_started(
            db_session, interaction.customer_ref, "web_form", interaction.id
        )
        # on_message fires the regeneration via asyncio.create_task
        # (fire-and-forget, its own session) — poll rather than assert
        # immediately, since it races the test coroutine.
        await conversation_hooks.on_message(
            db_session, interaction.id, "user", "web_form", "Hello, I need assistance."
        )

        import asyncio

        # Real LLM calls (4 concurrent complaint-intel analyses + 1 new
        # Agent Assist prompt + knowledge search) commonly take ~10s total —
        # give the background task real room rather than a tight timeout.
        latest = None
        for _ in range(60):
            await asyncio.sleep(0.5)
            async with test_factory() as verify_session:
                latest = await AgentAssistRepository(session=verify_session).get_latest(conversation_id)
            if latest is not None:
                break
        assert latest is not None

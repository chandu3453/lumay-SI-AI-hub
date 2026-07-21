"""Conversation domain integration tests — Sprint 28 Phase 3
(employee interaction center backend additions: priority, filters/search, SSE)."""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.complaint.schemas.complaint_schemas import ComplaintCreate
from domains.complaint.services.complaint_service import ComplaintService
from domains.conversation import integration_hooks as conversation_hooks
from domains.conversation.constants.conversation_constants import ConversationPriority
from domains.conversation.repositories.conversation_repository import ConversationRepository
from domains.conversation.schemas.conversation_schemas import ConversationCreate
from domains.conversation.services.conversation_service import ConversationService
from domains.customer.repositories.customer_repository import CustomerRepository
from domains.customer.schemas.customer_schema import CustomerCreateRequest
from domains.customer.services.customer_service import CustomerService
from domains.interaction.constants.interaction_constants import InteractionChannel
from domains.interaction.repositories.interaction_repository import InteractionRepository
from domains.interaction.schemas.interaction_schemas import InteractionCreate
from domains.interaction.services.interaction_service import InteractionService


async def _make_customer(db_session: AsyncSession, full_name: str):
    service = CustomerService(repository=CustomerRepository(session=db_session))
    customer, _ = await service.create_customer(
        CustomerCreateRequest(
            external_ref=f"p3-{uuid.uuid4().hex}", full_name=full_name,
            email=f"{uuid.uuid4().hex}@test.com",
        )
    )
    return customer


@pytest.mark.asyncio
class TestPrioritySync:
    async def test_set_priority_endpoint(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/conversations", json={"current_channel": "web_chat"})
        conversation_id = create_resp.json()["data"]["id"]
        assert create_resp.json()["data"]["priority"] == "medium"

        resp = await client.patch(
            f"/api/v1/conversations/{conversation_id}/priority", json={"priority": "critical"}
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["priority"] == "critical"

        list_resp = await client.get("/api/v1/conversations?priority=critical")
        ids = [c["id"] for c in list_resp.json()["data"]]
        assert conversation_id in ids

        # Priority changes must persist to the event log (not just SSE), same
        # persist-then-broadcast contract as close_conversation — otherwise a
        # reconnect or the activity timeline would never see it happened.
        events_resp = await client.get(f"/api/v1/conversations/{conversation_id}/events")
        assert events_resp.status_code == 200
        event_types = [e["event_type"] for e in events_resp.json()["data"]]
        assert "priority_changed" in event_types

    async def test_complaint_priority_propagates_to_conversation(
        self, db_session: AsyncSession, monkeypatch, test_engine,
    ) -> None:
        from sqlalchemy.ext.asyncio import async_sessionmaker

        test_factory = async_sessionmaker(test_engine, expire_on_commit=False)
        monkeypatch.setattr(
            "app.platform.database.session.get_session_factory", lambda: test_factory
        )

        customer = await _make_customer(db_session, "Priority Sync Customer")
        complaint_service = ComplaintService(
            repository=ComplaintRepository(session=db_session),
            customer_repository=CustomerRepository(session=db_session),
            interaction_repository=InteractionRepository(session=db_session),
        )
        complaint, _ = await complaint_service.create_complaint(
            ComplaintCreate(
                customer_id=customer.id, title="Urgent billing issue",
                category="billing", priority="critical",
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

            await conversation_hooks.on_complaint_lifecycle(
                verify_session, complaint, "complaint.assigned", {"queue": "billing"}
            )
            await verify_session.commit()

            refreshed = await conversation_repo.get_by_id(conversation.id)
            assert refreshed.priority == ConversationPriority.CRITICAL


@pytest.mark.asyncio
class TestFiltersAndSearch:
    async def test_filter_by_assigned_employee_and_priority(
        self, client: AsyncClient,
    ) -> None:
        create_resp = await client.post("/api/v1/conversations", json={"current_channel": "voice"})
        conversation_id = create_resp.json()["data"]["id"]
        employee_id = str(uuid.uuid4())
        await client.post(f"/api/v1/conversations/{conversation_id}/assign", json={"employee_id": employee_id})
        await client.patch(f"/api/v1/conversations/{conversation_id}/priority", json={"priority": "high"})

        resp = await client.get(
            f"/api/v1/conversations?assigned_employee_id={employee_id}&priority=high"
        )
        ids = [c["id"] for c in resp.json()["data"]]
        assert conversation_id in ids

        resp_other = await client.get(f"/api/v1/conversations?assigned_employee_id={uuid.uuid4()}")
        assert conversation_id not in [c["id"] for c in resp_other.json()["data"]]

    async def test_search_by_customer_name(self, db_session: AsyncSession) -> None:
        customer = await _make_customer(db_session, "Zzyzx Searchable Customer")
        conversation_service = ConversationService(repository=ConversationRepository(session=db_session))
        conversation, _ = await conversation_service.create_conversation(
            ConversationCreate(customer_id=customer.id, current_channel="web_chat")
        )

        repo = ConversationRepository(session=db_session)
        results, total = await repo.list(search="Zzyzx Searchable")
        assert total == 1
        assert results[0].id == conversation.id

    async def test_search_by_conversation_id(self, db_session: AsyncSession) -> None:
        conversation_service = ConversationService(repository=ConversationRepository(session=db_session))
        conversation, _ = await conversation_service.create_conversation(
            ConversationCreate(current_channel="email")
        )
        repo = ConversationRepository(session=db_session)
        results, total = await repo.list(search=str(conversation.id)[:8])
        assert total >= 1
        assert any(r.id == conversation.id for r in results)

    async def test_search_by_message_text(self, db_session: AsyncSession) -> None:
        interaction_service = InteractionService(repository=InteractionRepository(session=db_session))
        interaction, _ = await interaction_service.create_interaction(
            InteractionCreate(
                customer_ref=str(uuid.uuid4()), channel=InteractionChannel.WEB_FORM, transcript="[]"
            )
        )
        conversation_id = await conversation_hooks.on_interaction_started(
            db_session, interaction.customer_ref, "web_form", interaction.id
        )
        await conversation_hooks.on_message(
            db_session, interaction.id, "user", "web_form", "I need a refund for my unique-marker-xyz claim"
        )

        repo = ConversationRepository(session=db_session)
        results, total = await repo.list(search="unique-marker-xyz")
        assert total == 1
        assert results[0].id == conversation_id


@pytest.mark.asyncio
class TestReopenAndSSE:
    async def test_reopen_closed_conversation_via_status_endpoint(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/conversations", json={"current_channel": "web_chat"})
        conversation_id = create_resp.json()["data"]["id"]
        await client.patch(f"/api/v1/conversations/{conversation_id}/status", json={"status": "active"})
        close_resp = await client.post(f"/api/v1/conversations/{conversation_id}/close")
        assert close_resp.json()["data"]["current_status"] == "closed"

        reopen_resp = await client.patch(
            f"/api/v1/conversations/{conversation_id}/status", json={"status": "active"}
        )
        assert reopen_resp.status_code == 200
        assert reopen_resp.json()["data"]["current_status"] == "active"

    async def test_conversation_stream_history_endpoint(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/conversations", json={"current_channel": "web_chat"})
        conversation_id = create_resp.json()["data"]["id"]
        resp = await client.get(f"/api/v1/conversations/{conversation_id}/stream/history")
        assert resp.status_code == 200
        assert isinstance(resp.json()["data"], list)

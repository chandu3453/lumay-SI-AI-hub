"""Reporting domain integration tests — Sprint 29
(Customer 360 + Enterprise Analytics: read-only aggregation over real data,
no synthetic store involved anywhere in this file)."""

import csv
import io
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from domains.agent_assist.repositories.agent_assist_repository import AgentAssistRepository
from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.complaint.schemas.complaint_schemas import ComplaintCreate
from domains.complaint.services.complaint_service import ComplaintService
from domains.customer.repositories.customer_repository import CustomerRepository
from domains.customer.schemas.customer_schema import CustomerCreateRequest
from domains.customer.services.customer_service import CustomerService
from domains.identity.models.user import User
from domains.identity.repositories.user_repository import UserRepository
from domains.interaction.repositories.interaction_repository import InteractionRepository


async def _make_customer(db_session: AsyncSession, full_name: str):
    service = CustomerService(repository=CustomerRepository(session=db_session))
    customer, _ = await service.create_customer(
        CustomerCreateRequest(
            external_ref=f"r29-{uuid.uuid4().hex}", full_name=full_name,
            email=f"{uuid.uuid4().hex}@test.com",
        )
    )
    return customer


async def _create_conversation(
    client: AsyncClient, *, channel: str = "web_chat", customer_id: str | None = None
) -> str:
    body = {"current_channel": channel}
    if customer_id:
        body["customer_id"] = customer_id
    resp = await client.post("/api/v1/conversations", json=body)
    return resp.json()["data"]["id"]


async def _add_customer_message(client: AsyncClient, conversation_id: str, content: str) -> None:
    await client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"sender_type": "customer", "channel": "web_chat", "content": content},
    )


@pytest.mark.asyncio
class TestCustomer360:
    async def test_empty_state_for_customer_with_no_conversations(
        self, db_session: AsyncSession, client: AsyncClient,
    ) -> None:
        customer = await _make_customer(db_session, "Empty State Customer")
        resp = await client.get(f"/api/v1/customers/{customer.id}/360")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["current_conversation"] is None
        assert data["conversation_statistics"]["total_conversations"] == 0
        assert data["policies"]["available"] is False
        assert data["claims"]["available"] is False

    async def test_missing_customer_404s(self, client: AsyncClient) -> None:
        resp = await client.get(f"/api/v1/customers/{uuid.uuid4()}/360")
        assert resp.status_code == 404

    async def test_reflects_real_conversation_and_complaint(
        self, db_session: AsyncSession, client: AsyncClient,
    ) -> None:
        customer = await _make_customer(db_session, "Populated 360 Customer")
        conversation_id = await _create_conversation(client, customer_id=str(customer.id))
        await _add_customer_message(client, conversation_id, "Hello, testing 360.")

        complaint_service = ComplaintService(
            repository=ComplaintRepository(session=db_session),
            customer_repository=CustomerRepository(session=db_session),
            interaction_repository=InteractionRepository(session=db_session),
        )
        await complaint_service.create_complaint(
            ComplaintCreate(customer_id=customer.id, title="Test complaint", category="billing")
        )
        await db_session.flush()

        resp = await client.get(f"/api/v1/customers/{customer.id}/360")
        data = resp.json()["data"]
        assert data["current_conversation"]["id"] == conversation_id
        assert data["conversation_statistics"]["total_conversations"] == 1
        assert data["overview"]["open_complaints"] == 1
        assert len(data["complaints"]) == 1
        assert len(data["recent_conversations"]) == 1

    async def test_assigned_employee_name_resolves_when_user_exists(
        self, db_session: AsyncSession, client: AsyncClient,
    ) -> None:
        user = await UserRepository(session=db_session).add(
            User(
                email=f"{uuid.uuid4().hex}@lumay-test.com",
                hashed_password="x",
                full_name="Resolved Agent Name",
            )
        )
        customer = await _make_customer(db_session, "Assigned Employee Customer")
        conversation_id = await _create_conversation(client, customer_id=str(customer.id))
        await client.post(
            f"/api/v1/conversations/{conversation_id}/take-over",
            json={"employee_id": str(user.id)},
        )

        resp = await client.get(f"/api/v1/customers/{customer.id}/360")
        data = resp.json()["data"]
        assert data["assigned_employee"]["id"] == str(user.id)
        assert data["assigned_employee"]["full_name"] == "Resolved Agent Name"


@pytest.mark.asyncio
class TestCustomerActivityTimeline:
    async def test_merges_messages_and_events_chronologically_across_conversations(
        self, db_session: AsyncSession, client: AsyncClient,
    ) -> None:
        customer = await _make_customer(db_session, "Timeline Customer")
        conv_a = await _create_conversation(client, customer_id=str(customer.id))
        await _add_customer_message(client, conv_a, "First conversation message.")
        await client.post(f"/api/v1/conversations/{conv_a}/close")

        conv_b = await _create_conversation(client, customer_id=str(customer.id))
        await _add_customer_message(client, conv_b, "Second conversation message.")

        resp = await client.get(f"/api/v1/customers/{customer.id}/activity")
        data = resp.json()["data"]
        assert data["total"] >= 3  # 2 messages + at least 1 status_changed event
        timestamps = [item["timestamp"] for item in data["items"]]
        assert timestamps == sorted(timestamps)
        conversation_scoped_content = [
            item["content"] for item in data["items"] if item["type"] == "message"
        ]
        assert "First conversation message." in conversation_scoped_content
        assert "Second conversation message." in conversation_scoped_content

    async def test_missing_customer_404s(self, client: AsyncClient) -> None:
        resp = await client.get(f"/api/v1/customers/{uuid.uuid4()}/activity")
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestConversationAnalyticsSummary:
    async def test_counts_reflect_real_conversations(self, client: AsyncClient) -> None:
        before = (await client.get("/api/v1/reporting/conversations/summary")).json()["data"]

        conv1 = await _create_conversation(client, channel="web_chat")
        conv2 = await _create_conversation(client, channel="voice")
        await client.patch(f"/api/v1/conversations/{conv1}/status", json={"status": "active"})
        await client.post(f"/api/v1/conversations/{conv1}/close")

        after = (await client.get("/api/v1/reporting/conversations/summary")).json()["data"]
        assert after["total_conversations"] == before["total_conversations"] + 2
        assert after["resolved_conversations"] >= before["resolved_conversations"] + 1

    async def test_customer_satisfaction_is_explicit_placeholder(self, client: AsyncClient) -> None:
        data = (await client.get("/api/v1/reporting/conversations/summary")).json()["data"]
        assert data["customer_satisfaction"] is None

    async def test_ai_to_human_handoff_counted(self, client: AsyncClient) -> None:
        before = (await client.get("/api/v1/reporting/conversations/summary")).json()["data"]
        conversation_id = await _create_conversation(client)
        await client.post(
            f"/api/v1/conversations/{conversation_id}/take-over",
            json={"employee_id": str(uuid.uuid4())},
        )
        after = (await client.get("/api/v1/reporting/conversations/summary")).json()["data"]
        assert after["ai_to_human_handoffs"] == before["ai_to_human_handoffs"] + 1
        assert after["human_handled"] >= before["human_handled"] + 1


@pytest.mark.asyncio
class TestDistributions:
    async def test_channel_distribution_reflects_real_channels(self, client: AsyncClient) -> None:
        await _create_conversation(client, channel="voice")
        data = (await client.get("/api/v1/reporting/conversations/distributions")).json()["data"]
        assert data["channel_distribution"].get("voice", 0) >= 1
        assert data["voice_vs_chat"]["voice"] >= 1
        assert data["policy_category_distribution"]["available"] is False

    async def test_sentiment_distribution_reflects_latest_insight_per_conversation(
        self, db_session: AsyncSession, client: AsyncClient,
    ) -> None:
        conversation_id = await _create_conversation(client)
        await AgentAssistRepository(session=db_session).create(
            conversation_id=uuid.UUID(conversation_id),
            message_count_at_generation=1,
            sentiment="escalated",
            intent="Complaint",
        )
        await db_session.flush()

        data = (await client.get("/api/v1/reporting/conversations/distributions")).json()["data"]
        assert data["sentiment_distribution"].get("escalated", 0) >= 1
        assert data["intent_distribution"].get("Complaint", 0) >= 1

    async def test_only_latest_insight_per_conversation_counted(
        self, db_session: AsyncSession, client: AsyncClient,
    ) -> None:
        # Explicit, distinct created_at — SQLite's `now()` default only has
        # second-level resolution, so two rows created back-to-back in a
        # test can otherwise tie and make the "latest" comparison ambiguous.
        from datetime import UTC, datetime, timedelta

        conversation_id = await _create_conversation(client)
        repo = AgentAssistRepository(session=db_session)
        earlier = datetime.now(UTC) - timedelta(minutes=5)
        later = datetime.now(UTC)
        await repo.create(
            conversation_id=uuid.UUID(conversation_id),
            message_count_at_generation=1,
            sentiment="frustrated",
            created_at=earlier,
        )
        await repo.create(
            conversation_id=uuid.UUID(conversation_id),
            message_count_at_generation=2,
            sentiment="positive",
            created_at=later,
        )
        await db_session.flush()

        insights = await repo.latest_per_conversation()
        matching = [i for i in insights if i.conversation_id == uuid.UUID(conversation_id)]
        assert len(matching) == 1
        assert matching[0].sentiment == "positive"


@pytest.mark.asyncio
class TestTrends:
    async def test_returns_at_least_one_period_after_activity(self, client: AsyncClient) -> None:
        await _create_conversation(client)
        resp = await client.get("/api/v1/reporting/conversations/trends?granularity=day")
        data = resp.json()["data"]
        assert data["granularity"] == "day"
        assert len(data["conversation_trend"]) >= 1
        assert sum(p["count"] for p in data["conversation_trend"]) >= 1


@pytest.mark.asyncio
class TestEmployeeAnalytics:
    async def test_reflects_real_assignment_and_transfer(self, client: AsyncClient) -> None:
        employee_a = str(uuid.uuid4())
        employee_b = str(uuid.uuid4())
        conversation_id = await _create_conversation(client)
        await client.post(
            f"/api/v1/conversations/{conversation_id}/take-over",
            json={"employee_id": employee_a},
        )
        await client.post(
            f"/api/v1/conversations/{conversation_id}/transfer",
            json={"employee_id": employee_b},
        )

        data = (await client.get("/api/v1/reporting/employees")).json()["data"]
        employee_b_row = next((e for e in data if e["employee_id"] == employee_b), None)
        assert employee_b_row is not None
        assert employee_b_row["assigned_conversations"] == 1
        assert employee_b_row["transfer_count"] == 1


@pytest.mark.asyncio
class TestSupervisorDashboard:
    async def test_reflects_real_queue_state(self, client: AsyncClient) -> None:
        before = (await client.get("/api/v1/reporting/supervisor/dashboard")).json()["data"]
        await _create_conversation(client)
        after = (await client.get("/api/v1/reporting/supervisor/dashboard")).json()["data"]
        assert sum(after["queue_by_status"].values()) == sum(before["queue_by_status"].values()) + 1
        assert after["ai_active_conversations"] >= before["ai_active_conversations"] + 1


@pytest.mark.asyncio
class TestExport:
    async def test_csv_export_matches_summary(self, client: AsyncClient) -> None:
        summary = (await client.get("/api/v1/reporting/conversations/summary")).json()["data"]
        resp = await client.get("/api/v1/reporting/export/summary?format=csv")
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")
        rows = list(csv.DictReader(io.StringIO(resp.text)))
        assert len(rows) == 1
        assert int(rows[0]["total_conversations"]) == summary["total_conversations"]

    async def test_xlsx_export_returns_valid_workbook(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/reporting/export/employees?format=xlsx")
        assert resp.status_code == 200
        assert "spreadsheetml" in resp.headers["content-type"]

        from openpyxl import load_workbook

        workbook = load_workbook(io.BytesIO(resp.content))
        assert workbook.active.title == "employees"

    async def test_pdf_export_returns_501(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/reporting/export/summary?format=pdf")
        assert resp.status_code == 501

    async def test_unknown_report_returns_400(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/reporting/export/not-a-real-report?format=csv")
        assert resp.status_code == 400


@pytest.mark.asyncio
class TestUserBatchLookup:
    async def test_resolves_known_ids_and_omits_unknown(
        self, db_session: AsyncSession, client: AsyncClient,
    ) -> None:
        user = await UserRepository(session=db_session).add(
            User(
                email=f"{uuid.uuid4().hex}@lumay-test.com",
                hashed_password="x",
                full_name="Batch Lookup User",
            )
        )
        unknown_id = uuid.uuid4()

        resp = await client.get(f"/api/v1/users?ids={user.id},{unknown_id}")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) == 1
        assert data[0]["id"] == str(user.id)
        assert data[0]["full_name"] == "Batch Lookup User"

    async def test_empty_ids_returns_empty_list(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/users?ids=")
        assert resp.status_code == 200
        assert resp.json()["data"] == []

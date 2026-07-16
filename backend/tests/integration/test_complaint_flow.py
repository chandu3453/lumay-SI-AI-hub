"""Complaint domain integration flow tests."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from domains.complaint.constants.complaint_constants import (
    ComplaintCategory,
    ComplaintStatus,
)
from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.complaint.schemas.complaint_schemas import ComplaintCreate
from domains.complaint.services.complaint_service import ComplaintService
from domains.customer.repositories.customer_repository import CustomerRepository
from domains.interaction.constants.interaction_constants import InteractionChannel
from domains.interaction.repositories.interaction_repository import InteractionRepository


@pytest.mark.asyncio
class TestComplaintFlow:
    """End-to-end flow through the complaint layer."""

    async def test_create_and_retrieve_flow(self, db_session: AsyncSession) -> None:
        complaint_repo = ComplaintRepository(session=db_session)
        customer_repo = CustomerRepository(session=db_session)
        interaction_repo = InteractionRepository(session=db_session)
        service = ComplaintService(
            repository=complaint_repo,
            customer_repository=customer_repo,
            interaction_repository=interaction_repo,
        )

        customer = await customer_repo.create(
            external_ref="FLOW-CUST-001",
            full_name="Complaint Flow Customer",
        )
        interaction = await interaction_repo.create(channel=InteractionChannel.EMAIL)

        complaint, events = await service.create_complaint(
            ComplaintCreate(
                customer_id=customer.id,
                interaction_id=interaction.id,
                title="Flow complaint",
                description="Created through service flow",
                category=ComplaintCategory.SERVICE,
            )
        )
        assert complaint.id is not None
        assert complaint.customer_id == customer.id
        assert complaint.interaction_id == interaction.id
        assert complaint.status == ComplaintStatus.SUBMITTED
        assert len(events) == 1

        fetched = await service.get_complaint(complaint.id)
        assert fetched.id == complaint.id
        assert fetched.title == "Flow complaint"

        by_customer = await complaint_repo.get_by_customer_id(customer.id)
        assert len(by_customer) == 1
        assert by_customer[0].id == complaint.id

        by_interaction = await complaint_repo.get_by_interaction_id(interaction.id)
        assert len(by_interaction) == 1
        assert by_interaction[0].id == complaint.id

    async def test_lifecycle_flow(self, db_session: AsyncSession) -> None:
        complaint_repo = ComplaintRepository(session=db_session)
        service = ComplaintService(
            repository=complaint_repo,
            customer_repository=CustomerRepository(session=db_session),
            interaction_repository=InteractionRepository(session=db_session),
        )

        created, _ = await service.create_complaint(
            ComplaintCreate(title="Lifecycle complaint", category=ComplaintCategory.CLAIMS)
        )
        assert created.status == ComplaintStatus.SUBMITTED

        escalated, events = await service.escalate_complaint(created.id)
        assert escalated.status == ComplaintStatus.ESCALATED
        assert len(events) == 1

        resolved, events = await service.resolve_complaint(escalated.id)
        assert resolved.status == ComplaintStatus.RESOLVED
        assert len(events) == 1

        closed, events = await service.close_complaint(resolved.id)
        assert closed.status == ComplaintStatus.CLOSED
        assert len(events) == 1

    async def test_full_api_flow_with_cross_domain_references(
        self,
        client: AsyncClient,
    ) -> None:
        customer_resp = await client.post(
            "/api/v1/customers",
            json={"external_ref": "API-COMP-001", "full_name": "API Complaint Customer"},
        )
        assert customer_resp.status_code == 201
        customer_id = customer_resp.json()["data"]["id"]

        interaction_resp = await client.post(
            "/api/v1/interactions",
            json={"channel": "email", "subject": "Complaint reference"},
        )
        assert interaction_resp.status_code == 201
        interaction_id = interaction_resp.json()["data"]["id"]

        create_resp = await client.post(
            "/api/v1/complaints",
            json={
                "customer_id": customer_id,
                "interaction_id": interaction_id,
                "title": "API flow complaint",
                "category": "service",
            },
        )
        assert create_resp.status_code == 201
        complaint_id = create_resp.json()["data"]["id"]
        assert create_resp.json()["data"]["customer_id"] == customer_id
        assert create_resp.json()["data"]["interaction_id"] == interaction_id

        get_resp = await client.get(f"/api/v1/complaints/{complaint_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["title"] == "API flow complaint"

        assign_resp = await client.post(
            f"/api/v1/complaints/{complaint_id}/assign",
            json={"agent_id": "11111111-1111-1111-1111-111111111111", "queue": "priority"},
        )
        assert assign_resp.status_code == 200
        assert assign_resp.json()["data"]["assigned_queue"] == "priority"

        escalate_resp = await client.post(f"/api/v1/complaints/{complaint_id}/escalate")
        assert escalate_resp.status_code == 200
        assert escalate_resp.json()["data"]["status"] == "escalated"

        list_resp = await client.get("/api/v1/complaints?status=escalated")
        assert list_resp.status_code == 200
        ids = [item["id"] for item in list_resp.json()["data"]]
        assert complaint_id in ids


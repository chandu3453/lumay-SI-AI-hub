"""Customer domain integration flow tests."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from domains.customer.constants.customer_constants import (
    CommunicationChannel,
    CustomerStatus,
    CustomerType,
)
from domains.customer.models.customer import Customer
from domains.customer.repositories.customer_repository import CustomerRepository
from domains.customer.schemas.customer_schema import CustomerCreateRequest
from domains.customer.services.customer_service import CustomerService


@pytest.mark.asyncio
class TestCustomerFlow:
    """End-to-end flow through the entire customer layer."""

    async def test_create_and_retrieve_flow(
        self, db_session: AsyncSession,
    ) -> None:
        repo = CustomerRepository(session=db_session)
        service = CustomerService(repository=repo)

        data = CustomerCreateRequest(
            external_ref="FLOW-001",
            full_name="Integration Tester",
            email="flow@example.com",
            mobile_number="+9876543210",
            customer_type=CustomerType.ACTIVE,
            communication_channel=CommunicationChannel.EMAIL,
        )
        customer, events = await service.create_customer(data)
        assert customer.id is not None
        assert customer.external_ref == "FLOW-001"
        assert customer.full_name == "Integration Tester"
        assert customer.email == "flow@example.com"
        assert customer.mobile_number == "+9876543210"
        assert customer.customer_type == CustomerType.ACTIVE
        assert customer.status == CustomerStatus.ACTIVE
        assert len(events) == 1

        fetched = await service.get_customer(customer.id)
        assert fetched.id == customer.id
        assert fetched.full_name == "Integration Tester"

        by_ref = await service.get_customer_by_external_ref("FLOW-001")
        assert by_ref.id == customer.id

    async def test_lifecycle_flow(self, db_session: AsyncSession) -> None:
        repo = CustomerRepository(session=db_session)
        service = CustomerService(repository=repo)

        created, _ = await service.create_customer(
            CustomerCreateRequest(
                external_ref="LIFE-001",
                full_name="Lifecycle User",
            ),
        )
        assert created.status == CustomerStatus.ACTIVE

        deactivated, events = await service.deactivate_customer(created.id)
        assert deactivated.status == CustomerStatus.INACTIVE
        assert len(events) == 1

        activated, events = await service.activate_customer(deactivated.id)
        assert activated.status == CustomerStatus.ACTIVE
        assert len(events) == 1

        archived, events = await service.archive_customer(activated.id)
        assert archived.status == CustomerStatus.ARCHIVED
        assert len(events) == 1

    async def test_full_api_flow(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/customers",
            json={
                "external_ref": "API-FLOW-001",
                "full_name": "API Flow User",
                "email": "apiflow@example.com",
                "customer_type": "prospect",
            },
        )
        assert create_resp.status_code == 201
        customer_id = create_resp.json()["data"]["id"]
        assert create_resp.json()["data"]["status"] == "active"

        get_resp = await client.get(f"/api/v1/customers/{customer_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["full_name"] == "API Flow User"

        update_resp = await client.patch(
            f"/api/v1/customers/{customer_id}",
            json={"full_name": "Updated via API"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["data"]["full_name"] == "Updated via API"

        deactivate_resp = await client.post(
            f"/api/v1/customers/{customer_id}/deactivate",
        )
        assert deactivate_resp.status_code == 200
        assert deactivate_resp.json()["data"]["status"] == "inactive"

        activate_resp = await client.post(
            f"/api/v1/customers/{customer_id}/activate",
        )
        assert activate_resp.status_code == 200
        assert activate_resp.json()["data"]["status"] == "active"

        archive_resp = await client.post(
            f"/api/v1/customers/{customer_id}/archive",
        )
        assert archive_resp.status_code == 200
        assert archive_resp.json()["data"]["status"] == "archived"

        list_resp = await client.get(
            "/api/v1/customers?status=archived",
        )
        assert list_resp.status_code == 200
        ids = [i["id"] for i in list_resp.json()["data"]]
        assert customer_id in ids

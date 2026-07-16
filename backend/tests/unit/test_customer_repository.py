"""Customer repository unit tests."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from domains.customer.constants.customer_constants import (
    CommunicationChannel,
    CustomerStatus,
    CustomerType,
)
from domains.customer.models.customer import Customer
from domains.customer.repositories.customer_repository import CustomerRepository


@pytest.fixture
async def repo(db_session: AsyncSession) -> CustomerRepository:
    return CustomerRepository(session=db_session)


@pytest.mark.asyncio
class TestCustomerRepository:
    async def test_create_customer(self, repo: CustomerRepository) -> None:
        customer = await repo.create(
            external_ref="CUST-001",
            full_name="John Doe",
            email="john@example.com",
            mobile_number="+1234567890",
            customer_type=CustomerType.ACTIVE,
            communication_channel=CommunicationChannel.EMAIL,
            segment="individual",
            status=CustomerStatus.ACTIVE,
        )
        assert customer.id is not None
        assert customer.external_ref == "CUST-001"
        assert customer.full_name == "John Doe"
        assert customer.email == "john@example.com"
        assert customer.mobile_number == "+1234567890"
        assert customer.customer_type == CustomerType.ACTIVE
        assert customer.communication_channel == CommunicationChannel.EMAIL
        assert customer.status == CustomerStatus.ACTIVE

    async def test_get_by_id_found(self, repo: CustomerRepository) -> None:
        created = await repo.create(
            external_ref="CUST-002",
            full_name="Jane Doe",
        )
        fetched = await repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.full_name == "Jane Doe"

    async def test_get_by_id_not_found(self, repo: CustomerRepository) -> None:
        fetched = await repo.get_by_id(uuid.uuid4())
        assert fetched is None

    async def test_get_by_external_ref_found(
        self, repo: CustomerRepository,
    ) -> None:
        await repo.create(
            external_ref="REF-001",
            full_name="Alice",
        )
        fetched = await repo.get_by_external_ref("REF-001")
        assert fetched is not None
        assert fetched.external_ref == "REF-001"

    async def test_get_by_external_ref_not_found(
        self, repo: CustomerRepository,
    ) -> None:
        fetched = await repo.get_by_external_ref("NONEXISTENT")
        assert fetched is None

    async def test_get_by_email_found(self, repo: CustomerRepository) -> None:
        await repo.create(
            external_ref="CUST-003",
            full_name="Bob",
            email="bob@example.com",
        )
        fetched = await repo.get_by_email("bob@example.com")
        assert fetched is not None
        assert fetched.email == "bob@example.com"

    async def test_get_by_email_not_found(
        self, repo: CustomerRepository,
    ) -> None:
        fetched = await repo.get_by_email("missing@example.com")
        assert fetched is None

    async def test_update_customer(self, repo: CustomerRepository) -> None:
        created = await repo.create(
            external_ref="CUST-004",
            full_name="Original Name",
        )
        updated = await repo.update(
            created.id, full_name="Updated Name",
        )
        assert updated is not None
        assert updated.full_name == "Updated Name"
        assert updated.id == created.id

    async def test_update_not_found(self, repo: CustomerRepository) -> None:
        updated = await repo.update(uuid.uuid4(), full_name="Nope")
        assert updated is None

    async def test_list_without_filters(self, repo: CustomerRepository) -> None:
        await repo.create(external_ref="LST-001", full_name="A")
        await repo.create(external_ref="LST-002", full_name="B")
        items, total = await repo.list()
        assert total >= 2
        assert len(items) == total

    async def test_list_with_customer_type_filter(
        self, repo: CustomerRepository,
    ) -> None:
        await repo.create(external_ref="TYP-001", full_name="A",
                          customer_type=CustomerType.PROSPECT)
        await repo.create(external_ref="TYP-002", full_name="B",
                          customer_type=CustomerType.ACTIVE)
        items, total = await repo.list(customer_type=CustomerType.PROSPECT)
        assert total >= 1
        assert all(i.customer_type == CustomerType.PROSPECT for i in items)

    async def test_list_with_status_filter(
        self, repo: CustomerRepository,
    ) -> None:
        await repo.create(external_ref="STA-001", full_name="A",
                          status=CustomerStatus.INACTIVE)
        items, total = await repo.list(status=CustomerStatus.ACTIVE)
        assert total == 0

    async def test_list_with_communication_channel_filter(
        self, repo: CustomerRepository,
    ) -> None:
        await repo.create(external_ref="CHN-001", full_name="A",
                          communication_channel=CommunicationChannel.EMAIL)
        await repo.create(external_ref="CHN-002", full_name="B",
                          communication_channel=CommunicationChannel.PHONE)
        items, total = await repo.list(
            communication_channel=CommunicationChannel.EMAIL,
        )
        assert total >= 1
        assert all(
            i.communication_channel == CommunicationChannel.EMAIL
            for i in items
        )

    async def test_list_pagination(self, repo: CustomerRepository) -> None:
        for i in range(5):
            await repo.create(
                external_ref=f"PAG-{i:03d}", full_name=f"User {i}",
            )
        page1, total = await repo.list(page=1, page_size=2)
        assert len(page1) == 2
        assert total == 5
        page2, _ = await repo.list(page=2, page_size=2)
        assert len(page2) == 2
        page3, _ = await repo.list(page=3, page_size=2)
        assert len(page3) == 1

    async def test_soft_deleted_customer_excluded_from_queries(
        self, repo: CustomerRepository,
    ) -> None:
        created = await repo.create(
            external_ref="DEL-001",
            full_name="To Be Deleted",
        )
        created.is_deleted = True
        from sqlalchemy import update
        from sqlalchemy import text as sa_text
        await repo._session.execute(
            update(Customer).where(Customer.id == created.id).values(
                is_deleted=True,
            )
        )
        await repo._session.flush()

        by_id = await repo.get_by_id(created.id)
        assert by_id is not None
        assert by_id.is_deleted is True

        by_ref = await repo.get_by_external_ref("DEL-001")
        assert by_ref is None

        items, total = await repo.list()
        assert all(not i.is_deleted for i in items)

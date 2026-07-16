"""Complaint repository unit tests."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from domains.complaint.constants.complaint_constants import (
    ComplaintCategory,
    ComplaintPriority,
    ComplaintSeverity,
    ComplaintStatus,
)
from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.customer.repositories.customer_repository import CustomerRepository
from domains.interaction.constants.interaction_constants import InteractionChannel
from domains.interaction.repositories.interaction_repository import InteractionRepository


@pytest.fixture
async def repo(db_session: AsyncSession) -> ComplaintRepository:
    return ComplaintRepository(session=db_session)


@pytest.mark.asyncio
class TestComplaintRepository:
    async def test_create_complaint(self, repo: ComplaintRepository) -> None:
        complaint = await repo.create(
            title="Late payout",
            description="Claim payout was delayed.",
            category=ComplaintCategory.CLAIMS,
            priority=ComplaintPriority.HIGH,
            severity=ComplaintSeverity.MAJOR,
        )
        assert complaint.id is not None
        assert complaint.title == "Late payout"
        assert complaint.status == ComplaintStatus.SUBMITTED
        assert complaint.category == ComplaintCategory.CLAIMS

    async def test_get_by_id_found(self, repo: ComplaintRepository) -> None:
        created = await repo.create(
            title="Wrong premium",
            category=ComplaintCategory.BILLING,
        )
        fetched = await repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.title == "Wrong premium"

    async def test_get_by_id_not_found(self, repo: ComplaintRepository) -> None:
        fetched = await repo.get_by_id(uuid.uuid4())
        assert fetched is None

    async def test_update_complaint(self, repo: ComplaintRepository) -> None:
        created = await repo.create(
            title="Original title",
            category=ComplaintCategory.SERVICE,
        )
        updated = await repo.update(
            created.id,
            title="Updated title",
            priority=ComplaintPriority.CRITICAL,
        )
        assert updated is not None
        assert updated.title == "Updated title"
        assert updated.priority == ComplaintPriority.CRITICAL

    async def test_update_not_found(self, repo: ComplaintRepository) -> None:
        updated = await repo.update(uuid.uuid4(), title="Nope")
        assert updated is None

    async def test_list_without_filters(self, repo: ComplaintRepository) -> None:
        await repo.create(title="Complaint A", category=ComplaintCategory.GENERAL)
        await repo.create(title="Complaint B", category=ComplaintCategory.SERVICE)
        items, total = await repo.list()
        assert total == 2
        assert len(items) == 2

    async def test_list_filters_by_status(
        self,
        repo: ComplaintRepository,
    ) -> None:
        await repo.create(
            title="Resolved complaint",
            category=ComplaintCategory.GENERAL,
            status=ComplaintStatus.RESOLVED,
        )
        await repo.create(
            title="Submitted complaint",
            category=ComplaintCategory.GENERAL,
        )
        items, total = await repo.list(status=ComplaintStatus.RESOLVED)
        assert total == 1
        assert all(item.status == ComplaintStatus.RESOLVED for item in items)

    async def test_list_filters_by_category(
        self,
        repo: ComplaintRepository,
    ) -> None:
        await repo.create(title="Policy issue", category=ComplaintCategory.POLICY)
        await repo.create(title="Tech issue", category=ComplaintCategory.TECHNICAL)
        items, total = await repo.list(category=ComplaintCategory.POLICY)
        assert total == 1
        assert all(item.category == ComplaintCategory.POLICY for item in items)

    async def test_list_filters_by_priority(
        self,
        repo: ComplaintRepository,
    ) -> None:
        await repo.create(
            title="Critical complaint",
            category=ComplaintCategory.GENERAL,
            priority=ComplaintPriority.CRITICAL,
        )
        await repo.create(
            title="Low complaint",
            category=ComplaintCategory.GENERAL,
            priority=ComplaintPriority.LOW,
        )
        items, total = await repo.list(priority=ComplaintPriority.CRITICAL)
        assert total == 1
        assert all(item.priority == ComplaintPriority.CRITICAL for item in items)

    async def test_list_filters_by_severity(
        self,
        repo: ComplaintRepository,
    ) -> None:
        await repo.create(
            title="Major issue",
            category=ComplaintCategory.GENERAL,
            severity=ComplaintSeverity.MAJOR,
        )
        await repo.create(
            title="Minor issue",
            category=ComplaintCategory.GENERAL,
            severity=ComplaintSeverity.MINOR,
        )
        items, total = await repo.list(severity=ComplaintSeverity.MAJOR)
        assert total == 1
        assert all(item.severity == ComplaintSeverity.MAJOR for item in items)

    async def test_get_complaints_by_customer(
        self,
        repo: ComplaintRepository,
        db_session: AsyncSession,
    ) -> None:
        customer = await CustomerRepository(session=db_session).create(
            external_ref="COMP-CUST-001",
            full_name="Complaint Customer",
        )
        other_customer = await CustomerRepository(session=db_session).create(
            external_ref="COMP-CUST-002",
            full_name="Other Customer",
        )
        await repo.create(
            title="Customer complaint",
            category=ComplaintCategory.SERVICE,
            customer_id=customer.id,
        )
        await repo.create(
            title="Other complaint",
            category=ComplaintCategory.SERVICE,
            customer_id=other_customer.id,
        )

        items = await repo.get_by_customer_id(customer.id)
        assert len(items) == 1
        assert items[0].customer_id == customer.id

    async def test_get_complaints_by_interaction(
        self,
        repo: ComplaintRepository,
        db_session: AsyncSession,
    ) -> None:
        interaction_repo = InteractionRepository(session=db_session)
        interaction = await interaction_repo.create(channel=InteractionChannel.EMAIL)
        other_interaction = await interaction_repo.create(channel=InteractionChannel.VOICE)
        await repo.create(
            title="Interaction complaint",
            category=ComplaintCategory.SERVICE,
            interaction_id=interaction.id,
        )
        await repo.create(
            title="Other interaction complaint",
            category=ComplaintCategory.SERVICE,
            interaction_id=other_interaction.id,
        )

        items = await repo.get_by_interaction_id(interaction.id)
        assert len(items) == 1
        assert items[0].interaction_id == interaction.id

    async def test_list_pagination(self, repo: ComplaintRepository) -> None:
        for index in range(5):
            await repo.create(
                title=f"Complaint {index}",
                category=ComplaintCategory.GENERAL,
            )
        page1, total = await repo.list(page=1, page_size=2)
        page2, _ = await repo.list(page=2, page_size=2)
        page3, _ = await repo.list(page=3, page_size=2)
        assert total == 5
        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1


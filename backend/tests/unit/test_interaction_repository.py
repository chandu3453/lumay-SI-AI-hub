"""Interaction repository unit tests."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from domains.interaction.constants.interaction_constants import (
    InteractionChannel,
    InteractionDirection,
    InteractionStatus,
)
from domains.interaction.models.interaction import Interaction
from domains.interaction.repositories.interaction_repository import InteractionRepository


@pytest.fixture
async def repo(db_session: AsyncSession) -> InteractionRepository:
    return InteractionRepository(session=db_session)


@pytest.mark.asyncio
class TestInteractionRepository:
    async def test_create_interaction(self, repo: InteractionRepository) -> None:
        interaction = await repo.create(
            customer_ref="CUST-001",
            channel=InteractionChannel.EMAIL,
            direction=InteractionDirection.INBOUND,
            subject="Test subject",
            transcript="Hello world",
            attachments=["file1.pdf"],
        )
        assert interaction.id is not None
        assert interaction.customer_ref == "CUST-001"
        assert interaction.channel == InteractionChannel.EMAIL
        assert interaction.direction == InteractionDirection.INBOUND
        assert interaction.subject == "Test subject"
        assert interaction.transcript == "Hello world"
        assert interaction.attachments == ["file1.pdf"]
        assert interaction.status == InteractionStatus.RECEIVED

    async def test_get_by_id_found(self, repo: InteractionRepository) -> None:
        created = await repo.create(
            channel=InteractionChannel.VOICE,
            direction=InteractionDirection.OUTBOUND,
        )
        fetched = await repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.channel == InteractionChannel.VOICE

    async def test_get_by_id_not_found(self, repo: InteractionRepository) -> None:
        fetched = await repo.get_by_id(uuid.uuid4())
        assert fetched is None

    async def test_update_interaction(self, repo: InteractionRepository) -> None:
        created = await repo.create(
            channel=InteractionChannel.TEAMS,
            subject="Original",
        )
        updated = await repo.update(created.id, subject="Updated subject")
        assert updated is not None
        assert updated.subject == "Updated subject"
        assert updated.id == created.id

    async def test_update_not_found(self, repo: InteractionRepository) -> None:
        updated = await repo.update(uuid.uuid4(), subject="Nope")
        assert updated is None

    async def test_list_without_filters(self, repo: InteractionRepository) -> None:
        await repo.create(channel=InteractionChannel.EMAIL)
        await repo.create(channel=InteractionChannel.VOICE)
        items, total = await repo.list()
        assert total >= 2
        assert len(items) == total

    async def test_list_with_channel_filter(self, repo: InteractionRepository) -> None:
        await repo.create(channel=InteractionChannel.EMAIL)
        await repo.create(channel=InteractionChannel.VOICE)
        items, total = await repo.list(channel=InteractionChannel.EMAIL)
        assert total >= 1
        assert all(i.channel == InteractionChannel.EMAIL for i in items)

    async def test_list_with_status_filter(self, repo: InteractionRepository) -> None:
        await repo.create(channel=InteractionChannel.WHATSAPP)
        items, total = await repo.list(status=InteractionStatus.PROCESSING)
        assert total == 0

    async def test_list_pagination(self, repo: InteractionRepository) -> None:
        for _ in range(5):
            await repo.create(channel=InteractionChannel.API)
        page1, total = await repo.list(page=1, page_size=2)
        assert len(page1) == 2
        assert total == 5
        page2, _ = await repo.list(page=2, page_size=2)
        assert len(page2) == 2
        page3, _ = await repo.list(page=3, page_size=2)
        assert len(page3) == 1

    async def test_delete_interaction(self, repo: InteractionRepository) -> None:
        created = await repo.create(channel=InteractionChannel.TEAMS)
        await repo.delete(created)
        fetched = await repo.get_by_id(created.id)
        assert fetched is None

"""Interaction domain integration flow tests."""

import pytest
from httpx import AsyncClient

from domains.interaction.constants.interaction_constants import (
    InteractionChannel,
    InteractionDirection,
    InteractionStatus,
)
from domains.interaction.models.interaction import Interaction
from domains.interaction.repositories.interaction_repository import InteractionRepository
from domains.interaction.schemas.interaction_schemas import InteractionCreate
from domains.interaction.services.interaction_service import InteractionService
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestInteractionFlow:
    """End-to-end flow through the entire interaction layer."""

    async def test_create_and_retrieve_flow(self, db_session: AsyncSession) -> None:
        repo = InteractionRepository(session=db_session)
        service = InteractionService(repository=repo)

        data = InteractionCreate(
            customer_ref="FLOW-001",
            channel=InteractionChannel.EMAIL,
            direction=InteractionDirection.INBOUND,
            subject="Integration test",
            transcript="Full flow test",
            attachments=["doc.pdf"],
        )
        interaction, events = await service.create_interaction(data)
        assert interaction.id is not None
        assert interaction.customer_ref == "FLOW-001"
        assert interaction.status == InteractionStatus.RECEIVED
        assert len(events) == 1

        fetched = await service.get_interaction(interaction.id)
        assert fetched.id == interaction.id
        assert fetched.subject == "Integration test"

    async def test_close_and_archive_flow(self, db_session: AsyncSession) -> None:
        repo = InteractionRepository(session=db_session)
        service = InteractionService(repository=repo)

        created, _ = await service.create_interaction(
            InteractionCreate(channel=InteractionChannel.VOICE),
        )

        closed, events = await service.close_interaction(created.id)
        assert closed.status == InteractionStatus.COMPLETED
        assert len(events) == 1

        archived, events = await service.archive_interaction(closed.id)
        assert archived.status == InteractionStatus.ARCHIVED
        assert len(events) == 1

    async def test_full_api_flow(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/interactions",
            json={
                "channel": "web_form",
                "direction": "inbound",
                "subject": "API flow test",
            },
        )
        assert create_resp.status_code == 201
        interaction_id = create_resp.json()["data"]["id"]

        get_resp = await client.get(f"/api/v1/interactions/{interaction_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["subject"] == "API flow test"

        update_resp = await client.patch(
            f"/api/v1/interactions/{interaction_id}",
            json={"subject": "Updated via API"},
        )
        assert update_resp.status_code == 200

        close_resp = await client.post(f"/api/v1/interactions/{interaction_id}/close")
        assert close_resp.status_code == 200
        assert close_resp.json()["data"]["status"] == "completed"

        archive_resp = await client.post(
            f"/api/v1/interactions/{interaction_id}/archive",
        )
        assert archive_resp.status_code == 200
        assert archive_resp.json()["data"]["status"] == "archived"

        list_resp = await client.get(
            "/api/v1/interactions?status=archived",
        )
        assert list_resp.status_code == 200
        ids = [i["id"] for i in list_resp.json()["data"]]
        assert interaction_id in ids

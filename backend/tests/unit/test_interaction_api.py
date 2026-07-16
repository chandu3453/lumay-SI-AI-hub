"""Interaction REST API unit tests."""

import uuid

import pytest
from httpx import AsyncClient

from domains.interaction.constants.interaction_constants import InteractionChannel


@pytest.mark.asyncio
class TestInteractionAPI:
    async def test_create_interaction_201(self, client: AsyncClient) -> None:
        payload = {
            "channel": "email",
            "direction": "inbound",
            "subject": "Test interaction",
            "transcript": "Hello from test",
        }
        response = await client.post("/api/v1/interactions", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["channel"] == "email"
        assert body["data"]["subject"] == "Test interaction"
        assert body["data"]["status"] == "received"
        assert "id" in body["data"]
        assert "created_at" in body["data"]

    async def test_create_interaction_missing_channel_422(
        self, client: AsyncClient,
    ) -> None:
        payload = {"subject": "No channel"}
        response = await client.post("/api/v1/interactions", json=payload)
        assert response.status_code == 422

    async def test_create_interaction_invalid_channel_422(
        self, client: AsyncClient,
    ) -> None:
        payload = {"channel": "invalid_channel"}
        response = await client.post("/api/v1/interactions", json=payload)
        assert response.status_code == 422

    async def test_get_interaction_200(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/interactions", json={"channel": "email"})
        interaction_id = create_resp.json()["data"]["id"]

        response = await client.get(f"/api/v1/interactions/{interaction_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] == interaction_id

    async def test_get_interaction_404(self, client: AsyncClient) -> None:
        response = await client.get(f"/api/v1/interactions/{uuid.uuid4()}")
        assert response.status_code == 404
        body = response.json()
        assert body["success"] is False
        assert body["error_code"] == "INTERACTION__NOT_FOUND"

    async def test_list_interactions_200(self, client: AsyncClient) -> None:
        await client.post("/api/v1/interactions", json={"channel": "email"})
        await client.post("/api/v1/interactions", json={"channel": "voice"})

        response = await client.get("/api/v1/interactions")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert body["total"] >= 2
        assert body["page"] == 1
        assert body["page_size"] == 20

    async def test_list_interactions_with_filters(
        self, client: AsyncClient,
    ) -> None:
        await client.post("/api/v1/interactions", json={"channel": "email"})
        await client.post("/api/v1/interactions", json={"channel": "voice"})

        response = await client.get("/api/v1/interactions?channel=email")
        assert response.status_code == 200
        body = response.json()
        assert all(i["channel"] == "email" for i in body["data"])

    async def test_update_interaction_200(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/interactions", json={"channel": "email", "subject": "Original"},
        )
        interaction_id = create_resp.json()["data"]["id"]

        response = await client.patch(
            f"/api/v1/interactions/{interaction_id}",
            json={"subject": "Updated"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["subject"] == "Updated"

    async def test_update_nonexistent_interaction_404(
        self, client: AsyncClient,
    ) -> None:
        response = await client.patch(
            f"/api/v1/interactions/{uuid.uuid4()}",
            json={"subject": "Nope"},
        )
        assert response.status_code == 404

    async def test_close_interaction_200(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/interactions", json={"channel": "email"})
        interaction_id = create_resp.json()["data"]["id"]

        response = await client.post(f"/api/v1/interactions/{interaction_id}/close")
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["status"] == "completed"

    async def test_close_already_completed_409(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/interactions", json={"channel": "email"})
        interaction_id = create_resp.json()["data"]["id"]

        await client.post(f"/api/v1/interactions/{interaction_id}/close")
        response = await client.post(f"/api/v1/interactions/{interaction_id}/close")
        assert response.status_code == 409

    async def test_archive_interaction_200(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/interactions", json={"channel": "email"})
        interaction_id = create_resp.json()["data"]["id"]

        response = await client.post(f"/api/v1/interactions/{interaction_id}/archive")
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["status"] == "archived"

    async def test_archive_already_archived_409(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/interactions", json={"channel": "email"})
        interaction_id = create_resp.json()["data"]["id"]

        await client.post(f"/api/v1/interactions/{interaction_id}/archive")
        response = await client.post(f"/api/v1/interactions/{interaction_id}/archive")
        assert response.status_code == 409

    async def test_update_archived_interaction_409(
        self, client: AsyncClient,
    ) -> None:
        create_resp = await client.post("/api/v1/interactions", json={"channel": "email"})
        interaction_id = create_resp.json()["data"]["id"]

        await client.post(f"/api/v1/interactions/{interaction_id}/archive")
        response = await client.patch(
            f"/api/v1/interactions/{interaction_id}",
            json={"subject": "Nope"},
        )
        assert response.status_code == 409

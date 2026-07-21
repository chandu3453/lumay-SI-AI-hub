"""Conversation domain integration tests — Sprint 28 Phase 4
(human-AI collaboration & live conversation management: ownership/handoff,
supervisor monitoring, internal note edit/delete, presence/typing)."""

import uuid

import pytest
from httpx import AsyncClient


async def _create_conversation(client: AsyncClient, channel: str = "web_chat") -> str:
    resp = await client.post("/api/v1/conversations", json={"current_channel": channel})
    return resp.json()["data"]["id"]


@pytest.mark.asyncio
class TestOwnershipHandoff:
    async def test_take_over_stops_ai_and_inserts_handoff_message(
        self, client: AsyncClient,
    ) -> None:
        conversation_id = await _create_conversation(client)
        employee_id = str(uuid.uuid4())

        resp = await client.post(
            f"/api/v1/conversations/{conversation_id}/take-over",
            json={"employee_id": employee_id},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["current_status"] == "human_handling"
        assert data["human_handling"] is True
        assert data["ai_handling"] is False
        assert data["assigned_employee_id"] == employee_id

        messages = await client.get(f"/api/v1/conversations/{conversation_id}/messages")
        contents = [m["content"] for m in messages.json()["data"]]
        assert "You are now connected with one of our insurance specialists." in contents

        participants = await client.get(f"/api/v1/conversations/{conversation_id}/participants")
        types = [p["participant_type"] for p in participants.json()["data"]]
        assert "employee" in types

        history = await client.get(f"/api/v1/conversations/{conversation_id}/assignment-history")
        event_types = [e["event_type"] for e in history.json()["data"]]
        assert "employee_joined" in event_types
        assert "ai_handed_over" in event_types

    async def test_release_resumes_ai_and_clears_assignment(
        self, client: AsyncClient,
    ) -> None:
        conversation_id = await _create_conversation(client)
        employee_id = str(uuid.uuid4())
        await client.post(
            f"/api/v1/conversations/{conversation_id}/take-over",
            json={"employee_id": employee_id},
        )

        resp = await client.post(f"/api/v1/conversations/{conversation_id}/release")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["current_status"] == "ai_handling"
        assert data["ai_handling"] is True
        assert data["human_handling"] is False
        assert data["assigned_employee_id"] is None

        history = await client.get(f"/api/v1/conversations/{conversation_id}/assignment-history")
        event_types = [e["event_type"] for e in history.json()["data"]]
        assert "employee_left" in event_types

    async def test_transfer_preserves_previous_and_new_owner(
        self, client: AsyncClient,
    ) -> None:
        conversation_id = await _create_conversation(client)
        first_employee = str(uuid.uuid4())
        second_employee = str(uuid.uuid4())
        await client.post(
            f"/api/v1/conversations/{conversation_id}/take-over",
            json={"employee_id": first_employee},
        )

        resp = await client.post(
            f"/api/v1/conversations/{conversation_id}/transfer",
            json={"employee_id": second_employee},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["assigned_employee_id"] == second_employee
        # Still human-handled — a transfer never bounces through AI.
        assert resp.json()["data"]["current_status"] == "human_handling"

        history = await client.get(f"/api/v1/conversations/{conversation_id}/assignment-history")
        transfer_events = [
            e for e in history.json()["data"] if e["event_type"] == "conversation_transferred"
        ]
        assert len(transfer_events) == 1
        assert transfer_events[0]["payload"]["previous_owner"] == first_employee
        assert transfer_events[0]["payload"]["new_owner"] == second_employee

    async def test_accept_records_event_without_changing_ownership(
        self, client: AsyncClient,
    ) -> None:
        conversation_id = await _create_conversation(client)
        employee_id = str(uuid.uuid4())
        await client.post(
            f"/api/v1/conversations/{conversation_id}/take-over",
            json={"employee_id": employee_id},
        )

        resp = await client.post(
            f"/api/v1/conversations/{conversation_id}/accept",
            json={"employee_id": employee_id},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["assigned_employee_id"] == employee_id

        history = await client.get(f"/api/v1/conversations/{conversation_id}/assignment-history")
        event_types = [e["event_type"] for e in history.json()["data"]]
        assert "conversation_accepted" in event_types


@pytest.mark.asyncio
class TestSupervisorMode:
    async def test_supervisor_join_and_leave_never_touch_assignment(
        self, client: AsyncClient,
    ) -> None:
        conversation_id = await _create_conversation(client)
        employee_id = str(uuid.uuid4())
        supervisor_id = str(uuid.uuid4())
        await client.post(
            f"/api/v1/conversations/{conversation_id}/take-over",
            json={"employee_id": employee_id},
        )

        join_resp = await client.post(
            f"/api/v1/conversations/{conversation_id}/supervisor/join",
            json={"supervisor_id": supervisor_id},
        )
        assert join_resp.status_code == 200
        assert join_resp.json()["data"]["participant_type"] == "supervisor"

        conversation = await client.get(f"/api/v1/conversations/{conversation_id}")
        assert conversation.json()["data"]["assigned_employee_id"] == employee_id
        assert conversation.json()["data"]["current_status"] == "human_handling"

        leave_resp = await client.post(
            f"/api/v1/conversations/{conversation_id}/supervisor/leave",
            json={"supervisor_id": supervisor_id},
        )
        assert leave_resp.status_code == 200
        # Still unaffected after leave.
        conversation_after = await client.get(f"/api/v1/conversations/{conversation_id}")
        assert conversation_after.json()["data"]["assigned_employee_id"] == employee_id

        history = await client.get(f"/api/v1/conversations/{conversation_id}/assignment-history")
        event_types = [e["event_type"] for e in history.json()["data"]]
        assert "supervisor_joined" in event_types
        assert "supervisor_left" in event_types

    async def test_supervisor_join_is_idempotent(self, client: AsyncClient) -> None:
        conversation_id = await _create_conversation(client)
        supervisor_id = str(uuid.uuid4())

        first = await client.post(
            f"/api/v1/conversations/{conversation_id}/supervisor/join",
            json={"supervisor_id": supervisor_id},
        )
        second = await client.post(
            f"/api/v1/conversations/{conversation_id}/supervisor/join",
            json={"supervisor_id": supervisor_id},
        )
        assert first.json()["data"]["id"] == second.json()["data"]["id"]

        participants = await client.get(f"/api/v1/conversations/{conversation_id}/participants")
        supervisors = [
            p for p in participants.json()["data"] if p["participant_type"] == "supervisor"
        ]
        assert len(supervisors) == 1


@pytest.mark.asyncio
class TestInternalNotes:
    async def test_create_edit_delete_internal_note(self, client: AsyncClient) -> None:
        conversation_id = await _create_conversation(client)

        create_resp = await client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={
                "sender_type": "employee",
                "channel": "web_chat",
                "content": "Customer sounded frustrated, escalate if repeats.",
                "metadata": {"internal": True},
            },
        )
        assert create_resp.status_code == 201
        message_id = create_resp.json()["data"]["id"]

        edit_resp = await client.patch(
            f"/api/v1/conversations/{conversation_id}/messages/{message_id}",
            json={"content": "Customer sounded frustrated — escalated to team lead."},
        )
        assert edit_resp.status_code == 200
        assert edit_resp.json()["data"]["content"] == (
            "Customer sounded frustrated — escalated to team lead."
        )

        delete_resp = await client.delete(
            f"/api/v1/conversations/{conversation_id}/messages/{message_id}"
        )
        assert delete_resp.status_code == 200
        assert delete_resp.json()["data"]["message_metadata"]["deleted"] is True

    async def test_customer_visible_message_cannot_be_edited_or_deleted(
        self, client: AsyncClient,
    ) -> None:
        conversation_id = await _create_conversation(client)
        create_resp = await client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            json={"sender_type": "customer", "channel": "web_chat", "content": "Hello"},
        )
        message_id = create_resp.json()["data"]["id"]

        edit_resp = await client.patch(
            f"/api/v1/conversations/{conversation_id}/messages/{message_id}",
            json={"content": "tampered"},
        )
        assert edit_resp.status_code == 422

        delete_resp = await client.delete(
            f"/api/v1/conversations/{conversation_id}/messages/{message_id}"
        )
        assert delete_resp.status_code == 422

    async def test_edit_nonexistent_message_returns_404(self, client: AsyncClient) -> None:
        conversation_id = await _create_conversation(client)
        resp = await client.patch(
            f"/api/v1/conversations/{conversation_id}/messages/{uuid.uuid4()}",
            json={"content": "edited"},
        )
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestPresenceAndTyping:
    async def test_presence_round_trip(self, client: AsyncClient) -> None:
        conversation_id = await _create_conversation(client)

        post_resp = await client.post(
            f"/api/v1/conversations/{conversation_id}/presence",
            json={"participant_type": "employee", "participant_ref": "emp-42", "status": "online"},
        )
        assert post_resp.status_code == 200
        assert post_resp.json()["data"]["presence"]["employee"]["emp-42"] == "online"

        get_resp = await client.get(f"/api/v1/conversations/{conversation_id}/presence")
        assert get_resp.json()["data"]["presence"]["employee"]["emp-42"] == "online"

    async def test_typing_round_trip(self, client: AsyncClient) -> None:
        conversation_id = await _create_conversation(client)

        post_resp = await client.post(
            f"/api/v1/conversations/{conversation_id}/typing",
            json={"participant_type": "customer", "is_typing": True},
        )
        assert post_resp.status_code == 200
        assert post_resp.json()["data"]["typing"]["customer"] is True

        get_resp = await client.get(f"/api/v1/conversations/{conversation_id}/presence")
        assert get_resp.json()["data"]["typing"]["customer"] is True

    async def test_presence_snapshot_reports_derived_flags(self, client: AsyncClient) -> None:
        conversation_id = await _create_conversation(client, channel="voice")
        employee_id = str(uuid.uuid4())
        await client.post(
            f"/api/v1/conversations/{conversation_id}/take-over",
            json={"employee_id": employee_id},
        )

        resp = await client.get(f"/api/v1/conversations/{conversation_id}/presence")
        data = resp.json()["data"]
        assert data["ai_active"] is False  # human_handling now, not ai_handling
        assert data["conversation_live"] is True

    async def test_presence_for_missing_conversation_404s(self, client: AsyncClient) -> None:
        resp = await client.get(f"/api/v1/conversations/{uuid.uuid4()}/presence")
        assert resp.status_code == 404


@pytest.mark.asyncio
class TestExternalRefLookup:
    async def test_resolve_conversation_by_interaction_id(
        self, db_session, client: AsyncClient,
    ) -> None:
        from domains.conversation import integration_hooks as conversation_hooks
        from domains.interaction.constants.interaction_constants import InteractionChannel
        from domains.interaction.repositories.interaction_repository import InteractionRepository
        from domains.interaction.schemas.interaction_schemas import InteractionCreate
        from domains.interaction.services.interaction_service import InteractionService

        interaction_service = InteractionService(repository=InteractionRepository(session=db_session))
        interaction, _ = await interaction_service.create_interaction(
            InteractionCreate(
                customer_ref=str(uuid.uuid4()), channel=InteractionChannel.WEB_FORM, transcript="[]"
            )
        )
        conversation_id = await conversation_hooks.on_interaction_started(
            db_session, interaction.customer_ref, "web_form", interaction.id
        )

        resp = await client.get(
            "/api/v1/conversations/by-external-ref",
            params={"ref_type": "interaction_id", "ref_id": str(interaction.id)},
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == str(conversation_id)

    async def test_unknown_ref_returns_404(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/api/v1/conversations/by-external-ref",
            params={"ref_type": "interaction_id", "ref_id": str(uuid.uuid4())},
        )
        assert resp.status_code == 404

"""process_conversation_stream — the voice-pipeline streaming counterpart to
process_conversation, added for real-time barge-in/latency work. Verifies it
yields incremental chunks then a final "done" event shaped like
process_conversation's synchronous return, and that the same post-processing
(transcript persistence) happens."""

import json
import uuid

import pytest

from ai.gateway.ai_gateway import AIGateway, AIGatewayConfig
from ai.prompts.base_prompt import reset_prompt_registry
from ai.prompts.templates import register_default_prompts
from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.complaint.services.complaint_service import ComplaintService
from domains.customer.repositories.customer_repository import CustomerRepository
from domains.interaction.constants.interaction_constants import InteractionChannel
from domains.interaction.repositories.interaction_repository import InteractionRepository
from domains.interaction.schemas.interaction_schemas import InteractionCreate
from domains.interaction.services.interaction_service import InteractionService
from domains.workflow.repositories.workflow_repository import WorkflowRepository
from domains.workflow.services.workflow_service import WorkflowService


@pytest.fixture(autouse=True)
def _setup_prompts():
    reset_prompt_registry()
    register_default_prompts()
    yield
    reset_prompt_registry()


@pytest.fixture(autouse=True)
def _use_local_ai_gateway(monkeypatch):
    """process_conversation_stream calls the module-level get_ai_gateway() —
    pin it to the deterministic local provider so this test doesn't depend on
    real network/credentials, matching the pattern already used for
    ComplaintIntelligenceService tests."""
    gateway = AIGateway(config=AIGatewayConfig(default_provider="local", default_model="local-dev"))
    monkeypatch.setattr(
        "domains.interaction.services.conversation_engine.get_ai_gateway",
        lambda: gateway,
    )


@pytest.mark.asyncio
class TestProcessConversationStream:
    async def _make_interaction(self, db_session):
        interaction_service = InteractionService(repository=InteractionRepository(session=db_session))
        interaction, _ = await interaction_service.create_interaction(
            InteractionCreate(channel=InteractionChannel.WEB_FORM)
        )
        return interaction, interaction_service

    def _make_services(self, db_session):
        complaint_repo = ComplaintRepository(session=db_session)
        customer_repo = CustomerRepository(session=db_session)
        complaint_service = ComplaintService(
            repository=complaint_repo,
            customer_repository=customer_repo,
            interaction_repository=InteractionRepository(session=db_session),
        )
        workflow_service = WorkflowService(
            repository=WorkflowRepository(session=db_session), complaint_repository=complaint_repo
        )
        return complaint_service, workflow_service

    async def test_stream_yields_chunks_then_done_event(self, db_session) -> None:
        from domains.interaction.services.conversation_engine import process_conversation_stream

        interaction, interaction_service = await self._make_interaction(db_session)
        complaint_service, workflow_service = self._make_services(db_session)

        events = [
            e
            async for e in process_conversation_stream(
                interaction_id=interaction.id,
                message="I have a question about my claim",
                interaction_service=interaction_service,
                complaint_service=complaint_service,
                workflow_service=workflow_service,
                notification_service=None,
            )
        ]

        chunk_events = [e for e in events if e["type"] == "chunk"]
        done_events = [e for e in events if e["type"] == "done"]

        assert len(chunk_events) > 1, "expected the response to arrive as multiple chunks"
        assert len(done_events) == 1
        done = done_events[0]
        assert done["answer"] == "".join(e["text"] for e in chunk_events)
        # Same response shape as the blocking process_conversation().
        assert set(done.keys()) >= {
            "answer", "messages", "ai_analysis", "context_used",
            "auto_triaged", "complaint_id", "workflow_id", "provider_used",
        }
        assert done["provider_used"] == "local"

    async def test_stream_persists_transcript_like_blocking_version(self, db_session) -> None:
        from domains.interaction.services.conversation_engine import process_conversation_stream

        interaction, interaction_service = await self._make_interaction(db_session)
        complaint_service, workflow_service = self._make_services(db_session)

        async for _ in process_conversation_stream(
            interaction_id=interaction.id,
            message="Hello",
            interaction_service=interaction_service,
            complaint_service=complaint_service,
            workflow_service=workflow_service,
            notification_service=None,
        ):
            pass

        refreshed = await interaction_service.get_interaction(interaction.id)
        history = json.loads(refreshed.transcript)
        roles = [m["role"] for m in history]
        assert roles == ["user", "assistant"]
        assert history[0]["content"] == "Hello"
        assert history[1]["content"]

    async def test_stream_unknown_interaction_raises_not_found(self, db_session) -> None:
        """interaction_service.get_interaction() raises rather than returning
        None (pre-existing behavior, unchanged by this refactor) — the
        _prepare_turn "not found" branch it feeds is unreachable through this
        path in both the old and new code; this just documents that."""
        from domains.interaction.exceptions.interaction_exceptions import InteractionNotFoundError
        from domains.interaction.services.conversation_engine import process_conversation_stream

        interaction_service = InteractionService(repository=InteractionRepository(session=db_session))
        complaint_service, workflow_service = self._make_services(db_session)

        with pytest.raises(InteractionNotFoundError):
            async for _ in process_conversation_stream(
                interaction_id=uuid.uuid4(),
                message="Hello",
                interaction_service=interaction_service,
                complaint_service=complaint_service,
                workflow_service=workflow_service,
                notification_service=None,
            ):
                pass

"""AI Platform — gateway unit tests."""

import pytest

from ai.gateway.ai_gateway import AIGateway, AIGatewayConfig, GatewayRequest
from ai.models import ChatMessage
from ai.prompts.base_prompt import reset_prompt_registry
from ai.prompts.templates import register_default_prompts


@pytest.fixture(autouse=True)
def _setup_prompts():
    reset_prompt_registry()
    register_default_prompts()
    yield
    reset_prompt_registry()


class TestAIGateway:
    def setup_method(self) -> None:
        config = AIGatewayConfig(default_provider="local", default_model="local-dev")
        self.gateway = AIGateway(config=config)

    async def test_generate(self) -> None:
        response = await self.gateway.generate(prompt="Hello")
        assert response.content is not None
        assert "LocalProvider" in response.content

    async def test_generate_with_system_prompt(self) -> None:
        response = await self.gateway.generate(
            prompt="Hello",
            system_prompt="You are helpful",
        )
        assert response.content is not None

    async def test_chat(self) -> None:
        messages = [ChatMessage(role="user", content="Hello")]
        response = await self.gateway.chat(messages=messages)
        assert response.message.content is not None
        assert response.message.role == "assistant"

    async def test_summarize(self) -> None:
        text = "This is a long text that needs to be summarized into a shorter version."
        result = await self.gateway.summarize(text=text, max_words=50)
        assert result.summary is not None
        assert result.original_length > 0
        assert result.summary_length > 0

    async def test_classify(self) -> None:
        result = await self.gateway.classify(text="This is a complaint about billing")
        assert result.label is not None
        assert result.confidence >= 0.0

    async def test_embed(self) -> None:
        response = await self.gateway.embed(input="Test text")
        assert response.dimensions == 4
        assert len(response.vectors) == 1

    async def test_embed_batch(self) -> None:
        response = await self.gateway.embed(input=["A", "B"])
        assert len(response.vectors) == 2

    async def test_process_generate_operation(self) -> None:
        request = GatewayRequest(
            operation="generate",
            payload={"prompt": "Hello"},
        )
        response = await self.gateway.process(request)
        assert response.success is True
        assert response.data is not None
        assert "content" in response.data
        assert response.latency_ms is not None

    async def test_process_chat_operation(self) -> None:
        request = GatewayRequest(
            operation="chat",
            payload={"messages": [{"role": "user", "content": "Hello"}]},
        )
        response = await self.gateway.process(request)
        assert response.success is True
        assert response.data is not None

    async def test_process_summarize_operation(self) -> None:
        request = GatewayRequest(
            operation="summarize",
            payload={"text": "Long text here for summarization.", "max_words": 50},
        )
        response = await self.gateway.process(request)
        assert response.success is True
        assert "summary" in response.data

    async def test_process_classify_operation(self) -> None:
        request = GatewayRequest(
            operation="classify",
            payload={"text": "Complaint about service"},
        )
        response = await self.gateway.process(request)
        assert response.success is True
        assert "label" in response.data

    async def test_process_embed_operation(self) -> None:
        request = GatewayRequest(
            operation="embed",
            payload={"input": "Test"},
        )
        response = await self.gateway.process(request)
        assert response.success is True
        assert "dimensions" in response.data

    async def test_process_unknown_operation(self) -> None:
        request = GatewayRequest(
            operation="unknown_op",
            payload={},
        )
        response = await self.gateway.process(request)
        assert response.success is False
        assert "Unknown operation" in response.error

    async def test_process_with_error(self) -> None:
        request = GatewayRequest(
            operation="generate",
            payload={"prompt": "Hello"},
            metadata={"provider": "nonexistent"},
        )
        self.gateway._provider = None
        self.gateway._config = AIGatewayConfig(default_provider="nonexistent")
        response = await self.gateway.process(request)
        assert response.success is False
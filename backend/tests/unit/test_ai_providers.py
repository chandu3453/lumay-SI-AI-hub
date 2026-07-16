"""AI Platform — provider unit tests."""

import pytest

from ai.models import AIRequest, ChatMessage, ChatRequest, EmbeddingRequest
from ai.providers.base import create_provider
from ai.providers.local_provider import LocalProvider


class TestLocalProvider:
    def setup_method(self) -> None:
        self.provider = LocalProvider()

    def test_provider_name(self) -> None:
        assert self.provider.provider_name == "local"

    async def test_generate(self) -> None:
        request = AIRequest(prompt="Hello, how are you?")
        response = await self.provider.generate(request)
        assert response.content is not None
        assert "LocalProvider" in response.content
        assert response.finish_reason == "stop"
        assert response.usage is not None
        assert response.usage.total_tokens == 20

    async def test_chat(self) -> None:
        messages = [ChatMessage(role="user", content="Hello")]
        request = ChatRequest(messages=messages)
        response = await self.provider.chat(request)
        assert response.message.content is not None
        assert "LocalProvider" in response.message.content
        assert response.message.role == "assistant"

    async def test_embed(self) -> None:
        request = EmbeddingRequest(input="Test text")
        response = await self.provider.embed(request)
        assert len(response.vectors) == 1
        assert response.dimensions == 4
        assert response.latency_ms is not None

    async def test_embed_batch(self) -> None:
        request = EmbeddingRequest(input=["Text A", "Text B"])
        response = await self.provider.embed(request)
        assert len(response.vectors) == 2

    async def test_generate_stream(self) -> None:
        tokens = []
        async for token in self.provider.generate_stream(
            [{"role": "user", "content": "Hello"}]
        ):
            tokens.append(token)
        assert len(tokens) > 0


class TestProviderFactory:
    def test_create_local(self) -> None:
        provider = create_provider("local")
        assert provider.provider_name == "local"

    def test_create_unknown_raises(self) -> None:
        from ai.exceptions import AIConfigurationError
        with pytest.raises(AIConfigurationError):
            create_provider("nonexistent_provider")
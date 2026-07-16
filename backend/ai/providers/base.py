"""Abstract interface for LLM provider adapters.

All providers (Azure OpenAI, OpenAI, Local) implement this contract.
"""

from abc import ABC, abstractmethod
from typing import Any
from typing import AsyncGenerator

from ai.models import AIRequest, AIResponse, ChatRequest, ChatResponse, EmbeddingRequest, EmbeddingResponse


class BaseLLMProvider(ABC):
    """Abstract contract all LLM providers must satisfy."""

    @abstractmethod
    async def generate(self, request: AIRequest) -> AIResponse:
        """Generates a text completion from a prompt."""
        ...

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Generates a response from a chat message list."""
        ...

    @abstractmethod
    async def generate_stream(
        self, messages: list[dict[str, Any]], **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Streams tokens from a chat message list."""
        ...

    @abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generates dense vector embeddings for the input text(s)."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the human-readable name of this provider."""
        ...


def create_provider(provider_name: str | None = None) -> BaseLLMProvider:
    """Factory method — creates a provider instance based on configuration."""
    from ai.config import get_ai_settings

    settings = get_ai_settings()
    name = provider_name or settings.default_provider

    if name == "azure_openai":
        from ai.providers.azure_openai import AzureOpenAIProvider
        return AzureOpenAIProvider()
    elif name == "openai":
        from ai.providers.openai_provider import OpenAIProvider
        return OpenAIProvider()
    elif name == "local":
        from ai.providers.local_provider import LocalProvider
        return LocalProvider()
    else:
        from ai.exceptions import AIConfigurationError
        raise AIConfigurationError(message=f"Unknown AI provider: {name}")
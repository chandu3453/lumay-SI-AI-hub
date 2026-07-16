"""
Anthropic provider adapter — wraps the Anthropic Claude API.

Implements BaseLLMProvider for the Anthropic API.
Reads API key and model settings from configuration.
"""

from typing import Any
from typing import AsyncGenerator

from ai.providers.base import BaseLLMProvider, EmbeddingRequest, LLMResponse


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider.

    Configuration required:
      - anthropic_api_key
      - anthropic_model (default: claude-sonnet-4-20250514)
    """

    def __init__(self) -> None:
        ...

    async def generate(self, messages: list[dict[str, Any]], **kwargs: Any) -> LLMResponse:
        ...

    async def generate_stream(
        self, messages: list[dict[str, Any]], **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        ...

    async def embed(self, request: EmbeddingRequest) -> list[list[float]]:
        ...

"""OpenAI provider adapter — wraps the OpenAI API.

Implements BaseLLMProvider for the OpenAI API.
Uses settings from app.config.settings for API key and model selection.
"""

import time
from typing import Any
from typing import AsyncGenerator

from openai import AsyncOpenAI

from ai.config import get_openai_settings
from ai.exceptions import (
    AIProviderAuthError,
    AIProviderError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
)
from ai.models import AIRequest, AIResponse, ChatMessage, ChatRequest, ChatResponse, EmbeddingRequest, EmbeddingResponse, TokenUsage
from ai.providers.base import BaseLLMProvider
from app.platform.logging import get_logger

logger = get_logger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider.

    Reads configuration from application settings:
      - openai.api_key
      - openai.model
      - openai.embedding_model
    """

    def __init__(self) -> None:
        settings = get_openai_settings()
        self._client = AsyncOpenAI(
            api_key=settings.api_key.get_secret_value(),
        )
        self._model = settings.model
        self._embedding_model = settings.embedding_model

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate(self, request: AIRequest) -> AIResponse:
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        start = time.monotonic()
        try:
            response = await self._client.chat.completions.create(
                model=request.model or self._model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        except Exception as exc:
            raise self._map_error(exc)

        elapsed = (time.monotonic() - start) * 1000
        choice = response.choices[0]
        usage = response.usage
        return AIResponse(
            content=choice.message.content or "",
            finish_reason=choice.finish_reason,
            model=response.model,
            usage=TokenUsage.build(
                prompt=usage.prompt_tokens if usage else 0,
                completion=usage.completion_tokens if usage else 0,
                latency_ms=elapsed,
            ),
        )

    async def chat(self, request: ChatRequest) -> ChatResponse:
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})

        start = time.monotonic()
        try:
            response = await self._client.chat.completions.create(
                model=request.model or self._model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        except Exception as exc:
            raise self._map_error(exc)

        elapsed = (time.monotonic() - start) * 1000
        choice = response.choices[0]
        usage = response.usage
        return ChatResponse(
            message=ChatMessage(role=choice.message.role or "assistant", content=choice.message.content or ""),
            finish_reason=choice.finish_reason,
            model=response.model,
            usage=TokenUsage.build(
                prompt=usage.prompt_tokens if usage else 0,
                completion=usage.completion_tokens if usage else 0,
                latency_ms=elapsed,
            ),
        )

    async def generate_stream(
        self, messages: list[dict[str, Any]], **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        model = kwargs.get("model", self._model)
        try:
            stream = await self._client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                temperature=kwargs.get("temperature", 0.0),
                max_tokens=kwargs.get("max_tokens"),
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    yield delta.content
        except Exception as exc:
            raise self._map_error(exc)

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        inputs = [request.input] if isinstance(request.input, str) else request.input
        start = time.monotonic()
        try:
            response = await self._client.embeddings.create(
                model=request.model or self._embedding_model,
                input=inputs,
            )
        except Exception as exc:
            raise self._map_error(exc)

        elapsed = (time.monotonic() - start) * 1000
        vectors = [item.embedding for item in response.data]
        return EmbeddingResponse(
            vectors=vectors,
            dimensions=len(vectors[0]) if vectors else 0,
            model=response.model,
            latency_ms=elapsed,
        )

    def _map_error(self, exc: Exception) -> AIProviderError:
        msg = str(exc).lower()
        if "rate limit" in msg or "429" in msg:
            return AIProviderRateLimitError(context={"detail": str(exc)})
        if "auth" in msg or "401" in msg or "key" in msg:
            return AIProviderAuthError(context={"detail": str(exc)})
        if "timeout" in msg or "timed out" in msg:
            return AIProviderTimeoutError(context={"detail": str(exc)})
        return AIProviderError(context={"detail": str(exc)})
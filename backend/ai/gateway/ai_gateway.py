"""AI Gateway — single entry point for all AI capabilities.

Domains consume AI through this gateway only.
The gateway delegates to providers, prompt management, and token tracking
while handling request validation, context assembly, and error handling.

Provider Fallback Chain:
  The gateway tries each provider in order until one succeeds.
  Default chain: azure_openai → openai → local
  On AuthError or RateLimitError it automatically falls through.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any
from typing import AsyncGenerator

from ai.config import get_ai_settings
from ai.exceptions import AIError, AIPromptError, AITokenLimitError, AIProviderAuthError, AIProviderRateLimitError, AIProviderError
from ai.models import (
    AIRequest,
    AIResponse,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ClassificationResult,
    EmbeddingRequest,
    EmbeddingResponse,
    PromptContext,
    SummarizationResult,
    TokenUsage,
)
from ai.providers.base import BaseLLMProvider, create_provider
from app.platform.logging import get_logger
from ai.token_usage import TokenTracker, estimate_tokens

logger = get_logger(__name__)

# Provider fallback order — the gateway will try each in sequence until one works.
_PROVIDER_FALLBACK_CHAIN = ["azure_openai", "openai", "local"]


@dataclass(frozen=True)
class AIGatewayConfig:
    default_provider: str = "azure_openai"
    default_model: str = "gpt-4o"
    max_retries: int = 3
    request_timeout_seconds: int = 60


@dataclass(frozen=True)
class GatewayRequest:
    operation: str
    payload: dict[str, Any]
    pipeline: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GatewayResponse:
    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    latency_ms: float | None = None
    usage: dict[str, int] | None = None


class AIGateway:
    def __init__(self, config: AIGatewayConfig | None = None) -> None:
        settings = get_ai_settings()
        self._config = config or AIGatewayConfig(
            default_provider=settings.default_provider,
            default_model=settings.default_model,
            max_retries=settings.max_retries,
            request_timeout_seconds=settings.request_timeout_seconds,
        )
        self._provider: BaseLLMProvider | None = None
        self._active_provider_name: str | None = None
        self._tracker = TokenTracker()

    @property
    def provider(self) -> BaseLLMProvider:
        if self._provider is None:
            self._provider, self._active_provider_name = self._init_provider_with_fallback()
        return self._provider

    @property
    def active_provider_name(self) -> str:
        """Returns the name of the currently active provider (after fallback resolution)."""
        _ = self.provider  # ensures initialization
        return self._active_provider_name or self._config.default_provider

    def _init_provider_with_fallback(self) -> tuple[BaseLLMProvider, str]:
        """Creates the first available provider by trying the fallback chain.

        Returns the provider and its name. Does NOT make any API calls —
        just instantiates clients so fast errors (missing config) are caught here.
        """
        chain = _PROVIDER_FALLBACK_CHAIN[:]
        # Ensure the configured default is first
        preferred = self._config.default_provider
        if preferred in chain:
            chain.remove(preferred)
        chain.insert(0, preferred)

        for name in chain:
            try:
                p = create_provider(name)
                logger.debug("ai_gateway_provider_initialized", provider=name)
                return p, name
            except Exception as exc:
                logger.warning("ai_gateway_provider_init_failed", provider=name, error=str(exc))

        # Last resort — local provider always works
        from ai.providers.local_provider import LocalProvider
        logger.warning("ai_gateway_all_providers_failed_using_local")
        return LocalProvider(), "local"

    async def _call_with_fallback(self, operation: str, *args, **kwargs) -> tuple[Any, str]:
        """Calls the given operation on providers in fallback order.

        Returns (result, provider_name_used).
        """
        chain = _PROVIDER_FALLBACK_CHAIN[:]
        preferred = self._config.default_provider
        if preferred in chain:
            chain.remove(preferred)
        chain.insert(0, preferred)

        last_exc: Exception | None = None
        for name in chain:
            try:
                p = create_provider(name)
                method = getattr(p, operation)
                result = await method(*args, **kwargs)
                if name != self._config.default_provider:
                    logger.info("ai_gateway_fallback_succeeded", provider=name, operation=operation)
                # Update cached provider if different from current
                if self._active_provider_name != name:
                    self._provider = p
                    self._active_provider_name = name
                return result, name
            except (AIProviderAuthError, AIProviderRateLimitError) as exc:
                logger.warning(
                    "ai_gateway_provider_failed_trying_fallback",
                    provider=name,
                    operation=operation,
                    error=str(exc),
                )
                last_exc = exc
                continue
            except Exception as exc:
                logger.warning(
                    "ai_gateway_provider_error",
                    provider=name,
                    operation=operation,
                    error=str(exc),
                )
                last_exc = exc
                continue

        # All providers failed — raise the last exception
        if last_exc:
            raise last_exc
        raise AIProviderError(context={"detail": "All providers in fallback chain failed"})

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> AIResponse:
        settings = get_ai_settings()
        request = AIRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model or self._config.default_model,
            temperature=temperature if temperature is not None else settings.temperature_default,
            max_tokens=max_tokens or settings.max_tokens_default,
        )
        result, _ = await self._call_with_fallback("generate", request)
        return result

    async def chat(
        self,
        messages: list[ChatMessage],
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        settings = get_ai_settings()
        request = ChatRequest(
            messages=messages,
            system_prompt=system_prompt,
            model=model or self._config.default_model,
            temperature=temperature if temperature is not None else settings.temperature_default,
            max_tokens=max_tokens or settings.max_tokens_default,
        )
        result, _ = await self._call_with_fallback("chat", request)
        return result

    async def summarize(
        self,
        text: str,
        max_words: int = 150,
        model: str | None = None,
    ) -> SummarizationResult:
        from ai.prompts.base_prompt import get_prompt_registry

        registry = get_prompt_registry()
        system_prompt = registry.get("summarization/system").render(max_words=max_words)
        user_prompt = registry.get("summarization/user").render(text=text)

        response = await self.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model=model,
        )
        original_length = len(text.split())
        summary_length = len(response.content.split())
        return SummarizationResult(
            summary=response.content,
            compression_ratio=round(summary_length / max(original_length, 1), 4) if original_length else None,
            original_length=original_length,
            summary_length=summary_length,
        )

    async def classify(
        self,
        text: str,
        model: str | None = None,
    ) -> ClassificationResult:
        import json

        from ai.prompts.base_prompt import get_prompt_registry

        registry = get_prompt_registry()
        system_prompt = registry.get("classification/system").render()
        user_prompt = registry.get("classification/user").render(text=text)

        response = await self.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            model=model,
        )
        try:
            data = json.loads(response.content)
            label = data.get("label", "unknown")
            confidence = float(data.get("confidence", 0.0))
            return ClassificationResult(label=label, confidence=confidence)
        except (json.JSONDecodeError, ValueError):
            return ClassificationResult(label=response.content.strip(), confidence=0.5)

    async def embed(
        self,
        input: str | list[str],
        model: str | None = None,
    ) -> EmbeddingResponse:
        request = EmbeddingRequest(input=input, model=model)
        result, _ = await self._call_with_fallback("embed", request)
        return result

    async def process(self, request: GatewayRequest) -> GatewayResponse:
        start = time.monotonic()
        try:
            op = request.operation
            payload = request.payload
            if op == "generate":
                result = await self.generate(
                    prompt=payload.get("prompt", ""),
                    system_prompt=payload.get("system_prompt"),
                    model=payload.get("model"),
                )
                data = {"content": result.content, "finish_reason": result.finish_reason}
                usage = {"prompt_tokens": result.usage.prompt_tokens, "completion_tokens": result.usage.completion_tokens} if result.usage else None
            elif op == "chat":
                messages = [ChatMessage(**m) for m in payload.get("messages", [])]
                result = await self.chat(
                    messages=messages,
                    system_prompt=payload.get("system_prompt"),
                    model=payload.get("model"),
                )
                data = {"message": {"role": result.message.role, "content": result.message.content}}
                usage = {"prompt_tokens": result.usage.prompt_tokens, "completion_tokens": result.usage.completion_tokens} if result.usage else None
            elif op == "summarize":
                result = await self.summarize(
                    text=payload.get("text", ""),
                    max_words=payload.get("max_words", 150),
                )
                data = {"summary": result.summary, "compression_ratio": result.compression_ratio}
                usage = None
            elif op == "classify":
                result = await self.classify(text=payload.get("text", ""))
                data = {"label": result.label, "confidence": result.confidence}
                usage = None
            elif op == "embed":
                result = await self.embed(input=payload.get("input", ""))
                data = {"dimensions": result.dimensions, "vector_count": len(result.vectors)}
                usage = None
            else:
                return GatewayResponse(
                    success=False,
                    error=f"Unknown operation: {op}",
                    latency_ms=(time.monotonic() - start) * 1000,
                )
            elapsed = (time.monotonic() - start) * 1000
            return GatewayResponse(success=True, data=data, latency_ms=elapsed, usage=usage)
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            logger.error("gateway_process_failed", operation=request.operation, error=str(exc))
            return GatewayResponse(success=False, error=str(exc), latency_ms=elapsed)

    async def stream(self, request: GatewayRequest) -> AsyncGenerator[str, None]:
        messages = [{"role": "user", "content": request.payload.get("prompt", "")}]
        async for token in self.provider.generate_stream(messages):
            yield token


_gateway: AIGateway | None = None


def get_ai_gateway() -> AIGateway:
    global _gateway
    if _gateway is None:
        _gateway = AIGateway()
    return _gateway


def reset_ai_gateway() -> None:
    global _gateway
    _gateway = None
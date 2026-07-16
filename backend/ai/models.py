"""AI Platform — reusable AI infrastructure models."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float | None = None
    latency_ms: float | None = None

    @classmethod
    def build(cls, prompt: int = 0, completion: int = 0, latency_ms: float | None = None) -> "TokenUsage":
        return cls(
            prompt_tokens=prompt,
            completion_tokens=completion,
            total_tokens=prompt + completion,
            latency_ms=latency_ms,
        )


@dataclass(frozen=True)
class AIRequest:
    prompt: str
    system_prompt: str | None = None
    model: str | None = None
    temperature: float = 0.0
    max_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AIResponse:
    content: str
    finish_reason: str | None = None
    model: str | None = None
    usage: TokenUsage | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str
    name: str | None = None


@dataclass(frozen=True)
class ChatRequest:
    messages: list[ChatMessage]
    system_prompt: str | None = None
    model: str | None = None
    temperature: float = 0.0
    max_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChatResponse:
    message: ChatMessage
    finish_reason: str | None = None
    model: str | None = None
    usage: TokenUsage | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EmbeddingRequest:
    input: str | list[str]
    model: str | None = None


@dataclass(frozen=True)
class EmbeddingResponse:
    vectors: list[list[float]]
    dimensions: int
    model: str | None = None
    usage: TokenUsage | None = None
    latency_ms: float | None = None


@dataclass(frozen=True)
class PromptContext:
    template_name: str
    template_version: str | None = None
    variables: dict[str, Any] = field(default_factory=dict)
    rendered_prompt: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ClassificationResult:
    label: str
    confidence: float
    labels: list[tuple[str, float]] = field(default_factory=list)


@dataclass(frozen=True)
class SummarizationResult:
    summary: str
    compression_ratio: float | None = None
    original_length: int = 0
    summary_length: int = 0
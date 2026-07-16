"""AI Platform — model unit tests."""

import uuid

import pytest

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


class TestTokenUsage:
    def test_build_creates_usage(self) -> None:
        usage = TokenUsage.build(prompt=10, completion=20, latency_ms=100.0)
        assert usage.prompt_tokens == 10
        assert usage.completion_tokens == 20
        assert usage.total_tokens == 30
        assert usage.latency_ms == 100.0

    def test_zero_tokens(self) -> None:
        usage = TokenUsage()
        assert usage.total_tokens == 0
        assert usage.estimated_cost is None


class TestAIRequest:
    def test_minimal_request(self) -> None:
        req = AIRequest(prompt="Hello")
        assert req.prompt == "Hello"
        assert req.system_prompt is None
        assert req.temperature == 0.0
        assert req.max_tokens is None

    def test_full_request(self) -> None:
        req = AIRequest(
            prompt="Test", system_prompt="Be helpful",
            model="gpt-4", temperature=0.5, max_tokens=100,
        )
        assert req.model == "gpt-4"
        assert req.temperature == 0.5
        assert req.max_tokens == 100


class TestAIResponse:
    def test_minimal_response(self) -> None:
        resp = AIResponse(content="Hello back")
        assert resp.content == "Hello back"
        assert resp.finish_reason is None
        assert resp.usage is None

    def test_full_response(self) -> None:
        usage = TokenUsage.build(prompt=5, completion=10)
        resp = AIResponse(content="Hi", finish_reason="stop", model="gpt-4", usage=usage)
        assert resp.finish_reason == "stop"
        assert resp.usage.total_tokens == 15


class TestChatMessage:
    def test_user_message(self) -> None:
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_assistant_message(self) -> None:
        msg = ChatMessage(role="assistant", content="Hi there", name="AI")
        assert msg.name == "AI"


class TestChatRequest:
    def test_messages_required(self) -> None:
        msgs = [ChatMessage(role="user", content="Hi")]
        req = ChatRequest(messages=msgs)
        assert len(req.messages) == 1
        assert req.messages[0].content == "Hi"


class TestEmbeddingRequest:
    def test_single_text(self) -> None:
        req = EmbeddingRequest(input="Hello")
        assert req.input == "Hello"
        assert req.model is None

    def test_batch_text(self) -> None:
        req = EmbeddingRequest(input=["Hello", "World"])
        assert len(req.input) == 2  # type: ignore[arg-type]


class TestEmbeddingResponse:
    def test_vectors(self) -> None:
        resp = EmbeddingResponse(vectors=[[0.1, 0.2], [0.3, 0.4]], dimensions=2)
        assert len(resp.vectors) == 2
        assert resp.dimensions == 2


class TestClassificationResult:
    def test_creation(self) -> None:
        result = ClassificationResult(label="billing", confidence=0.95)
        assert result.label == "billing"
        assert result.confidence == 0.95

    def test_with_labels(self) -> None:
        result = ClassificationResult(
            label="billing", confidence=0.95,
            labels=[("billing", 0.95), ("policy", 0.05)],
        )
        assert len(result.labels) == 2


class TestSummarizationResult:
    def test_creation(self) -> None:
        result = SummarizationResult(summary="Short summary", original_length=100, summary_length=10)
        assert result.summary == "Short summary"

    def test_no_original_length(self) -> None:
        result = SummarizationResult(summary="Test")
        assert result.compression_ratio is None


class TestPromptContext:
    def test_creation(self) -> None:
        ctx = PromptContext(
            template_name="test",
            template_version="v1.0.0",
            variables={"text": "hello"},
            rendered_prompt="Say hello",
        )
        assert ctx.template_name == "test"
        assert ctx.rendered_prompt == "Say hello"
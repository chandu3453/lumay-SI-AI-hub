"""AI Platform — exception hierarchy tests."""

import pytest

from ai.exceptions import (
    AIConfigurationError,
    AIEmbeddingError,
    AIError,
    AIModelNotFoundError,
    AIPromptError,
    AIPromptNotFoundError,
    AIProviderAuthError,
    AIProviderError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AITokenLimitError,
)


class TestAIExceptions:
    def test_ai_error_base(self) -> None:
        exc = AIError(message="Generic AI error")
        assert exc.status_code == 500
        assert exc.error_code == "AI_INTERNAL_ERROR"
        assert exc.message == "Generic AI error"

    def test_provider_error(self) -> None:
        exc = AIProviderError()
        assert exc.status_code == 502
        assert exc.error_code == "AI_PROVIDER_ERROR"

    def test_provider_timeout(self) -> None:
        exc = AIProviderTimeoutError()
        assert exc.status_code == 504
        assert exc.error_code == "AI_PROVIDER_TIMEOUT"

    def test_provider_rate_limit(self) -> None:
        exc = AIProviderRateLimitError()
        assert exc.status_code == 429
        assert exc.error_code == "AI_PROVIDER_RATE_LIMITED"

    def test_provider_auth(self) -> None:
        exc = AIProviderAuthError(context={"detail": "Invalid key"})
        assert exc.status_code == 401
        assert exc.context["detail"] == "Invalid key"

    def test_model_not_found(self) -> None:
        exc = AIModelNotFoundError()
        assert exc.status_code == 404

    def test_embedding_error(self) -> None:
        exc = AIEmbeddingError()
        assert exc.status_code == 500

    def test_prompt_error(self) -> None:
        exc = AIPromptError()
        assert exc.status_code == 422

    def test_prompt_not_found(self) -> None:
        exc = AIPromptNotFoundError()
        assert exc.status_code == 404

    def test_configuration_error(self) -> None:
        exc = AIConfigurationError()
        assert exc.status_code == 500
        assert exc.error_code == "AI_CONFIGURATION_ERROR"

    def test_token_limit_error(self) -> None:
        exc = AITokenLimitError()
        assert exc.status_code == 422

    def test_exception_chaining(self) -> None:
        inner = ValueError("inner")
        outer = AIProviderError(message="Provider failed", context={"detail": str(inner)})
        assert "inner" in outer.context["detail"]

    def test_all_exceptions_are_ai_error_subclasses(self) -> None:
        exceptions = [
            AIProviderError(),
            AIProviderTimeoutError(),
            AIProviderRateLimitError(),
            AIProviderAuthError(),
            AIModelNotFoundError(),
            AIEmbeddingError(),
            AIPromptError(),
            AIPromptNotFoundError(),
            AIConfigurationError(),
            AITokenLimitError(),
        ]
        for exc in exceptions:
            assert isinstance(exc, AIError)
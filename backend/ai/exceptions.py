"""AI Platform — exception hierarchy."""

from http import HTTPStatus

from shared.base_exception import AppException


class AIError(AppException):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code = "AI_INTERNAL_ERROR"
    message = "An unexpected AI platform error occurred."


class AIProviderError(AIError):
    status_code = HTTPStatus.BAD_GATEWAY
    error_code = "AI_PROVIDER_ERROR"
    message = "AI provider returned an error."


class AIProviderTimeoutError(AIProviderError):
    status_code = HTTPStatus.GATEWAY_TIMEOUT
    error_code = "AI_PROVIDER_TIMEOUT"
    message = "AI provider request timed out."


class AIProviderRateLimitError(AIProviderError):
    status_code = HTTPStatus.TOO_MANY_REQUESTS
    error_code = "AI_PROVIDER_RATE_LIMITED"
    message = "AI provider rate limit exceeded."


class AIProviderAuthError(AIProviderError):
    status_code = HTTPStatus.UNAUTHORIZED
    error_code = "AI_PROVIDER_AUTH_ERROR"
    message = "AI provider authentication failed."


class AIModelNotFoundError(AIError):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "AI_MODEL_NOT_FOUND"
    message = "Requested AI model is not available."


class AIEmbeddingError(AIError):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code = "AI_EMBEDDING_ERROR"
    message = "Embedding generation failed."


class AIPromptError(AIError):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "AI_PROMPT_ERROR"
    message = "Prompt rendering or validation failed."


class AIPromptNotFoundError(AIPromptError):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "AI_PROMPT_NOT_FOUND"
    message = "Prompt template not found in registry."


class AIConfigurationError(AIError):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code = "AI_CONFIGURATION_ERROR"
    message = "AI platform is not properly configured."


class AITokenLimitError(AIError):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "AI_TOKEN_LIMIT_ERROR"
    message = "Token limit exceeded for the requested operation."
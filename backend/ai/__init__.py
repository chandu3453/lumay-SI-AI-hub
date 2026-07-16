"""AI Platform — isolated intelligence layer.

Architecture:
  gateway/        — AI Gateway (single entry point for all AI capabilities)
  orchestrator/   — LangGraph-based workflow orchestration (agentic workflows)
  guardrails/     — PII redaction, content safety, output validation
  providers/      — LLM provider adapters behind a common interface
  prompts/        — Versioned prompt template management
  retrieval/      — RAG document retrieval and reranking
  embeddings/     — Text encoding, vector storage, and similarity search
  evaluation/     — Response quality metrics and safety scoring
  pipelines/      — Domain-specific AI pipelines (complaint, sentiment, etc.)
  memory/         — Multi-turn conversation memory and summarisation

Rules:
  - The AI layer is isolated from business domains.
  - All domain code consumes AI capabilities exclusively through the gateway.
  - No domain import is allowed inside any AI sub-package.
"""

from ai.config import get_ai_settings
from app.config.settings import AIPricingSettings, AISettings
from ai.exceptions import (
    AIError,
    AIProviderError,
    AIProviderTimeoutError,
    AIProviderRateLimitError,
    AIProviderAuthError,
    AIModelNotFoundError,
    AIEmbeddingError,
    AIPromptError,
    AIPromptNotFoundError,
    AIConfigurationError,
    AITokenLimitError,
)
from ai.gateway import AIGateway, AIGatewayConfig, get_ai_gateway
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
from ai.prompts import (
    BasePrompt,
    PromptRegistry,
    PromptVersion,
    get_prompt_registry,
    register_default_prompts,
)
from ai.providers import BaseLLMProvider, create_provider
from ai.token_usage import TokenTracker

__all__ = [
    "AIConfigurationError",
    "AIEmbeddingError",
    "AIError",
    "AIGateway",
    "AIGatewayConfig",
    "AIModelNotFoundError",
    "AIPricingSettings",
    "AIPromptError",
    "AIPromptNotFoundError",
    "AIProviderAuthError",
    "AIProviderError",
    "AIProviderRateLimitError",
    "AIProviderTimeoutError",
    "AIRequest",
    "AIResponse",
    "AISettings",
    "AITokenLimitError",
    "BaseLLMProvider",
    "BasePrompt",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ClassificationResult",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "PromptContext",
    "PromptRegistry",
    "PromptVersion",
    "SummarizationResult",
    "TokenTracker",
    "TokenUsage",
    "create_provider",
    "get_ai_gateway",
    "get_ai_settings",
    "get_prompt_registry",
    "register_default_prompts",
]
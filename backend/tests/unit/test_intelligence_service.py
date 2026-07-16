"""Complaint Intelligence — service unit tests."""

import pytest

from ai.gateway.ai_gateway import AIGateway, AIGatewayConfig
from ai.intelligence.service import ComplaintIntelligenceService, DUPLICATE_SIMILARITY_THRESHOLD
from ai.intelligence.prompts import register_complaint_prompts
from ai.embeddings.encoder import TextEncoder
from ai.providers.local_provider import LocalProvider
from ai.prompts.base_prompt import get_prompt_registry, reset_prompt_registry
from ai.prompts.templates import register_default_prompts


@pytest.fixture(autouse=True)
def _setup_prompts():
    reset_prompt_registry()
    register_default_prompts()
    register_complaint_prompts()
    yield
    reset_prompt_registry()


@pytest.fixture
def local_gateway() -> AIGateway:
    return AIGateway(config=AIGatewayConfig(default_provider="local", default_model="local-dev"))


@pytest.fixture
def local_encoder() -> TextEncoder:
    return TextEncoder(provider=LocalProvider())


@pytest.fixture
def service(local_gateway: AIGateway) -> ComplaintIntelligenceService:
    return ComplaintIntelligenceService(gateway=local_gateway)


@pytest.fixture
def service_with_encoder(local_gateway: AIGateway, local_encoder: TextEncoder) -> ComplaintIntelligenceService:
    return ComplaintIntelligenceService(gateway=local_gateway, encoder=local_encoder)


COMPLAINT_BILLING = "I was overcharged on my insurance premium by $50. My policy number is POL-12345."
COMPLAINT_CLAIMS = "My claim was denied without proper explanation. Claim ID CLM-67890."
COMPLAINT_SERVICE = "The customer service agent was rude and unhelpful."


@pytest.mark.asyncio
class TestComplaintIntelligenceService:
    async def test_classify_returns_result(self, service: ComplaintIntelligenceService) -> None:
        result = await service.classify(COMPLAINT_BILLING)
        assert isinstance(result.category, str)
        assert result.confidence >= 0.0
        assert result.metadata is not None

    async def test_analyze_sentiment_returns_result(self, service: ComplaintIntelligenceService) -> None:
        result = await service.analyze_sentiment(COMPLAINT_BILLING)
        assert isinstance(result.sentiment, str)
        assert -1.0 <= result.polarity <= 1.0

    async def test_assess_severity_returns_result(self, service: ComplaintIntelligenceService) -> None:
        result = await service.assess_severity(COMPLAINT_BILLING)
        assert isinstance(result.severity, str)
        assert 0.0 <= result.severity_score <= 1.0

    async def test_extract_themes_returns_result(self, service: ComplaintIntelligenceService) -> None:
        result = await service.extract_themes(COMPLAINT_BILLING)
        assert isinstance(result.primary_theme, str)
        assert isinstance(result.keywords, list)

    async def test_recommend_priority_returns_result(self, service: ComplaintIntelligenceService) -> None:
        result = await service.recommend_priority(COMPLAINT_BILLING)
        assert isinstance(result.priority, str)
        assert 0.0 <= result.priority_score <= 1.0

    async def test_summarize_returns_result(self, service: ComplaintIntelligenceService) -> None:
        result = await service.summarize(COMPLAINT_BILLING, max_words=50)
        assert isinstance(result.summary, str)
        assert isinstance(result.key_points, list)

    async def test_recommend_resolution_returns_result(self, service: ComplaintIntelligenceService) -> None:
        result = await service.recommend_resolution(COMPLAINT_BILLING)
        assert isinstance(result.recommended_action, str)
        assert isinstance(result.steps, list)

    async def test_detect_duplicate_with_encoder(self, service_with_encoder: ComplaintIntelligenceService) -> None:
        result = await service_with_encoder.detect_duplicate(
            COMPLAINT_BILLING,
            COMPLAINT_BILLING,
        )
        assert result.is_duplicate is True
        assert result.similarity_score >= DUPLICATE_SIMILARITY_THRESHOLD

    async def test_detect_duplicate_different_texts(self, service_with_encoder: ComplaintIntelligenceService) -> None:
        result = await service_with_encoder.detect_duplicate(
            COMPLAINT_BILLING,
            COMPLAINT_CLAIMS,
        )
        assert isinstance(result.is_duplicate, bool)
        assert 0.0 <= result.similarity_score <= 1.0

    async def test_detect_duplicate_fallback_to_llm(self, service: ComplaintIntelligenceService) -> None:
        result = await service.detect_duplicate(
            COMPLAINT_BILLING,
            COMPLAINT_CLAIMS,
        )
        assert isinstance(result.is_duplicate, bool)
        assert 0.0 <= result.similarity_score <= 1.0

    async def test_analyze_complete_returns_all_analyses(self, service: ComplaintIntelligenceService) -> None:
        result = await service.analyze_complete(COMPLAINT_BILLING)
        assert result.classification is not None
        assert result.sentiment is not None
        assert result.severity is not None
        assert result.themes is not None
        assert result.priority is not None
        assert result.summary is not None
        assert result.resolution is not None
        assert result.metadata is not None

    async def test_all_methods_with_empty_text(self, service: ComplaintIntelligenceService) -> None:
        result = await service.classify("")
        assert isinstance(result.category, str)

        result = await service.analyze_sentiment("")
        assert isinstance(result.sentiment, str)

        result = await service.summarize("")
        assert isinstance(result.summary, str)

        result = await service.recommend_resolution("")
        assert isinstance(result.recommended_action, str)
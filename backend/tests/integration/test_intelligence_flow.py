"""Complaint Intelligence — integration tests with full pipeline."""

import pytest

from ai.gateway.ai_gateway import AIGateway, AIGatewayConfig
from ai.intelligence.prompts import register_complaint_prompts
from ai.intelligence.service import ComplaintIntelligenceService
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
def gateway() -> AIGateway:
    return AIGateway(config=AIGatewayConfig(default_provider="local", default_model="local-dev"))


@pytest.fixture
def service(gateway: AIGateway) -> ComplaintIntelligenceService:
    return ComplaintIntelligenceService(gateway=gateway)


@pytest.mark.asyncio
class TestIntelligenceIntegration:
    COMPLAINT_TEXT = "I was overcharged on my insurance premium by $50. Policy number POL-12345."

    async def test_classify_pipeline(self, service: ComplaintIntelligenceService) -> None:
        result = await service.classify(self.COMPLAINT_TEXT)
        assert result.category is not None
        assert result.metadata.model_used == "local-dev"
        assert result.metadata.processing_time_ms > 0
        assert "complaint/classification/system" in result.metadata.prompt_name

    async def test_prompt_registry_has_complaint_prompts(self) -> None:
        registry = get_prompt_registry()
        prompts = registry.list()
        names = [p["name"] for p in prompts]
        assert "complaint/classification/system" in names
        assert "complaint/sentiment/system" in names
        assert "complaint/severity/system" in names
        assert "complaint/theme/system" in names
        assert "complaint/priority/system" in names
        assert "complaint/summary/system" in names
        assert "complaint/resolution/system" in names
        assert "complaint/duplicate/system" in names

    async def test_complaint_prompts_have_tags(self) -> None:
        registry = get_prompt_registry()
        tagged = registry.get_by_tag("complaint")
        assert len(tagged) > 0
        tagged = registry.get_by_tag("classification")
        assert len(tagged) > 0

    async def test_sentiment_metadata_contains_usage(self, service: ComplaintIntelligenceService) -> None:
        result = await service.analyze_sentiment(self.COMPLAINT_TEXT)
        metadata = result.metadata
        assert metadata.token_usage is not None
        assert metadata.processing_time_ms > 0

    async def test_summary_word_count(self, service: ComplaintIntelligenceService) -> None:
        long_text = " ".join(["complaint word"] * 100)
        result = await service.summarize(long_text, max_words=30)
        assert result.metadata.processing_time_ms > 0

    async def test_complete_analysis_returns_metadata(self, service: ComplaintIntelligenceService) -> None:
        result = await service.analyze_complete(self.COMPLAINT_TEXT)
        assert result.metadata.processing_time_ms > 0
        assert "complaint/analysis/complete" in result.metadata.prompt_name

    async def test_duplicate_detection_threshold(self, service: ComplaintIntelligenceService) -> None:
        from ai.intelligence.service import DUPLICATE_SIMILARITY_THRESHOLD
        assert DUPLICATE_SIMILARITY_THRESHOLD == 0.85
"""Complaint Intelligence — output model unit tests."""

from ai.intelligence.models import (
    AnalysisMetadata,
    ComplaintAnalysis,
    ComplaintClassification,
    ComplaintSummary,
    DuplicateComplaintResult,
    PriorityRecommendation,
    ResolutionRecommendation,
    SentimentAnalysis,
    SeverityPrediction,
    ThemeAnalysis,
)


class TestAnalysisMetadata:
    def test_defaults(self) -> None:
        m = AnalysisMetadata()
        assert m.model_used == ""
        assert m.processing_time_ms == 0.0
        assert m.token_usage == {}
        assert m.explanation == ""

    def test_custom(self) -> None:
        m = AnalysisMetadata(
            model_used="gpt-4o",
            processing_time_ms=150.5,
            token_usage={"prompt_tokens": 100, "completion_tokens": 50},
            prompt_name="complaint/classification/system",
            explanation="Test analysis",
        )
        assert m.model_used == "gpt-4o"
        assert m.processing_time_ms == 150.5
        assert m.token_usage["prompt_tokens"] == 100


class TestComplaintClassification:
    def test_defaults(self) -> None:
        c = ComplaintClassification()
        assert c.category == ""
        assert c.confidence == 0.0

    def test_full(self) -> None:
        c = ComplaintClassification(
            category="billing",
            subcategory="overcharge",
            issue_type="incorrect_amount",
            confidence=0.95,
        )
        assert c.category == "billing"
        assert c.confidence == 0.95


class TestSentimentAnalysis:
    def test_defaults(self) -> None:
        s = SentimentAnalysis()
        assert s.sentiment == ""
        assert s.polarity == 0.0

    def test_with_emotions(self) -> None:
        s = SentimentAnalysis(
            sentiment="negative",
            polarity=-0.8,
            emotions={"anger": 0.9, "frustration": 0.7},
            intensity=0.85,
            confidence=0.92,
        )
        assert s.sentiment == "negative"
        assert s.polarity == -0.8
        assert s.emotions["anger"] == 0.9
        assert s.intensity == 0.85


class TestThemeAnalysis:
    def test_defaults(self) -> None:
        t = ThemeAnalysis()
        assert t.primary_theme == ""
        assert t.secondary_themes == []

    def test_with_themes(self) -> None:
        t = ThemeAnalysis(
            primary_theme="billing dispute",
            secondary_themes=["late fee", "customer service"],
            keywords=["overcharge", "bill", "error"],
            confidence=0.88,
        )
        assert t.primary_theme == "billing dispute"
        assert len(t.keywords) == 3


class TestSeverityPrediction:
    def test_defaults(self) -> None:
        s = SeverityPrediction()
        assert s.severity == ""
        assert s.severity_score == 0.0

    def test_critical(self) -> None:
        s = SeverityPrediction(
            severity="critical",
            severity_score=0.95,
            urgency="immediate",
            impact="regulatory_risk",
            confidence=0.90,
        )
        assert s.severity == "critical"
        assert s.urgency == "immediate"


class TestPriorityRecommendation:
    def test_defaults(self) -> None:
        p = PriorityRecommendation()
        assert p.priority == ""
        assert p.priority_score == 0.0

    def test_high(self) -> None:
        p = PriorityRecommendation(
            priority="high",
            priority_score=0.85,
            sla_risk="at_risk",
            rationale="Financial impact on customer",
            confidence=0.87,
        )
        assert p.priority == "high"
        assert "Financial" in p.rationale


class TestComplaintSummary:
    def test_defaults(self) -> None:
        s = ComplaintSummary()
        assert s.summary == ""
        assert s.key_points == []

    def test_with_entities(self) -> None:
        s = ComplaintSummary(
            summary="Customer reported billing error.",
            key_points=["Overcharged by $50", "Requested refund"],
            mentioned_entities={"policy_numbers": ["POL-123"], "amounts": ["$50"]},
            word_count=5,
        )
        assert "billing" in s.summary
        assert "POL-123" in s.mentioned_entities["policy_numbers"]


class TestDuplicateComplaintResult:
    def test_defaults(self) -> None:
        d = DuplicateComplaintResult()
        assert d.is_duplicate is False
        assert d.similarity_score == 0.0
        assert d.matched_complaint_id == ""

    def test_duplicate_found(self) -> None:
        d = DuplicateComplaintResult(
            is_duplicate=True,
            matched_complaint_id="comp-456",
            similarity_score=0.92,
            threshold=0.85,
            match_reason="Same policy and issue",
            confidence=0.90,
        )
        assert d.is_duplicate is True
        assert d.matched_complaint_id == "comp-456"


class TestResolutionRecommendation:
    def test_defaults(self) -> None:
        r = ResolutionRecommendation()
        assert r.recommended_action == ""
        assert r.steps == []

    def test_full(self) -> None:
        r = ResolutionRecommendation(
            recommended_action="Issue refund",
            steps=["Verify charge", "Process refund", "Notify customer"],
            department="billing",
            escalation_required=False,
            estimated_resolution_time="2-3 business days",
            confidence=0.85,
        )
        assert r.department == "billing"
        assert len(r.steps) == 3
        assert r.escalation_required is False


class TestComplaintAnalysis:
    def test_defaults(self) -> None:
        a = ComplaintAnalysis()
        assert isinstance(a.classification, ComplaintClassification)
        assert isinstance(a.sentiment, SentimentAnalysis)
        assert isinstance(a.themes, ThemeAnalysis)
        assert isinstance(a.severity, SeverityPrediction)
        assert isinstance(a.priority, PriorityRecommendation)
        assert isinstance(a.summary, ComplaintSummary)
        assert isinstance(a.duplicate, DuplicateComplaintResult)
        assert isinstance(a.resolution, ResolutionRecommendation)

    def test_full_analysis(self) -> None:
        analysis = ComplaintAnalysis(
            classification=ComplaintClassification(category="billing", confidence=0.95),
            sentiment=SentimentAnalysis(sentiment="negative", polarity=-0.7),
            severity=SeverityPrediction(severity="high", severity_score=0.8),
            priority=PriorityRecommendation(priority="high", priority_score=0.85),
        )
        assert analysis.classification.category == "billing"
        assert analysis.sentiment.polarity == -0.7
        assert analysis.severity.severity == "high"
        assert analysis.priority.priority == "high"
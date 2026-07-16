"""Complaint Intelligence Service — AI-powered complaint analysis (Phase 2).

All methods consume the AI Gateway, Prompt Registry, and Embedding Service
from the existing AI Core Platform. No provider is called directly.

Phase 2 additions (FR-002 to FR-020):
- detect_complaint()      : FR-002 complaint detection
- analyze_sentiment()     : FR-003 enhanced with segment trend + target
- extract_themes()        : FR-004 7-bucket taxonomy
- assess_severity()       : FR-005 trigger rules
- assess_escalation_risk(): FR-006 escalation risk score 0-100
- recommend_priority()    : FR-007 SLA breach probability
- analyze_root_cause()    : FR-016 root cause analysis
- detect_language()       : FR-019 bilingual AR/EN support
- analyze_complete()      : Full pipeline (all FR)
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from ai.embeddings.encoder import TextEncoder
from ai.gateway.ai_gateway import AIGateway, get_ai_gateway
from ai.intelligence.models import (
    AnalysisMetadata,
    ComplaintAnalysis,
    ComplaintClassification,
    ComplaintDetection,
    ComplaintSummary,
    DuplicateComplaintResult,
    EscalationRiskAssessment,
    LanguageDetection,
    PriorityRecommendation,
    ResolutionRecommendation,
    RootCauseAnalysis,
    SentimentAnalysis,
    SeverityPrediction,
    ThemeAnalysis,
)
from ai.intelligence.pipeline import (
    build_metadata,
    parse_json_response,
    preprocess,
    run_pipeline,
    validate_confidence,
)
from app.platform.logging import get_logger

logger = get_logger(__name__)

DUPLICATE_SIMILARITY_THRESHOLD = 0.85


class ComplaintIntelligenceService:
    def __init__(
        self,
        gateway: AIGateway | None = None,
        encoder: TextEncoder | None = None,
    ) -> None:
        self._gateway = gateway or get_ai_gateway()
        self._encoder = encoder

    # -----------------------------------------------------------------------
    # Backward Compatibility — Classify
    # -----------------------------------------------------------------------
    async def classify(
        self, complaint_text: str, model: str | None = None
    ) -> ComplaintClassification:
        text = preprocess(complaint_text)
        parsed, metadata = await run_pipeline(
            self._gateway,
            "complaint/classification/system",
            "complaint/classification/user",
            {"complaint_text": text},
        )
        if parsed:
            return ComplaintClassification(
                category=parsed.get("category", "general"),
                subcategory=parsed.get("subcategory", ""),
                issue_type=parsed.get("issue_type", ""),
                confidence=validate_confidence(parsed),
                explanation=parsed.get("explanation", ""),
                evidence=parsed.get("evidence", []),
                metadata=metadata,
            )
        return ComplaintClassification(metadata=metadata)

    # -----------------------------------------------------------------------
    # FR-002 — Complaint Detection
    # -----------------------------------------------------------------------
    async def detect_complaint(
        self, interaction_text: str, model: str | None = None
    ) -> ComplaintDetection:
        text = preprocess(interaction_text)
        parsed, metadata = await run_pipeline(
            self._gateway,
            "complaint/detection/system",
            "complaint/detection/user",
            {"interaction_text": text},
        )
        if parsed:
            return ComplaintDetection(
                is_complaint=bool(parsed.get("is_complaint", False)),
                detection_type=parsed.get("detection_type", "none"),
                confidence=validate_confidence(parsed),
                primary_complaint_statement=parsed.get("primary_complaint_statement", ""),
                excerpt=parsed.get("excerpt", ""),
                detected_language=parsed.get("detected_language", "en"),
                explanation=parsed.get("explanation", ""),
                evidence=parsed.get("evidence", []),
                metadata=metadata,
            )
        return ComplaintDetection(metadata=metadata)

    # -----------------------------------------------------------------------
    # FR-003 — Enhanced Sentiment Analysis
    # -----------------------------------------------------------------------
    async def analyze_sentiment(
        self, complaint_text: str, model: str | None = None
    ) -> SentimentAnalysis:
        text = preprocess(complaint_text)
        parsed, metadata = await run_pipeline(
            self._gateway,
            "complaint/sentiment/system",
            "complaint/sentiment/user",
            {"complaint_text": text},
        )
        if parsed:
            return SentimentAnalysis(
                sentiment=parsed.get("sentiment", "neutral"),
                sentiment_start=parsed.get("sentiment_start", ""),
                sentiment_end=parsed.get("sentiment_end", ""),
                sentiment_trend=parsed.get("sentiment_trend", "stable"),
                polarity=float(parsed.get("polarity", 0.0)),
                emotions=parsed.get("emotions", {}),
                intensity=float(parsed.get("intensity", 0.0)),
                sentiment_target=parsed.get("sentiment_target", "general"),
                confidence=validate_confidence(parsed),
                explanation=parsed.get("explanation", ""),
                evidence=parsed.get("evidence", []),
                metadata=metadata,
            )
        return SentimentAnalysis(metadata=metadata)

    # -----------------------------------------------------------------------
    # FR-004 — Theme Extraction (7-bucket LuMay taxonomy)
    # -----------------------------------------------------------------------
    async def extract_themes(
        self, complaint_text: str, model: str | None = None
    ) -> ThemeAnalysis:
        text = preprocess(complaint_text)
        parsed, metadata = await run_pipeline(
            self._gateway,
            "complaint/theme/system",
            "complaint/theme/user",
            {"complaint_text": text},
        )
        if parsed:
            return ThemeAnalysis(
                primary_theme=parsed.get("primary_theme", ""),
                secondary_themes=parsed.get("secondary_themes", []),
                subcategory=parsed.get("subcategory", ""),
                keywords=parsed.get("keywords", []),
                confidence=validate_confidence(parsed),
                explanation=parsed.get("explanation", ""),
                evidence=parsed.get("evidence", []),
                metadata=metadata,
            )
        return ThemeAnalysis(metadata=metadata)

    # -----------------------------------------------------------------------
    # FR-005 — Severity Assessment (trigger rules)
    # -----------------------------------------------------------------------
    async def assess_severity(
        self, complaint_text: str, model: str | None = None
    ) -> SeverityPrediction:
        text = preprocess(complaint_text)
        parsed, metadata = await run_pipeline(
            self._gateway,
            "complaint/severity/system",
            "complaint/severity/user",
            {"complaint_text": text},
        )
        if parsed:
            return SeverityPrediction(
                severity=parsed.get("severity", "medium"),
                severity_score=float(parsed.get("severity_score", 0.5)),
                urgency=parsed.get("urgency", "moderate"),
                impact=parsed.get("impact", "minor"),
                auto_escalation_triggers=parsed.get("auto_escalation_triggers", []),
                confidence=validate_confidence(parsed),
                explanation=parsed.get("explanation", ""),
                evidence=parsed.get("evidence", []),
                metadata=metadata,
            )
        return SeverityPrediction(metadata=metadata)

    # -----------------------------------------------------------------------
    # FR-006 — Escalation Risk Score (0-100)
    # -----------------------------------------------------------------------
    async def assess_escalation_risk(
        self, complaint_text: str, model: str | None = None
    ) -> EscalationRiskAssessment:
        text = preprocess(complaint_text)
        parsed, metadata = await run_pipeline(
            self._gateway,
            "complaint/escalation/system",
            "complaint/escalation/user",
            {"complaint_text": text},
        )
        if parsed:
            return EscalationRiskAssessment(
                escalation_risk_score=int(parsed.get("escalation_risk_score", 0)),
                risk_level=parsed.get("risk_level", "low"),
                triggers=parsed.get("triggers", []),
                confidence=validate_confidence(parsed),
                explanation=parsed.get("explanation", ""),
                evidence=parsed.get("evidence", []),
                metadata=metadata,
            )
        return EscalationRiskAssessment(metadata=metadata)

    # -----------------------------------------------------------------------
    # FR-007 — Priority + SLA Breach Prediction
    # -----------------------------------------------------------------------
    async def recommend_priority(
        self, complaint_text: str, model: str | None = None
    ) -> PriorityRecommendation:
        text = preprocess(complaint_text)
        parsed, metadata = await run_pipeline(
            self._gateway,
            "complaint/priority/system",
            "complaint/priority/user",
            {"complaint_text": text},
        )
        if parsed:
            return PriorityRecommendation(
                priority=parsed.get("priority", "medium"),
                priority_score=float(parsed.get("priority_score", 0.5)),
                sla_risk=parsed.get("sla_risk", "within_sla"),
                breach_probability=int(parsed.get("breach_probability", 0)),
                sla_hours_remaining=parsed.get("sla_hours_remaining"),
                estimated_breach_time=parsed.get("estimated_breach_time"),
                rationale=parsed.get("rationale", ""),
                confidence=validate_confidence(parsed),
                explanation=parsed.get("explanation", ""),
                evidence=parsed.get("evidence", []),
                metadata=metadata,
            )
        return PriorityRecommendation(metadata=metadata)

    # -----------------------------------------------------------------------
    # FR-011 — Complaint Summary (bilingual)
    # -----------------------------------------------------------------------
    async def summarize(
        self,
        complaint_text: str,
        max_words: int = 150,
        model: str | None = None,
    ) -> ComplaintSummary:
        text = preprocess(complaint_text)
        parsed, metadata = await run_pipeline(
            self._gateway,
            "complaint/summary/system",
            "complaint/summary/user",
            {"complaint_text": text, "max_words": max_words},
        )
        if parsed:
            summary_text = parsed.get("summary", "")
            return ComplaintSummary(
                summary=summary_text,
                key_points=parsed.get("key_points", []),
                mentioned_entities=parsed.get("mentioned_entities", {}),
                detected_language=parsed.get("detected_language", "en"),
                word_count=len(summary_text.split()),
                metadata=metadata,
            )
        return ComplaintSummary(metadata=metadata)

    # -----------------------------------------------------------------------
    # FR-016 — Root Cause Analysis
    # -----------------------------------------------------------------------
    async def analyze_root_cause(
        self, complaint_text: str, model: str | None = None
    ) -> RootCauseAnalysis:
        text = preprocess(complaint_text)
        parsed, metadata = await run_pipeline(
            self._gateway,
            "complaint/root_cause/system",
            "complaint/root_cause/user",
            {"complaint_text": text},
        )
        if parsed:
            return RootCauseAnalysis(
                root_cause=parsed.get("root_cause", ""),
                root_cause_category=parsed.get("root_cause_category", ""),
                contributing_factors=parsed.get("contributing_factors", []),
                process_failure_point=parsed.get("process_failure_point", ""),
                recommended_fix=parsed.get("recommended_fix", ""),
                prevention_suggestion=parsed.get("prevention_suggestion", ""),
                confidence=validate_confidence(parsed),
                explanation=parsed.get("explanation", ""),
                evidence=parsed.get("evidence", []),
                metadata=metadata,
            )
        return RootCauseAnalysis(metadata=metadata)

    # -----------------------------------------------------------------------
    # FR-019 — Language Detection
    # -----------------------------------------------------------------------
    async def detect_language(
        self, text: str, model: str | None = None
    ) -> LanguageDetection:
        parsed, metadata = await run_pipeline(
            self._gateway,
            "complaint/language/system",
            "complaint/language/user",
            {"text": text},
        )
        if parsed:
            return LanguageDetection(
                detected_language=parsed.get("detected_language", "en"),
                language_confidence=float(parsed.get("language_confidence", 0.0)),
                arabic_percentage=int(parsed.get("arabic_percentage", 0)),
                english_percentage=int(parsed.get("english_percentage", 100)),
                contains_arabic_insurance_terms=bool(
                    parsed.get("contains_arabic_insurance_terms", False)
                ),
                script=parsed.get("script", "latin"),
                metadata=metadata,
            )
        return LanguageDetection(metadata=metadata)

    # -----------------------------------------------------------------------
    # FR-011 — Resolution / Next Best Action
    # -----------------------------------------------------------------------
    async def recommend_resolution(
        self, complaint_text: str, model: str | None = None
    ) -> ResolutionRecommendation:
        text = preprocess(complaint_text)
        parsed, metadata = await run_pipeline(
            self._gateway,
            "complaint/resolution/system",
            "complaint/resolution/user",
            {"complaint_text": text},
        )
        if parsed:
            return ResolutionRecommendation(
                recommended_action=parsed.get("recommended_action", ""),
                steps=parsed.get("steps", []),
                department=parsed.get("department", ""),
                routing_rule=parsed.get("routing_rule", ""),
                escalation_required=bool(parsed.get("escalation_required", False)),
                estimated_resolution_time=parsed.get("estimated_resolution_time", ""),
                suggested_response_template=parsed.get("suggested_response_template", ""),
                confidence=validate_confidence(parsed),
                explanation=parsed.get("explanation", ""),
                evidence=parsed.get("evidence", []),
                metadata=metadata,
            )
        return ResolutionRecommendation(metadata=metadata)

    # -----------------------------------------------------------------------
    # Duplicate Detection (unchanged)
    # -----------------------------------------------------------------------
    async def detect_duplicate(
        self,
        complaint_a: str,
        complaint_b: str,
        threshold: float = DUPLICATE_SIMILARITY_THRESHOLD,
        model: str | None = None,
    ) -> DuplicateComplaintResult:
        if self._encoder:
            vector_a = await self._encoder.encode(complaint_a)
            vector_b = await self._encoder.encode(complaint_b)
            semantic_score = await self._encoder.similarity(vector_a, vector_b)
            if semantic_score >= threshold:
                return DuplicateComplaintResult(
                    is_duplicate=True,
                    similarity_score=round(semantic_score, 4),
                    threshold=threshold,
                    match_reason=f"Semantic similarity ({semantic_score:.2f}) exceeds threshold ({threshold})",
                    confidence=min(semantic_score, 1.0),
                    metadata=build_metadata("", 0.0, {}, "complaint/duplicate/embedding"),
                )

        text_a = preprocess(complaint_a)
        text_b = preprocess(complaint_b)
        parsed, metadata = await run_pipeline(
            self._gateway,
            "complaint/duplicate/system",
            "complaint/duplicate/user",
            {"complaint_a": text_a, "complaint_b": text_b},
        )
        if parsed:
            return DuplicateComplaintResult(
                is_duplicate=bool(parsed.get("is_duplicate", False)),
                similarity_score=float(parsed.get("similarity_score", 0.0)),
                threshold=threshold,
                match_reason=parsed.get("match_reason", ""),
                confidence=validate_confidence(parsed),
                metadata=metadata,
            )
        return DuplicateComplaintResult(threshold=threshold, metadata=metadata)

    # -----------------------------------------------------------------------
    # FR-002 to FR-020 — Full Analysis Pipeline
    # -----------------------------------------------------------------------
    async def analyze_complete(
        self, complaint_text: str, model: str | None = None
    ) -> ComplaintAnalysis:
        """Run all Phase 2 analysis pipelines concurrently and return combined result."""
        start = time.monotonic()
        text = preprocess(complaint_text)

        # Run all analyses concurrently for performance
        (
            detection,
            sentiment,
            themes,
            severity,
            escalation,
            priority,
            summary,
            root_cause,
            resolution,
            language,
        ) = await asyncio.gather(
            self.detect_complaint(text),
            self.analyze_sentiment(text),
            self.extract_themes(text),
            self.assess_severity(text),
            self.assess_escalation_risk(text),
            self.recommend_priority(text),
            self.summarize(text),
            self.analyze_root_cause(text),
            self.recommend_resolution(text),
            self.detect_language(text),
        )

        elapsed = (time.monotonic() - start) * 1000
        total_metadata = build_metadata(
            model_used=model or "",
            processing_time_ms=elapsed,
            token_usage={},
            prompt_name="complaint/analysis/complete",
            explanation="Full Phase 2 complaint analysis pipeline",
        )

        logger.info(
            "complaint_analysis_complete",
            processing_time_ms=round(elapsed, 1),
            is_complaint=detection.is_complaint,
            severity=severity.severity,
            escalation_risk=escalation.escalation_risk_score,
            sla_risk=priority.sla_risk,
            language=language.detected_language,
        )

        return ComplaintAnalysis(
            detection=detection,
            sentiment=sentiment,
            themes=themes,
            severity=severity,
            escalation=escalation,
            priority=priority,
            summary=summary,
            root_cause=root_cause,
            resolution=resolution,
            language=language,
            metadata=total_metadata,
        )
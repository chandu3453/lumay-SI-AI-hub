"""Complaint Intelligence output models — Phase 2.

All dataclasses are frozen (immutable) and returned by ComplaintIntelligenceService.
Phase 2 additions:
- ComplaintDetection      : FR-002
- SentimentAnalysis       : FR-003 (segment trend + target)
- ThemeAnalysis           : FR-004 (7-bucket taxonomy)
- SeverityPrediction      : FR-005 (trigger rules)
- EscalationRiskAssessment: FR-006
- PriorityRecommendation  : FR-007 (SLA breach probability)
- RootCauseAnalysis       : FR-016
- LanguageDetection       : FR-019
- ResolutionRecommendation: FR-011 (NBA + routing rule)
- All models carry explanation + evidence fields (FR-020)
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AnalysisMetadata:
    model_used: str = ""
    processing_time_ms: float = 0.0
    token_usage: dict[str, int] = field(default_factory=dict)
    prompt_name: str = ""
    explanation: str = ""


# ---------------------------------------------------------------------------
# FR-002 — Complaint Detection
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ComplaintDetection:
    is_complaint: bool = False
    detection_type: str = "none"           # "definite" | "possible" | "none"
    confidence: float = 0.0
    primary_complaint_statement: str = ""
    excerpt: str = ""
    detected_language: str = "en"          # "ar" | "en" | "mixed"
    explanation: str = ""
    evidence: list[str] = field(default_factory=list)
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)


# ---------------------------------------------------------------------------
# FR-003 — Enhanced Sentiment Analysis (segment trend + target)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SentimentAnalysis:
    sentiment: str = ""                    # overall: very_positive/positive/neutral/negative/very_negative
    sentiment_start: str = ""              # beginning of interaction
    sentiment_end: str = ""                # end of interaction
    sentiment_trend: str = ""              # "improving" | "declining" | "stable" | "volatile"
    polarity: float = 0.0                  # -1.0 to 1.0
    emotions: dict[str, float] = field(default_factory=dict)
    intensity: float = 0.0
    sentiment_target: str = ""             # "claim_process" | "agent_staff" | "provider" | ...
    confidence: float = 0.0
    explanation: str = ""
    evidence: list[str] = field(default_factory=list)
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)


# ---------------------------------------------------------------------------
# FR-004 — Theme Analysis (7-bucket LuMay taxonomy)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ThemeAnalysis:
    primary_theme: str = ""                # One of the 7 LuMay buckets
    secondary_themes: list[str] = field(default_factory=list)
    subcategory: str = ""
    keywords: list[str] = field(default_factory=list)
    confidence: float = 0.0
    explanation: str = ""
    evidence: list[str] = field(default_factory=list)
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)


# ---------------------------------------------------------------------------
# FR-005 — Severity Prediction (trigger rules)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SeverityPrediction:
    severity: str = ""                     # "critical" | "high" | "medium" | "low"
    severity_score: float = 0.0
    urgency: str = ""                      # "immediate" | "high" | "moderate" | "low"
    impact: str = ""                       # "financial_loss" | "regulatory_risk" | ...
    auto_escalation_triggers: list[str] = field(default_factory=list)
    confidence: float = 0.0
    explanation: str = ""
    evidence: list[str] = field(default_factory=list)
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)


# ---------------------------------------------------------------------------
# FR-006 — Escalation Risk Assessment (0-100)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class EscalationRiskAssessment:
    escalation_risk_score: int = 0         # 0-100
    risk_level: str = "low"               # "low" | "medium" | "high" | "critical"
    triggers: list[str] = field(default_factory=list)
    confidence: float = 0.0
    explanation: str = ""
    evidence: list[str] = field(default_factory=list)
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)


# ---------------------------------------------------------------------------
# FR-007 — Priority + SLA Breach Prediction
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PriorityRecommendation:
    priority: str = ""                     # "critical" | "high" | "medium" | "low"
    priority_score: float = 0.0
    sla_risk: str = ""                     # "breached" | "at_risk" | "within_sla"
    breach_probability: int = 0            # 0-100
    sla_hours_remaining: float | None = None
    estimated_breach_time: str | None = None
    rationale: str = ""
    confidence: float = 0.0
    explanation: str = ""
    evidence: list[str] = field(default_factory=list)
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)


# ---------------------------------------------------------------------------
# FR-011 — Complaint Summary (bilingual)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ComplaintSummary:
    summary: str = ""
    key_points: list[str] = field(default_factory=list)
    mentioned_entities: dict[str, list[str]] = field(default_factory=dict)
    detected_language: str = "en"
    word_count: int = 0
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)


# ---------------------------------------------------------------------------
# FR-011 — Resolution Recommendation (NBA + routing rule)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ResolutionRecommendation:
    recommended_action: str = ""
    steps: list[str] = field(default_factory=list)
    department: str = ""
    routing_rule: str = ""
    escalation_required: bool = False
    estimated_resolution_time: str = ""
    suggested_response_template: str = ""
    confidence: float = 0.0
    explanation: str = ""
    evidence: list[str] = field(default_factory=list)
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)


# ---------------------------------------------------------------------------
# FR-016 — Root Cause Analysis
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class RootCauseAnalysis:
    root_cause: str = ""
    root_cause_category: str = ""         # "process_failure" | "system_technical" | ...
    contributing_factors: list[str] = field(default_factory=list)
    process_failure_point: str = ""
    recommended_fix: str = ""
    prevention_suggestion: str = ""
    confidence: float = 0.0
    explanation: str = ""
    evidence: list[str] = field(default_factory=list)
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)


# ---------------------------------------------------------------------------
# FR-019 — Language Detection
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class LanguageDetection:
    detected_language: str = "en"          # "ar" | "en" | "mixed" | "other"
    language_confidence: float = 0.0
    arabic_percentage: int = 0
    english_percentage: int = 100
    contains_arabic_insurance_terms: bool = False
    script: str = "latin"                  # "arabic" | "latin" | "mixed"
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)


# ---------------------------------------------------------------------------
# Duplicate Detection (unchanged)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DuplicateComplaintResult:
    is_duplicate: bool = False
    matched_complaint_id: str = ""
    similarity_score: float = 0.0
    threshold: float = 0.0
    match_reason: str = ""
    confidence: float = 0.0
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)


# ---------------------------------------------------------------------------
# FR-002 to FR-020 — Full Analysis (all pipelines combined)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ComplaintAnalysis:
    detection: ComplaintDetection = field(default_factory=ComplaintDetection)
    classification: "ComplaintClassification" = field(default_factory=lambda: ComplaintClassification())
    sentiment: SentimentAnalysis = field(default_factory=SentimentAnalysis)
    themes: ThemeAnalysis = field(default_factory=ThemeAnalysis)
    severity: SeverityPrediction = field(default_factory=SeverityPrediction)
    escalation: EscalationRiskAssessment = field(default_factory=EscalationRiskAssessment)
    priority: PriorityRecommendation = field(default_factory=PriorityRecommendation)
    summary: ComplaintSummary = field(default_factory=ComplaintSummary)
    root_cause: RootCauseAnalysis = field(default_factory=RootCauseAnalysis)
    resolution: ResolutionRecommendation = field(default_factory=ResolutionRecommendation)
    duplicate: DuplicateComplaintResult = field(default_factory=DuplicateComplaintResult)
    language: LanguageDetection = field(default_factory=LanguageDetection)
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)


# ---------------------------------------------------------------------------
# Classification (kept for backward compat)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ComplaintClassification:
    category: str = ""
    subcategory: str = ""
    issue_type: str = ""
    confidence: float = 0.0
    explanation: str = ""
    evidence: list[str] = field(default_factory=list)
    metadata: AnalysisMetadata = field(default_factory=AnalysisMetadata)
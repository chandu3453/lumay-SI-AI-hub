"""Complaint Intelligence — AI-powered complaint analysis.

Provides reusable business intelligence services for complaint analysis:
classification, sentiment, themes, severity, priority, summarization,
duplicate detection, and resolution recommendations.

All analysis consumes the AI Gateway — no provider is called directly.
"""

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
from ai.intelligence.prompts import register_complaint_prompts
from ai.intelligence.service import ComplaintIntelligenceService

__all__ = [
    "AnalysisMetadata",
    "ComplaintAnalysis",
    "ComplaintClassification",
    "ComplaintIntelligenceService",
    "ComplaintSummary",
    "DuplicateComplaintResult",
    "PriorityRecommendation",
    "ResolutionRecommendation",
    "SentimentAnalysis",
    "SeverityPrediction",
    "ThemeAnalysis",
    "register_complaint_prompts",
]
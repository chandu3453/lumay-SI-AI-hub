"""
Response evaluator — scores LLM outputs on quality and safety dimensions.

Evaluates generated responses for correctness, relevance, safety,
conciseness, and structure compliance.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EvaluationMetric(StrEnum):
    """Supported evaluation dimensions."""

    CORRECTNESS = "correctness"
    RELEVANCE = "relevance"
    SAFETY = "safety"
    CONCISENESS = "conciseness"
    STRUCTURE = "structure"
    HALLUCINATION = "hallucination"


@dataclass(frozen=True)
class EvaluationResult:
    """Results of a single response evaluation.

    Attributes:
        scores:       Map of metric → score (0.0 – 1.0).
        passed:       True if all metrics met their thresholds.
        diagnostics:  Per-metric diagnostic details.
    """

    scores: dict[str, float]
    passed: bool
    diagnostics: dict[str, Any] = field(default_factory=dict)


class ResponseEvaluator:
    """Scores LLM responses across multiple evaluation dimensions.

    Args:
        thresholds: Map of metric → minimum acceptable score.
    """

    def __init__(self, thresholds: dict[EvaluationMetric, float] | None = None) -> None:
        ...

    async def evaluate(
        self, prompt: str, response: str, context: dict[str, Any] | None = None
    ) -> EvaluationResult:
        """Runs all configured evaluations on a prompt-response pair."""
        ...

    async def evaluate_batch(
        self, pairs: list[tuple[str, str]], context: dict[str, Any] | None = None
    ) -> list[EvaluationResult]:
        """Batch evaluation of multiple prompt-response pairs."""
        ...

"""
Evaluation metrics — individual scoring functions for LLM outputs.

Contains the implementation of each evaluation metric used by
the ResponseEvaluator. Each metric returns a normalised score (0.0 – 1.0).
"""

from typing import Any


class CorrectnessMetric:
    """Scores factual correctness against a ground-truth reference."""

    async def score(self, response: str, reference: str) -> float:
        ...


class RelevanceMetric:
    """Scores how well the response addresses the input prompt."""

    async def score(self, prompt: str, response: str) -> float:
        ...


class SafetyMetric:
    """Scores the response for harmful or unsafe content."""

    async def score(self, response: str) -> float:
        ...


class ConcisenessMetric:
    """Scores the response for brevity and absence of filler."""

    async def score(self, response: str) -> float:
        ...


class HallucinationMetric:
    """Detects hallucinated facts by comparing response against retrieved context."""

    async def score(self, response: str, context: str) -> float:
        ...

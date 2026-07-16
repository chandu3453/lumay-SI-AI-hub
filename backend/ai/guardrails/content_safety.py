"""
Content safety guardrail — blocks toxic, offensive, or unsafe content.

Evaluates text against content safety categories and returns
a pass/fail decision with a risk score.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ContentSafetyResult:
    """Result of a content safety evaluation.

    Attributes:
        passed:       True if no violations were detected.
        categories:   Map of category → risk score (0.0 – 1.0).
        top_category: The category with the highest risk score.
        details:      Additional diagnostics or flagged snippets.
    """

    passed: bool
    categories: dict[str, float]
    top_category: str | None = None
    details: dict[str, Any] | None = None


class ContentSafetyGuard:
    """Evaluates text for content safety violations.

    Categories include: hate, harassment, self-harm, sexual, violence, toxic.
    """

    def __init__(self, threshold: float = 0.7) -> None:
        ...

    async def check(self, text: str) -> ContentSafetyResult:
        """Runs safety evaluation on the input text."""
        ...

    async def check_batch(self, texts: list[str]) -> list[ContentSafetyResult]:
        """Batch safety evaluation for multiple texts."""
        ...

"""
PII guardrail — detects and redacts personally identifiable information.

Supports configurable entity types (SSN, email, phone, credit card, etc.)
with both detection and replacement modes.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PIIDetection:
    """A single detected PII entity.

    Attributes:
        type:     Entity type label (e.g. "ssn", "email", "phone").
        value:    The detected text snippet.
        start:    Character offset start.
        end:      Character offset end.
        score:    Confidence score for the detection.
    """

    type: str
    value: str
    start: int
    end: int
    score: float


@dataclass(frozen=True)
class PIIGuardResult:
    """Result of PII scanning/redaction.

    Attributes:
        redacted_text: Text with PII replaced (only in redact mode).
        detections:    List of all detected PII entities.
        entity_counts: Count of detections per entity type.
    """

    redacted_text: str | None = None
    detections: list[PIIDetection] = field(default_factory=list)
    entity_counts: dict[str, int] = field(default_factory=dict)


class PIIGuard:
    """Detects and optionally redacts PII from text.

    Args:
        enabled_entities: Subset of entity types to scan (None = all).
        redact_mode:      If True, replaces PII with placeholders.
        redact_token:     Replacement string for redacted entities.
    """

    def __init__(
        self,
        enabled_entities: list[str] | None = None,
        redact_mode: bool = True,
        redact_token: str = "[REDACTED]",
    ) -> None:
        ...

    async def scan(self, text: str) -> PIIGuardResult:
        """Detects PII entities in the input text."""
        ...

    async def redact(self, text: str) -> str:
        """Detects and replaces all PII with the configured token."""
        ...

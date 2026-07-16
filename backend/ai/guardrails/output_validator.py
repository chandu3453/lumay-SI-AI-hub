"""
Output validator guardrail — ensures structured output conforms to expected schema.

Validates LLM outputs against JSON Schema, Pydantic models,
or custom predicate functions before returning to the caller.
"""

from typing import Any


class ValidationError(Exception):
    """Raised when output validation fails."""


class OutputValidator:
    """Validates LLM output against a schema or model.

    Supports JSON Schema validation, Pydantic model validation,
    and custom callable validators.
    """

    def __init__(self, schema: dict[str, Any] | None = None) -> None:
        ...

    async def validate_json(self, output: str) -> dict[str, Any]:
        """Parses and validates JSON output against the configured schema."""
        ...

    async def validate_model(self, output: dict[str, Any], model_class: type) -> Any:
        """Validates a dict against a Pydantic model class."""
        ...

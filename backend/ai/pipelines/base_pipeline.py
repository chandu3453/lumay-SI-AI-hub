"""
Base pipeline — abstract foundation for all domain-specific AI pipelines.

Each pipeline wires together providers, prompts, retrieval, guardrails,
and evaluation into a complete, observable workflow step.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PipelineContext:
    """Context passed through all pipeline steps.

    Attributes:
        session_id:        Optional conversation session identifier.
        user_id:           Optional user identifier for audit.
        domain:            Domain context (complaint, interaction, etc.).
        metadata:          Arbitrary metadata forwarded to all steps.
    """

    session_id: str | None = None
    user_id: str | None = None
    domain: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PipelineResult:
    """Result of a pipeline execution.

    Attributes:
        success:       Whether the pipeline completed successfully.
        output:        Final output of the pipeline.
        steps:         Outputs from each pipeline step for observability.
        latency_ms:    Total pipeline execution time.
        usage:         Aggregate token usage across all LLM calls.
    """

    success: bool
    output: dict[str, Any] | None = None
    steps: dict[str, Any] = field(default_factory=dict)
    latency_ms: float | None = None
    usage: dict[str, int] | None = None


class BasePipeline(ABC):
    """Abstract base for all domain-specific AI pipelines.

    Subclasses define their step sequence and wire dependencies.
    """

    def __init__(self, name: str) -> None:
        ...

    @abstractmethod
    async def run(self, input_data: dict[str, Any], context: PipelineContext | None = None) -> PipelineResult:
        """Executes the full pipeline with the given input."""
        ...

    async def validate_input(self, input_data: dict[str, Any]) -> None:
        """Validates pipeline input before execution."""
        ...

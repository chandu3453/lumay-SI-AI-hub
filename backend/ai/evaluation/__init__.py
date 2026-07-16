"""
AI Evaluation — quality metrics, safety scoring, and response assessment.

Evaluates LLM outputs for correctness, relevance, safety, and structure.
Metrics are collected and exposed for monitoring and observability.

Exports:
  ResponseEvaluator  — Scores LLM responses on quality and safety dimensions.
  EvaluationMetric   — Enum of supported evaluation dimensions.
  EvaluationResult   — Dataclass wrapping scores and diagnostics.
"""

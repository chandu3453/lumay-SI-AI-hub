"""
AI Guardrails — safety and compliance filters.

Guardrails run before (input guard) and after (output guard) every LLM invocation.
They are composed into chains and can be configured per-pipeline.

Exports:
  ContentSafetyGuard   — Blocks toxic, offensive, or unsafe content.
  PIIGuard             — Detects and redacts personally identifiable information.
  OutputValidator      — Ensures structured output conforms to expected schema.
"""

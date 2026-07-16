"""
AI Pipelines — end-to-end domain-specific AI workflows.

Each pipeline wires together providers, prompts, retrieval, guardrails,
and evaluation into a complete domain workflow.

Exports:
  BasePipeline         — Abstract base for all domain pipelines.
  ComplaintPipeline    — Complaint intelligence pipeline (classification + sentiment).
  SentimentPipeline    — Sentiment analysis pipeline.
  ClassificationPipeline — Multi-label classification pipeline.
"""

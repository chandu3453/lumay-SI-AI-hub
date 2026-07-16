"""System-level prompt templates for the AI platform.

Contains the system prompts used by various pipelines —
complaint classification, sentiment analysis, PII redaction, etc.
"""

from ai.prompts.base_prompt import BasePrompt


class ComplaintClassifierPrompt(BasePrompt):
    """System prompt for complaint classification and triage."""


class SentimentAnalysisPrompt(BasePrompt):
    """System prompt for sentiment analysis of complaint text."""


class PIIRedactionPrompt(BasePrompt):
    """System prompt for PII detection and redaction guidance."""


class SummarisationPrompt(BasePrompt):
    """System prompt for conversation and document summarisation."""
"""
Memory summarizer — compresses long conversation histories into concise summaries.

Used when the sliding window would otherwise lose important context
from early turns. Summaries are stored alongside the active window.
"""

from typing import Any


class MemorySummarizer:
    """Compresses conversation history into a concise summary.

    Uses an LLM call to produce extractive or abstractive summaries
    from the full message history.
    """

    def __init__(self, max_summary_tokens: int = 512) -> None:
        ...

    async def summarize(self, messages: list[dict[str, Any]]) -> str:
        """Generates a summary from a list of messages."""
        ...

    async def incremental_summary(
        self, previous_summary: str, new_messages: list[dict[str, Any]]
    ) -> str:
        """Updates an existing summary with new messages (no full re-summarisation)."""
        ...

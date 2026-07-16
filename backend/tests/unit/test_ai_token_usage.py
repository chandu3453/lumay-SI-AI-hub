"""AI Platform — token usage tracking tests."""

import pytest

from ai.models import TokenUsage
from ai.token_usage import TokenTracker, estimate_tokens


class TestTokenTracker:
    def test_record_usage(self) -> None:
        tracker = TokenTracker()
        usage = tracker.record(prompt_tokens=10, completion_tokens=20)
        assert usage.prompt_tokens == 10
        assert usage.completion_tokens == 20
        assert usage.total_tokens == 30
        assert usage.estimated_cost is not None
        assert usage.estimated_cost > 0

    def test_multiple_records(self) -> None:
        tracker = TokenTracker()
        tracker.record(prompt_tokens=10, completion_tokens=10)
        tracker.record(prompt_tokens=20, completion_tokens=30)
        assert tracker.total_prompt_tokens == 30
        assert tracker.total_completion_tokens == 40
        assert tracker.total_tokens == 70

    def test_total_cost(self) -> None:
        tracker = TokenTracker()
        tracker.record(prompt_tokens=1000, completion_tokens=1000)
        cost = tracker.total_cost
        assert cost > 0

    def test_reset(self) -> None:
        tracker = TokenTracker()
        tracker.record(prompt_tokens=10, completion_tokens=10)
        assert tracker.total_tokens == 20
        tracker.reset()
        assert tracker.total_tokens == 0
        assert tracker.total_cost == 0.0


class TestEstimateTokens:
    def test_estimate(self) -> None:
        text = "Hello world, this is a test sentence."
        estimated = estimate_tokens(text)
        assert estimated > 0
        assert estimated <= len(text)

    def test_empty_string(self) -> None:
        assert estimate_tokens("") == 1
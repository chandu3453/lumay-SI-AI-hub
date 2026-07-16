"""AI Platform — token usage tracking and cost estimation."""

import time
from dataclasses import dataclass, field

from ai.config import get_ai_pricing
from ai.models import TokenUsage


@dataclass
class TokenTracker:
    usage: list[TokenUsage] = field(default_factory=list)

    def record(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        model: str | None = None,
    ) -> TokenUsage:
        pricing = get_ai_pricing()
        prompt_cost = (
            (prompt_tokens / 1000) * pricing.gpt4o_per_1k_prompt
        )
        completion_cost = (
            (completion_tokens / 1000) * pricing.gpt4o_per_1k_completion
        )
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost=round(prompt_cost + completion_cost, 6),
        )
        self.usage.append(usage)
        return usage

    @property
    def total_prompt_tokens(self) -> int:
        return sum(u.prompt_tokens for u in self.usage)

    @property
    def total_completion_tokens(self) -> int:
        return sum(u.completion_tokens for u in self.usage)

    @property
    def total_tokens(self) -> int:
        return sum(u.total_tokens for u in self.usage)

    @property
    def total_cost(self) -> float:
        return sum(u.estimated_cost or 0.0 for u in self.usage)

    def reset(self) -> None:
        self.usage.clear()


def estimate_tokens(text: str) -> int:
    return len(text) // 4 + 1


def measure_latency(func):
    async def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = await func(*args, **kwargs)
        elapsed = (time.monotonic() - start) * 1000
        if isinstance(result, tuple):
            return (*result, elapsed)
        return result
    return wrapper
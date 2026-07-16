"""Text encoder — converts text into dense vector embeddings.

Supports batching and optional caching via Redis for efficiency.
Uses the configured embedding provider (Azure OpenAI or OpenAI).
"""

from __future__ import annotations

import math
import time
from typing import Any

from ai.config import get_ai_settings
from ai.exceptions import AIEmbeddingError
from ai.models import EmbeddingResponse
from ai.providers.base import create_provider
from app.platform.logging import get_logger

logger = get_logger(__name__)


class TextEncoder:
    def __init__(self, cache_ttl_seconds: int = 86400, provider: BaseLLMProvider | None = None) -> None:
        self._provider = provider or create_provider(
            get_ai_settings().default_provider
        )
        self._cache_ttl = cache_ttl_seconds
        self._cache: dict[str, list[float]] = {}

    async def encode(self, text: str) -> list[float]:
        if text in self._cache:
            return self._cache[text]
        from ai.models import EmbeddingRequest as ER
        response = await self._provider.embed(ER(input=text))
        vector = response.vectors[0]
        self._cache[text] = vector
        return vector

    async def encode_batch(self, texts: list[str]) -> list[list[float]]:
        uncached = [t for t in texts if t not in self._cache]
        if uncached:
            from ai.models import EmbeddingRequest as ER
            response = await self._provider.embed(ER(input=uncached))
            for text, vector in zip(uncached, response.vectors):
                self._cache[text] = vector
        return [self._cache[t] for t in texts]

    async def similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    async def similarity_batch(
        self, query: list[float], candidates: list[list[float]]
    ) -> list[tuple[int, float]]:
        scores = []
        for i, candidate in enumerate(candidates):
            score = await self.similarity(query, candidate)
            scores.append((i, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def clear_cache(self) -> None:
        self._cache.clear()
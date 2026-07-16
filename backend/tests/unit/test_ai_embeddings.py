"""AI Platform — embedding service unit tests."""

import pytest

from ai.embeddings.encoder import TextEncoder
from ai.providers.local_provider import LocalProvider


class TestTextEncoder:
    def setup_method(self) -> None:
        self.encoder = TextEncoder(provider=LocalProvider())

    async def test_encode_single(self) -> None:
        vector = await self.encoder.encode("Hello world")
        assert len(vector) == 4
        assert all(isinstance(v, float) for v in vector)

    async def test_encode_batch(self) -> None:
        vectors = await self.encoder.encode_batch(["Hello", "World"])
        assert len(vectors) == 2
        assert len(vectors[0]) == 4

    async def test_cache_hit(self) -> None:
        text = "Cached text"
        v1 = await self.encoder.encode(text)
        v2 = await self.encoder.encode(text)
        assert v1 == v2

    async def test_similarity_identical(self) -> None:
        vector = [1.0, 0.0, 0.0, 0.0]
        score = await self.encoder.similarity(vector, vector)
        assert abs(score - 1.0) < 0.01

    async def test_similarity_orthogonal(self) -> None:
        a = [1.0, 0.0, 0.0, 0.0]
        b = [0.0, 1.0, 0.0, 0.0]
        score = await self.encoder.similarity(a, b)
        assert abs(score) < 0.01

    async def test_similarity_zero_vector(self) -> None:
        zero = [0.0, 0.0, 0.0, 0.0]
        a = [1.0, 0.0, 0.0, 0.0]
        score = await self.encoder.similarity(a, zero)
        assert score == 0.0

    async def test_similarity_batch(self) -> None:
        query = [1.0, 0.0, 0.0, 0.0]
        candidates = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.5, 0.5, 0.0, 0.0],
        ]
        scores = await self.encoder.similarity_batch(query, candidates)
        assert len(scores) == 3
        assert scores[0][0] == 0
        assert scores[0][1] > 0.99

    async def test_clear_cache(self) -> None:
        await self.encoder.encode("Clear me")
        assert len(self.encoder._cache) == 1
        self.encoder.clear_cache()
        assert len(self.encoder._cache) == 0
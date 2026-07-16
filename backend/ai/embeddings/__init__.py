"""AI Embeddings — text encoding, vector storage, and similarity search.

Encodes text into dense vector representations using the configured
embedding model and manages vector indices in OpenSearch.
"""

from ai.embeddings.encoder import TextEncoder

__all__ = ["TextEncoder"]
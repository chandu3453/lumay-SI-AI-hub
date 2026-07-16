"""
Vector store service — CRUD operations for vector indices in OpenSearch.

Manages the lifecycle of vector indices: creation, document indexing,
search, and deletion. Uses the OpenSearch k-NN plugin.
"""

from typing import Any


class VectorStoreService:
    """Manages vector indices in OpenSearch.

    Handles index creation with k-NN mappings, document indexing
    with vector fields, and similarity search.
    """

    def __init__(self, index_name: str, vector_dimensions: int = 3072) -> None:
        ...

    async def create_index(self, mapping: dict[str, Any] | None = None) -> None:
        """Creates the vector index with k-NN mappings."""
        ...

    async def index_document(
        self, doc_id: str, vector: list[float], text: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """Indexes a document with its embedding vector."""
        ...

    async def search(
        self, query_vector: list[float], top_k: int = 10, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Performs k-NN similarity search."""
        ...

    async def delete_document(self, doc_id: str) -> None:
        """Removes a document from the index."""
        ...

    async def delete_index(self) -> None:
        """Deletes the entire vector index."""
        ...

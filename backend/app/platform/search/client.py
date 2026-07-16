"""
OpenSearch Client.

Manages the OpenSearch async client lifecycle.
Provides a base search service for domain-specific search adapters.
"""

from typing import Any

from opensearchpy import AsyncOpenSearch

from app.config import get_settings
from app.platform.logging import get_logger

logger = get_logger(__name__)

_search_client: AsyncOpenSearch | None = None


async def init_search_client() -> None:
    """Initialises the async OpenSearch client."""
    global _search_client

    settings = get_settings()

    _search_client = AsyncOpenSearch(
        hosts=[settings.opensearch.url],
        http_auth=(settings.opensearch.user, settings.opensearch.password),
        use_ssl=settings.opensearch.use_ssl,
        verify_certs=False,
        ssl_show_warn=False,
    )

    logger.info("opensearch_client_initialized", url=settings.opensearch.url)


async def close_search_client() -> None:
    """Closes the OpenSearch connection pool."""
    global _search_client

    if _search_client is not None:
        await _search_client.close()
        _search_client = None
        logger.info("opensearch_client_closed")


def get_search_client() -> AsyncOpenSearch:
    if _search_client is None:
        raise RuntimeError("Search client is not initialised. Call init_search_client() first.")
    return _search_client


class BaseSearchService:
    """
    Abstract base for domain-specific OpenSearch services.
    Provides index management and document CRUD scaffolding.
    """

    def __init__(self, index_name: str) -> None:
        self._index = index_name

    async def index_document(self, doc_id: str, body: dict[str, Any]) -> dict[str, Any]:
        client = get_search_client()
        return await client.index(index=self._index, id=doc_id, body=body, refresh="wait_for")

    async def get_document(self, doc_id: str) -> dict[str, Any] | None:
        client = get_search_client()
        try:
            result = await client.get(index=self._index, id=doc_id)
            return result.get("_source")
        except Exception:
            return None

    async def delete_document(self, doc_id: str) -> None:
        client = get_search_client()
        await client.delete(index=self._index, id=doc_id, ignore=[404])

    async def search(self, query: dict[str, Any]) -> dict[str, Any]:
        client = get_search_client()
        return await client.search(index=self._index, body=query)

    async def ping(self) -> bool:
        try:
            client = get_search_client()
            return await client.ping()
        except Exception:
            return False

"""Search platform — OpenSearch client lifecycle and BaseSearchService."""

from app.platform.search.client import (
    BaseSearchService,
    close_search_client,
    get_search_client,
    init_search_client,
)

__all__ = [
    "BaseSearchService",
    "close_search_client",
    "get_search_client",
    "init_search_client",
]

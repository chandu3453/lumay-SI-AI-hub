"""Search domain exceptions."""
from domains.search.exceptions.search_exceptions import (
    SearchQueryError,
    IndexNotFoundError,
    SearchServiceUnavailableError,
)

__all__ = [
    "SearchQueryError",
    "IndexNotFoundError",
    "SearchServiceUnavailableError",
]

"""
Pagination Utilities.

Reusable helpers for offset-based pagination.
"""

from dataclasses import dataclass

from app.shared.constants.platform import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE


@dataclass(frozen=True)
class PaginationParams:
    """Parsed, validated pagination parameters."""

    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def parse_pagination(page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> PaginationParams:
    """
    Validates and normalises pagination parameters.
    Clamps page_size to the allowed range.
    """
    page = max(1, page)
    page_size = max(1, min(page_size, MAX_PAGE_SIZE))
    return PaginationParams(page=page, page_size=page_size)

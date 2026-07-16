"""
Pagination Utilities.

Reusable offset-based pagination across all domain list endpoints.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import Field

from shared.base_schema import AppBaseModel

DataT = TypeVar("DataT")

DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 500


@dataclass(frozen=True)
class PaginationParams:
    """Validated pagination parameters."""

    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def parse_pagination(
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> PaginationParams:
    """Normalises and validates pagination query parameters."""
    return PaginationParams(
        page=max(1, page),
        page_size=max(1, min(page_size, MAX_PAGE_SIZE)),
    )


class PaginationMeta(AppBaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def build(cls, page: int, page_size: int, total_items: int) -> "PaginationMeta":
        total_pages = max(1, -(-total_items // page_size))
        return cls(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )


class PagedResponse(AppBaseModel, Generic[DataT]):
    """Standard paginated API response envelope."""

    data: list[DataT]
    pagination: PaginationMeta

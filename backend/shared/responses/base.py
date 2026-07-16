"""
Standard API Response Envelopes.

All API responses are wrapped in these typed envelopes for
consistent client-facing contracts across all domains.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class SuccessResponse(BaseModel, Generic[DataT]):
    """Standard success envelope for single-resource responses."""

    success: bool = True
    data: DataT


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Standard paginated response envelope for list resources."""

    success: bool = True
    data: list[DataT]
    pagination: "PaginationMeta"


class PaginationMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=500)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    has_next: bool
    has_previous: bool

    @classmethod
    def from_counts(cls, page: int, page_size: int, total_items: int) -> "PaginationMeta":
        total_pages = max(1, -(-total_items // page_size))  # ceiling division
        return cls(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )

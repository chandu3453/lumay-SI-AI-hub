"""
Standard API Response Schemas.

All API endpoints return one of these envelopes for consistency.
"""

from typing import Any, Generic, TypeVar

from pydantic import Field

from shared.base_schema import AppBaseModel

DataT = TypeVar("DataT")


class SuccessResponse(AppBaseModel, Generic[DataT]):
    success: bool = True
    data: DataT


class ListResponse(AppBaseModel, Generic[DataT]):
    success: bool = True
    data: list[DataT]
    total: int
    page: int = 1
    page_size: int = 20


class PaginatedResponse(AppBaseModel, Generic[DataT]):
    success: bool = True
    data: list[DataT]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorDetail(AppBaseModel):
    field: str
    message: str


class ErrorResponse(AppBaseModel):
    success: bool = False
    error_code: str
    message: str
    context: dict[str, Any] = Field(default_factory=dict)

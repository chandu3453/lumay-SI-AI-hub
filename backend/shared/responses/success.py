from typing import Any, Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class SuccessResponse(BaseModel, Generic[DataT]):
    success: bool = True
    data: DataT


class ListResponse(BaseModel, Generic[DataT]):
    success: bool = True
    data: list[DataT]
    total: int
    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel, Generic[DataT]):
    success: bool = True
    data: list[DataT]
    total: int
    page: int
    page_size: int
    total_pages: int

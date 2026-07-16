"""
Standard Error Response Schema.
"""

from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error envelope returned for all 4xx and 5xx responses."""

    success: bool = False
    error_code: str
    message: str
    context: dict[str, Any] = Field(default_factory=dict)

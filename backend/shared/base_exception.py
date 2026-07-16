"""
Application Exception Hierarchy.

All domain exceptions inherit from AppException.
Maps to HTTP status codes for consistent error responses.
"""

from http import HTTPStatus


class AppException(Exception):
    """Root application exception."""

    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        error_code: str | None = None,
        context: dict | None = None,
    ) -> None:
        self.message = message or self.__class__.message
        self.error_code = error_code or self.__class__.error_code
        self.context = context or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "NOT_FOUND"
    message = "Resource not found."


class ConflictError(AppException):
    status_code = HTTPStatus.CONFLICT
    error_code = "CONFLICT"
    message = "Resource conflict."


class ValidationError(AppException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"
    message = "Validation failed."


class UnauthorizedError(AppException):
    status_code = HTTPStatus.UNAUTHORIZED
    error_code = "UNAUTHORIZED"
    message = "Authentication required."


class ForbiddenError(AppException):
    status_code = HTTPStatus.FORBIDDEN
    error_code = "FORBIDDEN"
    message = "Insufficient permissions."


class ServiceUnavailableError(AppException):
    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    error_code = "SERVICE_UNAVAILABLE"
    message = "Upstream service unavailable."

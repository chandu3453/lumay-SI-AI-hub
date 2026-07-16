"""
Base Application Exceptions.

All domain exceptions inherit from these base classes.
Ensures consistent error serialisation across the platform.
"""

from http import HTTPStatus


class AppException(Exception):
    """
    Base exception for all application-level errors.
    Maps to an HTTP status code and structured error payload.
    """

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
    message = "The requested resource was not found."


class ValidationError(AppException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"
    message = "Input validation failed."


class ConflictError(AppException):
    status_code = HTTPStatus.CONFLICT
    error_code = "CONFLICT"
    message = "A resource conflict occurred."


class UnauthorizedError(AppException):
    status_code = HTTPStatus.UNAUTHORIZED
    error_code = "UNAUTHORIZED"
    message = "Authentication is required."


class ForbiddenError(AppException):
    status_code = HTTPStatus.FORBIDDEN
    error_code = "FORBIDDEN"
    message = "You do not have permission to perform this action."


class ServiceUnavailableError(AppException):
    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    error_code = "SERVICE_UNAVAILABLE"
    message = "A downstream service is currently unavailable."


class ExternalIntegrationError(AppException):
    status_code = HTTPStatus.BAD_GATEWAY
    error_code = "EXTERNAL_INTEGRATION_ERROR"
    message = "An external integration returned an unexpected response."

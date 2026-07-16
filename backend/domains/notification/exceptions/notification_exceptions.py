"""Notification Domain Exceptions."""

from http import HTTPStatus

from shared.base_exception import AppException


class NotificationNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "NOTIFICATION__NOT_FOUND"
    message = "Notification not found."


class NotificationValidationError(AppException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "NOTIFICATION__VALIDATION_ERROR"
    message = "Notification data validation failed."


class NotificationAlreadyExistsError(AppException):
    status_code = HTTPStatus.CONFLICT
    error_code = "NOTIFICATION__ALREADY_EXISTS"
    message = "A notification with this identifier already exists."
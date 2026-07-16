"""Complaint Domain Exceptions."""

from http import HTTPStatus

from shared.base_exception import AppException


class ComplaintNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "COMPLAINT__NOT_FOUND"
    message = "Complaint not found."


class ComplaintAlreadyExistsError(AppException):
    status_code = HTTPStatus.CONFLICT
    error_code = "COMPLAINT__ALREADY_EXISTS"
    message = "A complaint with this identifier already exists."


class ComplaintValidationError(AppException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "COMPLAINT__VALIDATION_ERROR"
    message = "Complaint data validation failed."

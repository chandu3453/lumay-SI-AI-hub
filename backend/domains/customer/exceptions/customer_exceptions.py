"""Customer Domain Exceptions."""

from http import HTTPStatus

from shared.base_exception import AppException


class CustomerNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "CUSTOMER__NOT_FOUND"
    message = "Customer not found."


class CustomerAlreadyExistsError(AppException):
    status_code = HTTPStatus.CONFLICT
    error_code = "CUSTOMER__ALREADY_EXISTS"
    message = "A customer with this identifier already exists."


class CustomerProfileIncompleteError(AppException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "CUSTOMER__PROFILE_INCOMPLETE"
    message = "Customer profile is incomplete and cannot be processed."


class CustomerValidationError(AppException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "CUSTOMER__VALIDATION_ERROR"
    message = "Customer data validation failed."

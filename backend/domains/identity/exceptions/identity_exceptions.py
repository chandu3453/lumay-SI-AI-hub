"""Identity domain exceptions."""

from http import HTTPStatus

from shared.base_exception import AppException


class UserNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "IDENTITY__USER_NOT_FOUND"
    message = "User not found."


class UserAlreadyExistsError(AppException):
    status_code = HTTPStatus.CONFLICT
    error_code = "IDENTITY__USER_ALREADY_EXISTS"
    message = "A user with this email already exists."


class InvalidCredentialsError(AppException):
    status_code = HTTPStatus.UNAUTHORIZED
    error_code = "IDENTITY__INVALID_CREDENTIALS"
    message = "Invalid email or password."


class AccountDisabledError(AppException):
    status_code = HTTPStatus.FORBIDDEN
    error_code = "IDENTITY__ACCOUNT_DISABLED"
    message = "This account has been disabled."


class TokenInvalidError(AppException):
    status_code = HTTPStatus.UNAUTHORIZED
    error_code = "IDENTITY__TOKEN_INVALID"
    message = "Authentication token is invalid or expired."

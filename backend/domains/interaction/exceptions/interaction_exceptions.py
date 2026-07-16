"""
Interaction Domain Exceptions.
"""

from http import HTTPStatus

from shared.base_exception import AppException


class InteractionNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "INTERACTION__NOT_FOUND"
    message = "Interaction not found."


class InteractionAlreadyProcessedError(AppException):
    status_code = HTTPStatus.CONFLICT
    error_code = "INTERACTION__ALREADY_PROCESSED"
    message = "This interaction has already been processed."


class InvalidInteractionChannelError(AppException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "INTERACTION__INVALID_CHANNEL"
    message = "The specified interaction channel is not supported."

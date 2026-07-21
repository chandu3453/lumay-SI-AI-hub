"""Conversation Domain Exceptions."""

from http import HTTPStatus

from shared.base_exception import AppException


class ConversationNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "CONVERSATION__NOT_FOUND"
    message = "Conversation not found."


class InvalidConversationTransitionError(AppException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "CONVERSATION__INVALID_TRANSITION"
    message = "The requested conversation status transition is not allowed."


class UnsupportedChannelError(AppException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "CONVERSATION__UNSUPPORTED_CHANNEL"
    message = "The specified channel is not supported."


class MessageNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "CONVERSATION__MESSAGE_NOT_FOUND"
    message = "Message not found."


class MessageNotEditableError(AppException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "CONVERSATION__MESSAGE_NOT_EDITABLE"
    message = "Only internal notes can be edited or deleted — customer-visible messages are immutable."

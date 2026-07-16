"""Workflow Domain Exceptions."""

from http import HTTPStatus

from shared.base_exception import AppException


class WorkflowNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "WORKFLOW__NOT_FOUND"
    message = "Workflow not found."


class WorkflowValidationError(AppException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "WORKFLOW__VALIDATION_ERROR"
    message = "Workflow data validation failed."


class WorkflowAlreadyExistsError(AppException):
    status_code = HTTPStatus.CONFLICT
    error_code = "WORKFLOW__ALREADY_EXISTS"
    message = "A workflow with this identifier already exists."
"""
Audit Domain Exceptions.
"""

from http import HTTPStatus

from shared.base_exception import AppException


class AuditLogNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "AUDIT__LOG_NOT_FOUND"
    message = "Audit log entry not found."


class AuditLogImmutableError(AppException):
    status_code = HTTPStatus.FORBIDDEN
    error_code = "AUDIT__LOG_IMMUTABLE"
    message = "Audit log entries are immutable and cannot be modified."

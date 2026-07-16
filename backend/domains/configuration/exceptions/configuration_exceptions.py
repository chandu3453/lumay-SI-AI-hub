"""
Configuration Domain Exceptions.
"""

from http import HTTPStatus

from shared.base_exception import AppException


class ConfigurationKeyNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "CONFIGURATION__KEY_NOT_FOUND"
    message = "Configuration key not found."


class ConfigurationReadOnlyError(AppException):
    status_code = HTTPStatus.FORBIDDEN
    error_code = "CONFIGURATION__READ_ONLY"
    message = "This configuration key is read-only and cannot be modified at runtime."


class InvalidConfigurationValueError(AppException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "CONFIGURATION__INVALID_VALUE"
    message = "The provided configuration value is invalid."

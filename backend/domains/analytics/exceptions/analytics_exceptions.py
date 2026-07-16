"""
Analytics Domain Exceptions.
"""

from http import HTTPStatus

from shared.base_exception import AppException


class ReportNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "ANALYTICS__REPORT_NOT_FOUND"
    message = "Analytics report not found."


class MetricNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "ANALYTICS__METRIC_NOT_FOUND"
    message = "The requested metric is not available."


class InvalidDateRangeError(AppException):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "ANALYTICS__INVALID_DATE_RANGE"
    message = "The provided date range is invalid."


class ReportGenerationError(AppException):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code = "ANALYTICS__GENERATION_FAILED"
    message = "Failed to generate the analytics report."

"""
Search Domain Exceptions.
"""

from http import HTTPStatus

from shared.base_exception import AppException


class SearchQueryError(AppException):
    status_code = HTTPStatus.BAD_REQUEST
    error_code = "SEARCH__INVALID_QUERY"
    message = "The search query is invalid or malformed."


class IndexNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "SEARCH__INDEX_NOT_FOUND"
    message = "The requested search index does not exist."


class SearchServiceUnavailableError(AppException):
    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    error_code = "SEARCH__SERVICE_UNAVAILABLE"
    message = "The search service is currently unavailable."

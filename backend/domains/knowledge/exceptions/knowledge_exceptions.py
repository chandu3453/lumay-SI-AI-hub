"""
Knowledge Domain Exceptions.
"""

from http import HTTPStatus

from shared.base_exception import AppException


class KnowledgeArticleNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "KNOWLEDGE__ARTICLE_NOT_FOUND"
    message = "Knowledge base article not found."


class KnowledgeCategoryNotFoundError(AppException):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "KNOWLEDGE__CATEGORY_NOT_FOUND"
    message = "Knowledge base category not found."


class KnowledgeIndexingError(AppException):
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code = "KNOWLEDGE__INDEXING_FAILED"
    message = "Failed to index the knowledge base article."

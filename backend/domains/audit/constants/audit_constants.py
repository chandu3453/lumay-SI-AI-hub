"""Audit Domain Constants."""

from enum import StrEnum
from typing import Final


DOMAIN_NAME: Final[str] = "audit"
EXCHANGE_NAME: Final[str] = "lumay.audit"

CACHE_PREFIX_AUDIT: Final[str] = "audit"

# Retention
AUDIT_LOG_RETENTION_DAYS: Final[int] = 2555  # ~7 years (regulatory requirement)


class AuditAction(StrEnum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    ASSIGN = "assign"
    ESCALATE = "escalate"
    RESOLVE = "resolve"


class AuditResourceType(StrEnum):
    USER = "user"
    CUSTOMER = "customer"
    COMPLAINT = "complaint"
    INTERACTION = "interaction"
    WORKFLOW = "workflow"
    DOCUMENT = "document"
    CONFIGURATION = "configuration"

"""Audit domain exceptions."""
from domains.audit.exceptions.audit_exceptions import (
    AuditLogNotFoundError,
    AuditLogImmutableError,
)

__all__ = [
    "AuditLogNotFoundError",
    "AuditLogImmutableError",
]

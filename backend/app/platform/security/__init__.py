"""Security platform — RBAC roles and permission dependency factory."""

from app.platform.security.permissions import Role, require_roles

__all__ = [
    "require_roles",
    "Role",
]

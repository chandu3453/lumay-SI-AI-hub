"""RBAC permission system — role definitions and FastAPI dependency factories."""

from enum import StrEnum

from fastapi import Depends, HTTPException, status

from app.platform.auth.dependencies import CurrentUser
from app.platform.auth.models import TokenPayload


class Role(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    ANALYST = "analyst"
    AGENT = "agent"
    AUDITOR = "auditor"
    READONLY = "readonly"


def require_roles(*roles: Role) -> Depends:  # type: ignore[type-arg]
    """
    FastAPI dependency factory for role-gated endpoints.

    Usage:
        @router.get("/admin", dependencies=[Depends(require_roles(Role.ADMIN))])
    """
    async def _guard(user: CurrentUser) -> TokenPayload:
        if not any(user.has_role(r.value) for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user
    return Depends(_guard)

"""Authentication dependency — re-exports from platform.auth.dependencies."""

from app.platform.auth.dependencies import CurrentUser, get_current_user

__all__ = ["CurrentUser", "get_current_user"]

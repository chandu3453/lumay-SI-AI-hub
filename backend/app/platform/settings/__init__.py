"""Settings platform — re-exports the canonical Settings model."""

from app.config import Environment, Settings, get_settings, reload_settings

__all__ = ["Environment", "get_settings", "reload_settings", "Settings"]

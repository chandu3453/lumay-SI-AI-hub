"""Settings dependency."""

from app.config import Settings, get_settings


def get_app_settings() -> Settings:
    """
    Provides app settings via dependency injection.

    Usage:
        async def endpoint(settings: Settings = Depends(get_app_settings)): ...
    """
    return get_settings()

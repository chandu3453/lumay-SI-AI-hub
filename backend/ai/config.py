"""AI Platform — configuration, integrated with the app settings system.

All getter functions use lazy imports to avoid circular dependencies.
"""

from __future__ import annotations


def get_ai_settings():
    from app.config import get_settings
    return get_settings().ai


def get_ai_pricing():
    from app.config import get_settings
    return get_settings().ai_pricing


def get_azure_openai_settings():
    from app.config import get_settings
    return get_settings().azure_openai


def get_openai_settings():
    from app.config import get_settings
    return get_settings().openai
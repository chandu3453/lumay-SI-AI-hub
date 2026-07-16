"""
Domain Service Base.

Thin marker base class for all domain services.
Enforces constructor injection of dependencies.
"""

from typing import Any


class BaseService:
    """
    Abstract marker for domain services.

    Services contain business rules and orchestrate repositories.
    They must not directly access HTTP request/response objects.
    All dependencies must be injected via __init__.
    """

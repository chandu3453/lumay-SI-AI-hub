"""
Platform-wide Constants.
"""

from typing import Final

# Pagination
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 500

# Cache TTLs (seconds)
CACHE_TTL_SHORT: Final[int] = 60          # 1 minute
CACHE_TTL_MEDIUM: Final[int] = 300        # 5 minutes
CACHE_TTL_LONG: Final[int] = 3600         # 1 hour
CACHE_TTL_EXTENDED: Final[int] = 86400    # 24 hours

# API Version
API_V1_PREFIX: Final[str] = "/api/v1"

# Date Formats
ISO_DATE_FORMAT: Final[str] = "%Y-%m-%d"
ISO_DATETIME_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%SZ"

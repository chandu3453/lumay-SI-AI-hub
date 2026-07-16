"""Configuration Domain Constants."""

from typing import Final


DOMAIN_NAME: Final[str] = "configuration"

CACHE_PREFIX_CONFIG: Final[str] = "config"
CACHE_TTL_CONFIG: Final[int] = 300  # 5 minutes

# Reserved system config key prefixes (read-only at runtime)
SYSTEM_KEY_PREFIXES: Final[tuple[str, ...]] = ("system.", "platform.", "security.")

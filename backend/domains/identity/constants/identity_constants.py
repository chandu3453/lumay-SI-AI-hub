"""Identity domain constants."""

from typing import Final

DOMAIN_NAME: Final[str] = "identity"
EXCHANGE_NAME: Final[str] = "lumay.identity"

PASSWORD_MIN_LENGTH: Final[int] = 12
PASSWORD_MAX_LENGTH: Final[int] = 128
MAX_LOGIN_ATTEMPTS: Final[int] = 5
LOCKOUT_DURATION_MINUTES: Final[int] = 30

CACHE_PREFIX_USER: Final[str] = "identity:user"
CACHE_PREFIX_SESSION: Final[str] = "identity:session"
CACHE_PREFIX_BLACKLIST: Final[str] = "identity:token:blacklist"

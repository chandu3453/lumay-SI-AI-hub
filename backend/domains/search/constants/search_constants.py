"""Search Domain Constants."""

from typing import Final


DOMAIN_NAME: Final[str] = "search"

# OpenSearch index names
INDEX_COMPLAINTS: Final[str] = "lumay-complaints"
INDEX_INTERACTIONS: Final[str] = "lumay-interactions"
INDEX_CUSTOMERS: Final[str] = "lumay-customers"
INDEX_KNOWLEDGE: Final[str] = "lumay-knowledge"

# Search defaults
DEFAULT_RESULT_SIZE: Final[int] = 20
MAX_RESULT_SIZE: Final[int] = 200
MIN_SCORE_THRESHOLD: Final[float] = 0.5

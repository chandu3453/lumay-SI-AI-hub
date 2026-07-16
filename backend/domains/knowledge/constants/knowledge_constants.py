"""Knowledge Domain Constants."""

from enum import StrEnum
from typing import Final


DOMAIN_NAME: Final[str] = "knowledge"
EXCHANGE_NAME: Final[str] = "lumay.knowledge"
OPENSEARCH_INDEX: Final[str] = "lumay-knowledge"

CACHE_PREFIX_KNOWLEDGE: Final[str] = "knowledge"


class ArticleStatus(StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ArticleType(StrEnum):
    FAQ = "faq"
    PROCEDURE = "procedure"
    POLICY = "policy"
    REGULATION = "regulation"
    TEMPLATE = "template"

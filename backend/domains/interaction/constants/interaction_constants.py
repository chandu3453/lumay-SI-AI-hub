"""Interaction Domain Constants."""

from enum import StrEnum
from typing import Final


DOMAIN_NAME: Final[str] = "interaction"
EXCHANGE_NAME: Final[str] = "lumay.interaction"

CACHE_PREFIX_INTERACTION: Final[str] = "interaction"


class InteractionChannel(StrEnum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    VOICE = "voice"
    TEAMS = "teams"
    WEB_FORM = "web_form"
    API = "api"


class InteractionDirection(StrEnum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class InteractionStatus(StrEnum):
    RECEIVED = "received"
    PROCESSING = "processing"
    CLASSIFIED = "classified"
    LINKED = "linked"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"

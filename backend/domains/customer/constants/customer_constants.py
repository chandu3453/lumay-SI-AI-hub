"""Customer Domain Constants."""

from enum import StrEnum
from typing import Final


DOMAIN_NAME: Final[str] = "customer"
EXCHANGE_NAME: Final[str] = "lumay.customer"

CACHE_PREFIX_CUSTOMER: Final[str] = "customer"
CACHE_PREFIX_CUSTOMER_PROFILE: Final[str] = "customer:profile"


class CustomerStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DECEASED = "deceased"
    ARCHIVED = "archived"


class CustomerSegment(StrEnum):
    INDIVIDUAL = "individual"
    CORPORATE = "corporate"
    SME = "sme"
    VIP = "vip"


class CommunicationChannel(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PHONE = "phone"
    WEB_FORM = "web_form"
    API = "api"


class CustomerType(StrEnum):
    PROSPECT = "prospect"
    ACTIVE = "active"
    FORMER = "former"
    CHURNED = "churned"

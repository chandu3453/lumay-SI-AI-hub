"""Analytics Domain Constants."""

from enum import StrEnum
from typing import Final


DOMAIN_NAME: Final[str] = "analytics"
EXCHANGE_NAME: Final[str] = "lumay.analytics"

CACHE_PREFIX_ANALYTICS: Final[str] = "analytics"
CACHE_TTL_DASHBOARD: Final[int] = 300   # 5 minutes
CACHE_TTL_REPORT: Final[int] = 3600     # 1 hour


class ReportType(StrEnum):
    COMPLAINT_SUMMARY = "complaint_summary"
    SENTIMENT_TREND = "sentiment_trend"
    AGENT_PERFORMANCE = "agent_performance"
    SLA_COMPLIANCE = "sla_compliance"
    CHANNEL_VOLUME = "channel_volume"


class TimeGranularity(StrEnum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

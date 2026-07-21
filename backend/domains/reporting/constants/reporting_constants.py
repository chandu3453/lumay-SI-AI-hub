"""Reporting Domain Constants."""

from typing import Final

DOMAIN_NAME: Final[str] = "reporting"

RECENT_CONVERSATIONS_LIMIT: Final[int] = 10
MESSAGE_RESPONSE_TIME_CONVERSATION_CAP: Final[int] = 200
"""Average Response Time is computed from message pairs across the filtered
conversation set — capped to the most recent N conversations so the report
endpoint stays a bounded query rather than scanning every message ever sent."""

NOT_AVAILABLE_MESSAGE: Final[str] = (
    "Not available — no backing domain exists in this system for this data."
)

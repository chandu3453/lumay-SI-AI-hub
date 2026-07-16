"""Repeat Complaint Detection Service — FR-008.

Checks if a new complaint from a customer is a repeat of a prior
complaint within 30, 60, or 90-day windows using theme/semantic matching.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from app.platform.logging import get_logger

logger = get_logger(__name__)

# Repeat complaint windows as specified in BR-002
REPEAT_WINDOWS = [30, 60, 90]


class RepeatComplaintResult:
    """Structured result of repeat complaint check."""

    def __init__(
        self,
        is_repeat: bool = False,
        repeat_window_days: int | None = None,
        prior_complaint_ids: list[str] | None = None,
        prior_complaint_count: int = 0,
        matched_themes: list[str] | None = None,
    ) -> None:
        self.is_repeat = is_repeat
        self.repeat_window_days = repeat_window_days
        self.prior_complaint_ids = prior_complaint_ids or []
        self.prior_complaint_count = prior_complaint_count
        self.matched_themes = matched_themes or []

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_repeat": self.is_repeat,
            "repeat_window_days": self.repeat_window_days,
            "prior_complaint_ids": self.prior_complaint_ids,
            "prior_complaint_count": self.prior_complaint_count,
            "matched_themes": self.matched_themes,
        }


class RepeatComplaintService:
    """FR-008: Check if a complaint is a repeat within time windows.

    Uses the complaint repository to query the customer's complaint history
    within each window, then checks for theme/category overlap.
    """

    def __init__(self, repository: Any) -> None:
        self._repository = repository
        self._logger = get_logger(__name__)

    async def check_repeat_complaint(
        self,
        customer_id: uuid.UUID,
        current_theme: str | None = None,
        current_category: str | None = None,
        exclude_complaint_id: uuid.UUID | None = None,
    ) -> RepeatComplaintResult:
        """Check if the customer has filed a similar complaint within time windows.

        Args:
            customer_id: The customer's UUID
            current_theme: The theme of the new complaint (FR-004 taxonomy)
            current_category: Category of the new complaint (fallback)
            exclude_complaint_id: ID of the current complaint to exclude from history

        Returns:
            RepeatComplaintResult with repeat detection outcome
        """
        now = datetime.now(tz=timezone.utc)

        # Check each window from smallest to largest
        for window_days in REPEAT_WINDOWS:
            since = now - timedelta(days=window_days)

            try:
                prior_complaints = await self._repository.list_by_customer_since(
                    customer_id=customer_id,
                    since=since,
                    exclude_id=exclude_complaint_id,
                )
            except Exception as exc:
                self._logger.warning(
                    "repeat_check_failed",
                    customer_id=str(customer_id),
                    window_days=window_days,
                    error=str(exc),
                )
                continue

            if not prior_complaints:
                continue

            # Find complaints with matching theme or category
            matched_ids: list[str] = []
            matched_themes: list[str] = []

            for prior in prior_complaints:
                prior_theme = getattr(prior, "theme", None)
                prior_category = getattr(prior, "category", None)

                # Theme match (preferred — FR-004 taxonomy)
                if current_theme and prior_theme and prior_theme == current_theme:
                    matched_ids.append(str(prior.id))
                    if prior_theme not in matched_themes:
                        matched_themes.append(prior_theme)
                # Category match (fallback)
                elif (
                    current_category
                    and prior_category
                    and prior_category == current_category
                    and not current_theme
                ):
                    matched_ids.append(str(prior.id))

            if matched_ids:
                self._logger.info(
                    "repeat_complaint_detected",
                    customer_id=str(customer_id),
                    window_days=window_days,
                    prior_count=len(matched_ids),
                )
                return RepeatComplaintResult(
                    is_repeat=True,
                    repeat_window_days=window_days,
                    prior_complaint_ids=matched_ids,
                    prior_complaint_count=len(prior_complaints),
                    matched_themes=matched_themes,
                )

        return RepeatComplaintResult(is_repeat=False)

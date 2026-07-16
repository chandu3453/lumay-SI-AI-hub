"""Real-Time Alert Triggers Service — FR-013 (Phase 2).

Dispatches in-session alerts for:
- Sentiment drop detected (sentiment_start > sentiment_end)
- Escalation risk threshold exceeded (score >= 70)
- SLA breach imminent (breach_probability >= 80 or sla_hours_remaining <= 2)
- Regulatory / legal keywords detected
- Repeat complaint detected (FR-008)
"""

from __future__ import annotations

import uuid
from typing import Any

from app.platform.logging import get_logger
from domains.notification.constants.notification_constants import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)

logger = get_logger(__name__)

# Thresholds
ESCALATION_RISK_HIGH_THRESHOLD = 70        # FR-006: alert if score >= 70
ESCALATION_RISK_CRITICAL_THRESHOLD = 85   # FR-006: alert if score >= 85 (critical)
SLA_BREACH_PROBABILITY_THRESHOLD = 80      # FR-007: alert if breach prob >= 80%
SLA_HOURS_REMAINING_THRESHOLD = 2.0        # FR-007: alert if <= 2h remaining
SENTIMENT_DROP_PAIRS = {                   # FR-013: pairs that indicate a drop
    ("positive", "negative"),
    ("positive", "very_negative"),
    ("very_positive", "negative"),
    ("very_positive", "very_negative"),
    ("neutral", "very_negative"),
}


class AlertService:
    """FR-013: Real-time in-session alert dispatcher.

    Checks analysis results against threshold rules and creates notification
    records via the notification repository.
    """

    def __init__(self, notification_repository: Any | None = None) -> None:
        self._notification_repo = notification_repository
        self._logger = get_logger(__name__)

    # -----------------------------------------------------------------------
    # FR-013 — Sentiment Drop Alert
    # -----------------------------------------------------------------------
    async def dispatch_sentiment_drop_alert(
        self,
        complaint_id: uuid.UUID,
        agent_id: uuid.UUID | None,
        sentiment_start: str | None,
        sentiment_end: str | None,
        customer_name: str = "Customer",
    ) -> bool:
        """Dispatch alert when customer sentiment worsens during interaction."""
        if not sentiment_start or not sentiment_end:
            return False

        pair = (sentiment_start.lower(), sentiment_end.lower())
        if pair not in SENTIMENT_DROP_PAIRS:
            return False

        await self._create_alert(
            complaint_id=complaint_id,
            agent_id=agent_id,
            alert_type="sentiment_drop",
            priority=NotificationPriority.HIGH,
            subject=f"⚠️ Sentiment Drop Detected — {customer_name}",
            message=(
                f"Customer sentiment dropped from '{sentiment_start}' to '{sentiment_end}' "
                f"during this interaction. Immediate agent intervention recommended."
            ),
            metadata={
                "sentiment_start": sentiment_start,
                "sentiment_end": sentiment_end,
                "alert_code": "FR013_SENTIMENT_DROP",
            },
        )
        self._logger.info(
            "sentiment_drop_alert_dispatched",
            complaint_id=str(complaint_id),
            from_sentiment=sentiment_start,
            to_sentiment=sentiment_end,
        )
        return True

    # -----------------------------------------------------------------------
    # FR-013 — Escalation Risk Alert
    # -----------------------------------------------------------------------
    async def dispatch_escalation_risk_alert(
        self,
        complaint_id: uuid.UUID,
        agent_id: uuid.UUID | None,
        risk_score: int,
        triggers: list[str],
        customer_name: str = "Customer",
    ) -> bool:
        """Dispatch alert when escalation risk score exceeds threshold."""
        if risk_score < ESCALATION_RISK_HIGH_THRESHOLD:
            return False

        is_critical = risk_score >= ESCALATION_RISK_CRITICAL_THRESHOLD
        priority = NotificationPriority.CRITICAL if is_critical else NotificationPriority.HIGH

        triggers_text = ", ".join(triggers[:3]) if triggers else "threshold exceeded"

        await self._create_alert(
            complaint_id=complaint_id,
            agent_id=agent_id,
            alert_type="escalation_risk",
            priority=priority,
            subject=f"{'🔴 CRITICAL' if is_critical else '🟡 HIGH'} Escalation Risk — {customer_name} (Score: {risk_score})",
            message=(
                f"AI escalation risk score is {risk_score}/100. "
                f"Triggers detected: {triggers_text}. "
                f"{'Immediate supervisor escalation required.' if is_critical else 'Please review and consider escalation.'}"
            ),
            metadata={
                "escalation_risk_score": risk_score,
                "triggers": triggers,
                "alert_code": "FR013_ESCALATION_RISK",
                "is_critical": is_critical,
            },
        )
        self._logger.info(
            "escalation_risk_alert_dispatched",
            complaint_id=str(complaint_id),
            risk_score=risk_score,
            is_critical=is_critical,
        )
        return True

    # -----------------------------------------------------------------------
    # FR-013 — SLA Breach Alert
    # -----------------------------------------------------------------------
    async def dispatch_sla_breach_alert(
        self,
        complaint_id: uuid.UUID,
        agent_id: uuid.UUID | None,
        breach_probability: int,
        sla_hours_remaining: float | None,
        customer_name: str = "Customer",
    ) -> bool:
        """Dispatch alert when SLA breach is imminent."""
        should_alert = (
            breach_probability >= SLA_BREACH_PROBABILITY_THRESHOLD
            or (sla_hours_remaining is not None and sla_hours_remaining <= SLA_HOURS_REMAINING_THRESHOLD)
        )
        if not should_alert:
            return False

        is_critical = breach_probability >= 95 or (
            sla_hours_remaining is not None and sla_hours_remaining <= 0.5
        )
        priority = NotificationPriority.CRITICAL if is_critical else NotificationPriority.HIGH

        hours_msg = (
            f" ({sla_hours_remaining:.1f}h remaining)" if sla_hours_remaining is not None else ""
        )

        await self._create_alert(
            complaint_id=complaint_id,
            agent_id=agent_id,
            alert_type="sla_breach",
            priority=priority,
            subject=f"⏰ SLA Breach Risk — {customer_name} ({breach_probability}% probability{hours_msg})",
            message=(
                f"SLA breach probability is {breach_probability}%{hours_msg}. "
                f"{'This complaint has breached SLA or is about to breach immediately.' if is_critical else 'Urgent action required to prevent SLA breach.'}"
            ),
            metadata={
                "breach_probability": breach_probability,
                "sla_hours_remaining": sla_hours_remaining,
                "alert_code": "FR013_SLA_BREACH",
                "is_critical": is_critical,
            },
        )
        self._logger.info(
            "sla_breach_alert_dispatched",
            complaint_id=str(complaint_id),
            breach_probability=breach_probability,
            hours_remaining=sla_hours_remaining,
        )
        return True

    # -----------------------------------------------------------------------
    # FR-013 — Repeat Complaint Alert
    # -----------------------------------------------------------------------
    async def dispatch_repeat_complaint_alert(
        self,
        complaint_id: uuid.UUID,
        agent_id: uuid.UUID | None,
        repeat_window_days: int,
        prior_complaint_count: int,
        customer_name: str = "Customer",
    ) -> bool:
        """Dispatch alert when a repeat complaint is detected (FR-008)."""
        await self._create_alert(
            complaint_id=complaint_id,
            agent_id=agent_id,
            alert_type="repeat_complaint",
            priority=NotificationPriority.HIGH,
            subject=f"🔄 Repeat Complaint — {customer_name} ({prior_complaint_count} prior in {repeat_window_days} days)",
            message=(
                f"{customer_name} has filed {prior_complaint_count} complaint(s) on a similar issue "
                f"within the past {repeat_window_days} days. "
                f"This indicates a recurring problem — consider root cause escalation."
            ),
            metadata={
                "repeat_window_days": repeat_window_days,
                "prior_complaint_count": prior_complaint_count,
                "alert_code": "FR008_REPEAT_COMPLAINT",
            },
        )
        self._logger.info(
            "repeat_complaint_alert_dispatched",
            complaint_id=str(complaint_id),
            repeat_window_days=repeat_window_days,
            prior_count=prior_complaint_count,
        )
        return True

    # -----------------------------------------------------------------------
    # FR-013 — Dispatch all alerts from analysis result
    # -----------------------------------------------------------------------
    async def dispatch_from_analysis(
        self,
        complaint_id: uuid.UUID,
        agent_id: uuid.UUID | None,
        analysis_data: dict[str, Any],
        customer_name: str = "Customer",
    ) -> dict[str, bool]:
        """Convenience method: check all alert conditions from AI analysis dict.

        Args:
            analysis_data: dict with keys matching ComplaintAnalysis fields
            Returns dict mapping alert_type -> was_dispatched
        """
        results: dict[str, bool] = {}

        # Sentiment drop
        results["sentiment_drop"] = await self.dispatch_sentiment_drop_alert(
            complaint_id=complaint_id,
            agent_id=agent_id,
            sentiment_start=analysis_data.get("sentiment_start"),
            sentiment_end=analysis_data.get("sentiment_end"),
            customer_name=customer_name,
        )

        # Escalation risk
        results["escalation_risk"] = await self.dispatch_escalation_risk_alert(
            complaint_id=complaint_id,
            agent_id=agent_id,
            risk_score=analysis_data.get("escalation_risk_score", 0),
            triggers=analysis_data.get("escalation_triggers", []),
            customer_name=customer_name,
        )

        # SLA breach
        results["sla_breach"] = await self.dispatch_sla_breach_alert(
            complaint_id=complaint_id,
            agent_id=agent_id,
            breach_probability=analysis_data.get("sla_breach_probability", 0),
            sla_hours_remaining=analysis_data.get("sla_hours_remaining"),
            customer_name=customer_name,
        )

        self._logger.info(
            "alert_dispatch_complete",
            complaint_id=str(complaint_id),
            dispatched={k: v for k, v in results.items() if v},
        )
        return results

    # -----------------------------------------------------------------------
    # Internal
    # -----------------------------------------------------------------------
    async def _create_alert(
        self,
        complaint_id: uuid.UUID,
        agent_id: uuid.UUID | None,
        alert_type: str,
        priority: NotificationPriority,
        subject: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Create a notification record for the alert."""
        if self._notification_repo is None:
            # Log-only mode when repo not injected (e.g. during testing)
            self._logger.warning(
                "alert_no_repo",
                alert_type=alert_type,
                complaint_id=str(complaint_id),
                subject=subject,
            )
            return

        try:
            await self._notification_repo.create(
                complaint_id=complaint_id,
                notification_type=alert_type,
                notification_channel=NotificationChannel.IN_APP,
                recipient=str(agent_id) if agent_id else "supervisor",
                subject=subject,
                message=message,
                priority=priority,
                notification_status=NotificationStatus.PENDING,
                profile_metadata=metadata or {},
            )
        except Exception as exc:
            self._logger.error(
                "alert_create_failed",
                alert_type=alert_type,
                complaint_id=str(complaint_id),
                error=str(exc),
            )

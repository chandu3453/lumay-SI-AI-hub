"""SLA Service — FR-007: Complaint SLA deadline calculation.

Calculates acknowledgment and resolution deadlines based on complaint severity,
using Oman business hours (Sunday–Thursday, 08:00–17:00 AST, UTC+4).
Public holidays are configurable via OMAN_PUBLIC_HOLIDAYS list.

SLA Targets (LuMay Insurance defaults):
    Critical : 4h  acknowledgment / 24h  resolution
    High     : 24h acknowledgment / 72h  resolution
    Medium   : 48h acknowledgment / 5bd  resolution  (~120 business hours)
    Low      : 5bd acknowledgment / 10bd resolution   (~240 business hours)
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from app.platform.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Oman business-hour configuration
# ---------------------------------------------------------------------------
# Working days: Sun=6, Mon=0, Tue=1, Wed=2, Thu=3  (Fri=4, Sat=5 = weekend)
OMAN_WORK_DAYS = {0, 1, 2, 3, 6}  # Mon–Thu + Sun
OMAN_WORK_START = 8   # 08:00 local time
OMAN_WORK_END = 17    # 17:00 local time
OMAN_UTC_OFFSET = 4   # UTC+4 (Arabian Standard Time)

# Configurable Oman public holidays 2025/2026 (yyyy-mm-dd)
OMAN_PUBLIC_HOLIDAYS: set[date] = {
    date(2025, 1, 1),   # New Year's Day
    date(2025, 3, 31),  # Eid Al-Fitr (approx)
    date(2025, 4, 1),
    date(2025, 4, 2),
    date(2025, 6, 6),   # Eid Al-Adha (approx)
    date(2025, 6, 7),
    date(2025, 6, 8),
    date(2025, 11, 18), # National Day
    date(2025, 11, 19),
    date(2026, 1, 1),   # New Year's Day 2026
}

# ---------------------------------------------------------------------------
# SLA hours table (acknowledgment_hours, resolution_hours)
# ---------------------------------------------------------------------------
SLA_TABLE: dict[str, tuple[float, float]] = {
    "critical": (4.0,   24.0),
    "high":     (24.0,  72.0),
    "medium":   (48.0,  120.0),  # 5 business days
    "low":      (120.0, 240.0),  # 5bd / 10bd
    # Backward-compat aliases
    "minor":    (120.0, 240.0),
    "moderate": (48.0,  120.0),
    "major":    (24.0,  72.0),
}

# Alert thresholds as percentages of SLA elapsed
SLA_ALERT_THRESHOLDS = [0.50, 0.75, 0.90, 1.00]


def _is_business_hour(dt: datetime) -> bool:
    """Returns True if dt falls within Oman business hours."""
    local = dt + timedelta(hours=OMAN_UTC_OFFSET)
    if local.weekday() not in OMAN_WORK_DAYS:
        return False
    if local.date() in OMAN_PUBLIC_HOLIDAYS:
        return False
    return OMAN_WORK_START <= local.hour < OMAN_WORK_END


def _add_business_hours(start: datetime, hours: float) -> datetime:
    """Advance start by N business hours, skipping weekends and public holidays."""
    remaining = hours
    current = start.replace(tzinfo=timezone.utc) if start.tzinfo is None else start

    while remaining > 0:
        if _is_business_hour(current):
            remaining -= 1 / 60  # advance by 1 minute at a time
            current += timedelta(minutes=1)
        else:
            current += timedelta(minutes=1)

    return current


class SLAService:
    """FR-007 — SLA deadline calculation with Oman business calendar."""

    def calculate_deadlines(
        self,
        severity: str,
        received_at: datetime,
    ) -> dict[str, str]:
        """Calculate acknowledgment and resolution deadlines for a complaint.

        Args:
            severity: Complaint severity level (critical/high/medium/low)
            received_at: The datetime the complaint was received

        Returns:
            Dict with 'acknowledgment_deadline' and 'resolution_deadline' as ISO strings
        """
        sev_key = severity.lower() if severity else "medium"
        ack_hours, res_hours = SLA_TABLE.get(sev_key, SLA_TABLE["medium"])

        start = received_at
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)

        ack_deadline = _add_business_hours(start, ack_hours)
        res_deadline = _add_business_hours(start, res_hours)

        return {
            "acknowledgment_deadline": ack_deadline.isoformat(),
            "resolution_deadline": res_deadline.isoformat(),
        }

    def compute_sla_status(
        self,
        severity: str,
        received_at: datetime,
        acknowledged_time: str | None = None,
        current_status: str = "submitted",
        resolution_deadline: str | None = None,
    ) -> dict[str, Any]:
        """Calculate real-time SLA status for a complaint.

        Returns:
            Dict with sla_status, time_remaining_hours, breach_probability, recommended_action
        """
        now = datetime.now(tz=timezone.utc)

        # Parse resolution deadline
        if resolution_deadline:
            try:
                deadline = datetime.fromisoformat(resolution_deadline)
                if deadline.tzinfo is None:
                    deadline = deadline.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                deadline = None
        else:
            # Compute on the fly
            deadlines = self.calculate_deadlines(severity, received_at)
            try:
                deadline = datetime.fromisoformat(deadlines["resolution_deadline"])
            except (ValueError, TypeError):
                deadline = None

        if deadline is None:
            return {
                "sla_status": "within_sla",
                "time_remaining_hours": None,
                "breach_probability": 0,
                "recommended_action": "Monitor complaint",
            }

        hours_remaining = (deadline - now).total_seconds() / 3600
        sev_key = severity.lower() if severity else "medium"
        _, total_hours = SLA_TABLE.get(sev_key, SLA_TABLE["medium"])

        if hours_remaining <= 0:
            sla_status = "breached"
            breach_probability = 100
            recommended_action = "URGENT: SLA already breached — escalate immediately"
        elif hours_remaining / total_hours <= 0.25:
            sla_status = "at_risk"
            breach_probability = min(int((1 - hours_remaining / total_hours) * 100), 99)
            recommended_action = "SLA critically at risk — assign and prioritize immediately"
        elif hours_remaining / total_hours <= 0.50:
            sla_status = "at_risk"
            breach_probability = max(int((1 - hours_remaining / total_hours) * 80), 40)
            recommended_action = "SLA at risk — review and assign owner"
        else:
            sla_status = "within_sla"
            breach_probability = max(int((1 - hours_remaining / total_hours) * 30), 0)
            recommended_action = "Monitor complaint progress"

        return {
            "sla_status": sla_status,
            "time_remaining_hours": round(max(hours_remaining, 0), 2),
            "breach_probability": breach_probability,
            "deadline_iso": deadline.isoformat(),
            "recommended_action": recommended_action,
            "pct_elapsed": round(max((1 - hours_remaining / total_hours) * 100, 0), 1),
        }

    def get_alert_thresholds_breached(
        self,
        severity: str,
        received_at: datetime,
        resolution_deadline: str | None = None,
    ) -> list[str]:
        """Returns list of threshold labels breached so far (e.g. ['50%', '75%'])."""
        status = self.compute_sla_status(severity, received_at, resolution_deadline=resolution_deadline)
        pct = status.get("pct_elapsed", 0) / 100
        breached: list[str] = []
        for threshold in SLA_ALERT_THRESHOLDS:
            if pct >= threshold:
                label = "breached" if threshold == 1.00 else f"{int(threshold * 100)}%"
                breached.append(label)
        return breached

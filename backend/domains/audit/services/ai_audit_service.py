"""AI Decision Audit Service — FR-018 (Phase 2).

Logs every AI analysis run with full input/output for compliance and traceability.
Entries are stored in the audit domain and can be queried by complaint or model.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from app.platform.logging import get_logger

logger = get_logger(__name__)


class AIAuditService:
    """FR-018: Audit logging for all AI decisions.

    Logs:
    - Input text hash (not the raw text itself for privacy)
    - Model used and prompt version
    - All output fields with confidence scores
    - Override history entries
    - Processing time
    """

    def __init__(self, audit_repository: Any | None = None) -> None:
        self._repo = audit_repository
        self._logger = get_logger(__name__)

    async def log_analysis(
        self,
        complaint_id: uuid.UUID,
        actor_id: uuid.UUID | None,
        analysis_result: dict[str, Any],
        model_used: str = "",
        processing_time_ms: float = 0.0,
    ) -> None:
        """Log a full Phase 2 AI analysis run.

        Privacy: raw text is NOT stored — only a SHA-256 hash of the input.
        """
        input_text = analysis_result.pop("_input_text", "")
        input_hash = hashlib.sha256(input_text.encode()).hexdigest() if input_text else ""

        entry = {
            "event": "ai_analysis_complete",
            "complaint_id": str(complaint_id),
            "actor_id": str(actor_id) if actor_id else "system",
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "model_used": model_used,
            "processing_time_ms": round(processing_time_ms, 1),
            "input_hash": input_hash,
            # Condensed output — avoid storing full text in audit log
            "outputs": {
                "detection_type": analysis_result.get("detection_type"),
                "detection_confidence": analysis_result.get("detection_confidence"),
                "sentiment": analysis_result.get("sentiment"),
                "sentiment_trend": analysis_result.get("sentiment_trend"),
                "theme": analysis_result.get("theme"),
                "severity": analysis_result.get("severity"),
                "severity_score": analysis_result.get("severity_score"),
                "escalation_risk_score": analysis_result.get("escalation_risk_score"),
                "escalation_risk_level": analysis_result.get("escalation_risk_level"),
                "sla_risk": analysis_result.get("sla_risk"),
                "sla_breach_probability": analysis_result.get("sla_breach_probability"),
                "root_cause_category": analysis_result.get("root_cause_category"),
                "detected_language": analysis_result.get("detected_language"),
                "is_repeat": analysis_result.get("is_repeat"),
            },
        }

        await self._write_entry(
            complaint_id=complaint_id,
            actor_id=actor_id,
            action="ai_analysis",
            resource_type="complaint",
            details=entry,
        )

    async def log_override(
        self,
        complaint_id: uuid.UUID,
        actor_id: uuid.UUID | None,
        override_fields: dict[str, Any],
        override_reason: str,
    ) -> None:
        """Log a human override of AI classification (FR-014)."""
        entry = {
            "event": "ai_override_applied",
            "complaint_id": str(complaint_id),
            "actor_id": str(actor_id) if actor_id else "unknown",
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "override_reason": override_reason,
            "overridden_fields": list(override_fields.keys()),
            "changes": override_fields,
        }

        await self._write_entry(
            complaint_id=complaint_id,
            actor_id=actor_id,
            action="ai_override",
            resource_type="complaint",
            details=entry,
        )

    async def log_alert_dispatched(
        self,
        complaint_id: uuid.UUID,
        alert_type: str,
        alert_metadata: dict[str, Any],
    ) -> None:
        """Log an FR-013 alert dispatch."""
        entry = {
            "event": "alert_dispatched",
            "complaint_id": str(complaint_id),
            "alert_type": alert_type,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            **alert_metadata,
        }

        await self._write_entry(
            complaint_id=complaint_id,
            actor_id=None,
            action=f"alert_{alert_type}",
            resource_type="notification",
            details=entry,
        )

    # -----------------------------------------------------------------------
    # Internal write
    # -----------------------------------------------------------------------
    async def _write_entry(
        self,
        complaint_id: uuid.UUID,
        actor_id: uuid.UUID | None,
        action: str,
        resource_type: str,
        details: dict[str, Any],
    ) -> None:
        if self._repo is None:
            # Structured log fallback when repo not available
            self._logger.info(
                "audit_entry",
                action=action,
                resource_type=resource_type,
                complaint_id=str(complaint_id),
                details_json=json.dumps(details, default=str),
            )
            return

        try:
            await self._repo.create(
                actor_id=actor_id or uuid.UUID(int=0),
                action=action,
                resource_type=resource_type,
                resource_id=str(complaint_id),
                details=details,
            )
        except Exception as exc:
            self._logger.error(
                "audit_write_failed",
                action=action,
                complaint_id=str(complaint_id),
                error=str(exc),
            )

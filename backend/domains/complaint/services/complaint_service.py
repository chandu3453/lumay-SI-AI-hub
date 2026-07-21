"""Complaint domain service — Phase 2 business orchestration layer.

Phase 2 additions:
- trigger_ai_analysis()   : FR-010 background AI analysis on complaint create
- run_ai_analysis()       : FR-010 synchronous on-demand AI analysis
- apply_ai_override()     : FR-014 human override with audit trail
- list_complaints()       : Extended with Phase 2 filters
"""

import uuid
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any

from domains.complaint.constants.complaint_constants import (
    ComplaintCategory,
    ComplaintPriority,
    ComplaintSeverity,
    ComplaintStatus,
)
from domains.complaint.events.complaint_events import (
    ComplaintArchivedEvent,
    ComplaintAssignedEvent,
    ComplaintClosedEvent,
    ComplaintCreatedEvent,
    ComplaintEscalatedEvent,
    ComplaintResolvedEvent,
    ComplaintUpdatedEvent,
    DomainEvent,
)
from domains.complaint.exceptions.complaint_exceptions import (
    ComplaintNotFoundError,
    ComplaintValidationError,
)
from domains.complaint.models.complaint import Complaint
from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.complaint.schemas.complaint_schemas import (
    AIOverrideRequest,
    ComplaintCreate,
    ComplaintUpdate,
)
from domains.complaint.services.sla_service import SLAService
from domains.customer.repositories.customer_repository import CustomerRepository
from domains.interaction.repositories.interaction_repository import InteractionRepository
from app.platform.logging import get_logger
from shared.base_service import BaseService

_ALLOWED_TRANSITIONS: dict[ComplaintStatus, set[ComplaintStatus]] = {
    ComplaintStatus.SUBMITTED: {
        ComplaintStatus.UNDER_REVIEW,
        ComplaintStatus.ESCALATED,
        ComplaintStatus.RESOLVED,
        ComplaintStatus.CLOSED,
        ComplaintStatus.ARCHIVED,
    },
    ComplaintStatus.UNDER_REVIEW: {
        ComplaintStatus.INVESTIGATING,
        ComplaintStatus.ESCALATED,
        ComplaintStatus.RESOLVED,
        ComplaintStatus.CLOSED,
        ComplaintStatus.ARCHIVED,
    },
    ComplaintStatus.INVESTIGATING: {
        ComplaintStatus.ESCALATED,
        ComplaintStatus.RESOLVED,
        ComplaintStatus.CLOSED,
        ComplaintStatus.ARCHIVED,
    },
    ComplaintStatus.ESCALATED: {
        ComplaintStatus.INVESTIGATING,
        ComplaintStatus.RESOLVED,
        ComplaintStatus.CLOSED,
        ComplaintStatus.ARCHIVED,
    },
    ComplaintStatus.RESOLVED: {
        ComplaintStatus.CLOSED,
        ComplaintStatus.ARCHIVED,
    },
    ComplaintStatus.CLOSED: set(),
    ComplaintStatus.ARCHIVED: set(),
}

_IMMUTABLE_STATUSES = {
    ComplaintStatus.CLOSED,
    ComplaintStatus.ARCHIVED,
}


class ComplaintService(BaseService):
    def __init__(
        self,
        repository: ComplaintRepository,
        customer_repository: CustomerRepository,
        interaction_repository: InteractionRepository,
    ) -> None:
        self._repository = repository
        self._customer_repository = customer_repository
        self._interaction_repository = interaction_repository
        self._logger = get_logger(__name__)
        self._sla_service = SLAService()

    # -----------------------------------------------------------------------
    # Core CRUD
    # -----------------------------------------------------------------------
    async def create_complaint(
        self, data: ComplaintCreate
    ) -> tuple[Complaint, list[DomainEvent]]:
        self._logger.info("complaint_create_requested", title=data.title)

        if data.customer_id:
            customer = await self._customer_repository.get_by_id(data.customer_id)
            if customer is None:
                raise ComplaintValidationError(
                    message="Referenced customer not found.",
                    context={"customer_id": str(data.customer_id)},
                )

        if data.interaction_id:
            interaction = await self._interaction_repository.get_by_id(data.interaction_id)
            if interaction is None:
                raise ComplaintValidationError(
                    message="Referenced interaction not found.",
                    context={"interaction_id": str(data.interaction_id)},
                )

        complaint = await self._repository.create(**data.model_dump())

        # FR-007: Calculate SLA deadlines immediately on creation
        try:
            sla_deadlines = self._sla_service.calculate_deadlines(
                severity=str(complaint.severity),
                received_at=complaint.created_at,
            )
            await self._repository.update(complaint.id, **sla_deadlines)
        except Exception as exc:
            self._logger.warning("sla_deadline_calculation_failed", complaint_id=str(complaint.id), error=str(exc))

        events: list[DomainEvent] = [
            ComplaintCreatedEvent(
                complaint_id=complaint.id,
                customer_id=data.customer_id,
                category=complaint.category,
            )
        ]
        self._logger.info(
            "complaint_created",
            complaint_id=str(complaint.id),
            category=complaint.category,
        )
        return complaint, events

    async def get_complaint(self, complaint_id: uuid.UUID) -> Complaint:
        complaint = await self._repository.get_by_id(complaint_id)
        if complaint is None:
            raise ComplaintNotFoundError(context={"complaint_id": str(complaint_id)})
        return complaint

    async def list_complaints(
        self,
        *,
        customer_id: uuid.UUID | None = None,
        status: ComplaintStatus | None = None,
        category: ComplaintCategory | None = None,
        priority: ComplaintPriority | None = None,
        severity: ComplaintSeverity | None = None,
        # Phase 2 filters
        theme: str | None = None,
        sla_risk: str | None = None,
        is_repeat: bool | None = None,
        detected_language: str | None = None,
        escalation_risk_min: int | None = None,
        product: str | None = None,
        channel: str | None = None,
        regulatory_flag: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[Complaint], int]:
        self._logger.debug(
            "complaint_list_requested",
            customer_id=str(customer_id) if customer_id else None,
            status=status,
            category=category,
            priority=priority,
            severity=severity,
            page=page,
            page_size=page_size,
        )
        return await self._repository.list(
            customer_id=customer_id,
            status=status,
            category=category,
            priority=priority,
            severity=severity,
            theme=theme,
            sla_risk=sla_risk,
            is_repeat=is_repeat,
            detected_language=detected_language,
            escalation_risk_min=escalation_risk_min,
            product=product,
            channel=channel,
            regulatory_flag=regulatory_flag,
            page=page,
            page_size=page_size,
        )

    async def update_complaint(
        self, complaint_id: uuid.UUID, data: ComplaintUpdate
    ) -> tuple[Complaint, list[DomainEvent]]:
        complaint = await self.get_complaint(complaint_id)
        self._assert_mutable(complaint)

        new_status = data.status
        if new_status is not None and new_status != complaint.status:
            self._validate_transition(complaint.status, new_status)

        updated = await self._repository.update(
            complaint_id, **data.model_dump(exclude_none=True)
        )
        events: list[DomainEvent] = [ComplaintUpdatedEvent(complaint_id=complaint.id)]
        self._logger.info("complaint_updated", complaint_id=str(complaint_id))
        return updated, events

    # -----------------------------------------------------------------------
    # FR-010 — AI Analysis Trigger
    # -----------------------------------------------------------------------
    async def trigger_ai_analysis(self, complaint_id: uuid.UUID) -> None:
        """Background task: run full Phase 2 AI analysis and persist results."""
        try:
            await self.run_ai_analysis(complaint_id)
        except Exception as exc:
            self._logger.error(
                "ai_analysis_background_failed",
                complaint_id=str(complaint_id),
                error=str(exc),
            )

    async def run_ai_analysis(self, complaint_id: uuid.UUID) -> Complaint:
        """FR-010: Run full Phase 2 AI analysis pipeline and persist all results."""
        complaint = await self.get_complaint(complaint_id)

        # Build analysis text from title + description
        text_parts = [complaint.title]
        if complaint.description:
            text_parts.append(complaint.description)
        analysis_text = " ".join(text_parts)

        if not analysis_text.strip():
            self._logger.warning("ai_analysis_skipped_empty_text", complaint_id=str(complaint_id))
            return complaint

        try:
            from ai.intelligence.service import ComplaintIntelligenceService
            ai_service = ComplaintIntelligenceService()
            analysis = await ai_service.analyze_complete(analysis_text)

            # Build per-field explanations for FR-020
            ai_explanation = {
                "detection": analysis.detection.explanation,
                "sentiment": analysis.sentiment.explanation,
                "theme": analysis.themes.explanation,
                "severity": analysis.severity.explanation,
                "escalation": analysis.escalation.explanation,
                "priority": analysis.priority.explanation,
                "root_cause": analysis.root_cause.explanation,
            }

            # Gather all update fields
            update_fields: dict[str, Any] = {
                # FR-002
                "complaint_detected": analysis.detection.is_complaint,
                "detection_type": analysis.detection.detection_type,
                "detection_confidence": analysis.detection.confidence,
                "primary_complaint_statement": analysis.detection.primary_complaint_statement,
                # FR-003
                "sentiment": analysis.sentiment.sentiment,
                "sentiment_start": analysis.sentiment.sentiment_start,
                "sentiment_end": analysis.sentiment.sentiment_end,
                "sentiment_trend": analysis.sentiment.sentiment_trend,
                "sentiment_target": analysis.sentiment.sentiment_target,
                "sentiment_polarity": analysis.sentiment.polarity,
                "sentiment_intensity": analysis.sentiment.intensity,
                "sentiment_emotions": analysis.sentiment.emotions,
                # FR-004
                "theme": analysis.themes.primary_theme,
                "theme_secondary": analysis.themes.secondary_themes,
                "theme_keywords": analysis.themes.keywords,
                # FR-005
                "severity_score": analysis.severity.severity_score,
                "auto_escalation_triggers": analysis.severity.auto_escalation_triggers,
                # FR-006
                "escalation_risk_score": analysis.escalation.escalation_risk_score,
                "escalation_risk_level": analysis.escalation.risk_level,
                "escalation_triggers": analysis.escalation.triggers,
                # FR-007
                "sla_risk": analysis.priority.sla_risk,
                "sla_breach_probability": analysis.priority.breach_probability,
                "sla_hours_remaining": analysis.priority.sla_hours_remaining,
                "priority_score": analysis.priority.priority_score,
                # FR-016
                "root_cause": analysis.root_cause.root_cause,
                "root_cause_category": analysis.root_cause.root_cause_category,
                "contributing_factors": analysis.root_cause.contributing_factors,
                "process_failure_point": analysis.root_cause.process_failure_point,
                # FR-019
                "detected_language": analysis.language.detected_language,
                "arabic_percentage": analysis.language.arabic_percentage,
                # FR-020
                "ai_summary": analysis.summary.summary,
                "ai_explanation": ai_explanation,
                "recommendation": analysis.resolution.recommended_action,
                "routing_rule": analysis.resolution.routing_rule,
                "suggested_response_template": analysis.resolution.suggested_response_template,
            }

            # Auto-upgrade severity if critical triggers fired
            if analysis.severity.auto_escalation_triggers:
                from domains.complaint.constants.complaint_constants import ComplaintSeverity
                update_fields["severity"] = ComplaintSeverity.CRITICAL

            updated = await self._repository.update(complaint_id, **update_fields)
            self._logger.info(
                "ai_analysis_completed",
                complaint_id=str(complaint_id),
                is_complaint=analysis.detection.is_complaint,
                theme=analysis.themes.primary_theme,
                severity=analysis.severity.severity,
                escalation_risk=analysis.escalation.escalation_risk_score,
            )
            return updated

        except Exception as exc:
            self._logger.error(
                "ai_analysis_failed",
                complaint_id=str(complaint_id),
                error=str(exc),
            )
            return complaint

    # -----------------------------------------------------------------------
    # FR-007 — Acknowledge Complaint
    # -----------------------------------------------------------------------
    async def acknowledge_complaint(
        self,
        complaint_id: uuid.UUID,
        agent_id: uuid.UUID | None = None,
    ) -> tuple[Complaint, list[DomainEvent]]:
        """FR-007: Record acknowledgment time and recalculate SLA status."""
        complaint = await self.get_complaint(complaint_id)
        self._assert_mutable(complaint)

        now = datetime.now(tz=timezone.utc)
        update_fields: dict[str, Any] = {
            "acknowledged_time": now.isoformat(),
        }

        # Recalculate SLA status with acknowledgment recorded
        if complaint.created_at:
            sla_status = self._sla_service.compute_sla_status(
                severity=str(complaint.severity),
                received_at=complaint.created_at,
                acknowledged_time=now.isoformat(),
                current_status=str(complaint.status),
                resolution_deadline=complaint.resolution_deadline,
            )
            update_fields["sla_risk"] = sla_status["sla_status"]
            update_fields["sla_hours_remaining"] = sla_status.get("time_remaining_hours")
            update_fields["sla_breach_probability"] = sla_status.get("breach_probability")

        # Transition to UNDER_REVIEW if still SUBMITTED
        if complaint.status == ComplaintStatus.SUBMITTED:
            update_fields["status"] = ComplaintStatus.UNDER_REVIEW

        updated = await self._repository.update(complaint_id, **update_fields)
        events: list[DomainEvent] = [ComplaintUpdatedEvent(complaint_id=complaint.id)]
        self._logger.info("complaint_acknowledged", complaint_id=str(complaint_id))
        return updated, events

    # -----------------------------------------------------------------------
    # FR-008 — Get Related Complaints
    # -----------------------------------------------------------------------
    async def get_related_complaints(
        self,
        complaint_id: uuid.UUID,
        limit: int = 10,
    ) -> list[Complaint]:
        """FR-008: Return related/repeat complaints for the same customer."""
        complaint = await self.get_complaint(complaint_id)
        if complaint.customer_id is None:
            return []
        related = await self._repository.get_related_complaints(
            customer_id=complaint.customer_id,
            theme=complaint.theme,
            exclude_id=complaint_id,
            limit=limit,
        )
        return list(related)

    # -----------------------------------------------------------------------
    # FR-007 — Real-time SLA Status
    # -----------------------------------------------------------------------
    async def get_sla_status(
        self,
        complaint_id: uuid.UUID,
    ) -> dict[str, Any]:
        """FR-007: Compute real-time SLA status for a complaint."""
        complaint = await self.get_complaint(complaint_id)
        if complaint.created_at is None:
            return {"sla_status": "unknown", "message": "Complaint has no creation time"}
        return self._sla_service.compute_sla_status(
            severity=str(complaint.severity),
            received_at=complaint.created_at,
            acknowledged_time=complaint.acknowledged_time,
            current_status=str(complaint.status),
            resolution_deadline=complaint.resolution_deadline,
        )

    # -----------------------------------------------------------------------
    # FR-014 — Human Override (existing, keep unchanged)
    # -----------------------------------------------------------------------
    async def apply_ai_override(
        self,
        complaint_id: uuid.UUID,
        override: AIOverrideRequest,
        agent_id: uuid.UUID | None = None,
    ) -> tuple[Complaint, list[DomainEvent]]:
        """FR-014: Apply human override on AI classification fields.

        Saves original AI values in ai_override_log before overriding.
        """
        complaint = await self.get_complaint(complaint_id)
        self._assert_mutable(complaint)

        # Build override log entry
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "agent_id": str(agent_id) if agent_id else "unknown",
            "reason": override.override_reason,
            "changes": {},
        }

        update_fields: dict[str, Any] = {}

        if override.category is not None:
            log_entry["changes"]["category"] = {
                "from": complaint.category,
                "to": override.category,
            }
            update_fields["category"] = override.category

        if override.theme is not None:
            log_entry["changes"]["theme"] = {
                "from": complaint.theme,
                "to": override.theme,
            }
            update_fields["theme"] = override.theme

        if override.severity is not None:
            log_entry["changes"]["severity"] = {
                "from": complaint.severity,
                "to": override.severity,
            }
            update_fields["severity"] = override.severity

        if override.priority is not None:
            log_entry["changes"]["priority"] = {
                "from": complaint.priority,
                "to": override.priority,
            }
            update_fields["priority"] = override.priority

        if override.sentiment is not None:
            log_entry["changes"]["sentiment"] = {
                "from": complaint.sentiment,
                "to": override.sentiment,
            }
            update_fields["sentiment"] = override.sentiment

        if override.root_cause is not None:
            log_entry["changes"]["root_cause"] = {
                "from": complaint.root_cause,
                "to": override.root_cause,
            }
            update_fields["root_cause"] = override.root_cause

        if override.root_cause_category is not None:
            log_entry["changes"]["root_cause_category"] = {
                "from": complaint.root_cause_category,
                "to": override.root_cause_category,
            }
            update_fields["root_cause_category"] = override.root_cause_category

        # Append to override log
        existing_log = complaint.ai_override_log or []
        update_fields["ai_override_log"] = [*existing_log, log_entry]

        updated = await self._repository.update(complaint_id, **update_fields)
        events: list[DomainEvent] = [ComplaintUpdatedEvent(complaint_id=complaint.id)]

        self._logger.info(
            "ai_override_applied",
            complaint_id=str(complaint_id),
            agent_id=str(agent_id),
            changed_fields=list(log_entry["changes"].keys()),
        )
        return updated, events

    # -----------------------------------------------------------------------
    # Lifecycle methods (unchanged)
    # -----------------------------------------------------------------------
    async def assign_complaint(
        self,
        complaint_id: uuid.UUID,
        agent_id: uuid.UUID,
        queue: str | None = None,
    ) -> tuple[Complaint, list[DomainEvent]]:
        complaint = await self.get_complaint(complaint_id)
        self._assert_mutable(complaint)

        kwargs: dict = {"assigned_agent_id": agent_id}
        if queue is not None:
            kwargs["assigned_queue"] = queue

        updated = await self._repository.update(complaint_id, **kwargs)
        events: list[DomainEvent] = [
            ComplaintAssignedEvent(
                complaint_id=complaint.id,
                agent_id=agent_id,
                queue=queue or "",
            )
        ]
        self._logger.info("complaint_assigned", complaint_id=str(complaint_id), agent_id=str(agent_id))
        return updated, events

    async def escalate_complaint(
        self, complaint_id: uuid.UUID, reason: str = ""
    ) -> tuple[Complaint, list[DomainEvent]]:
        complaint = await self.get_complaint(complaint_id)
        self._assert_mutable(complaint)
        self._validate_transition(complaint.status, ComplaintStatus.ESCALATED)

        updated = await self._repository.update(complaint_id, status=ComplaintStatus.ESCALATED)
        events: list[DomainEvent] = [
            ComplaintEscalatedEvent(complaint_id=complaint.id, reason=reason)
        ]
        self._logger.info("complaint_escalated", complaint_id=str(complaint_id))
        return updated, events

    async def resolve_complaint(
        self, complaint_id: uuid.UUID, resolution_summary: str = ""
    ) -> tuple[Complaint, list[DomainEvent]]:
        complaint = await self.get_complaint(complaint_id)
        self._assert_mutable(complaint)
        self._validate_transition(complaint.status, ComplaintStatus.RESOLVED)

        updated = await self._repository.update(
            complaint_id,
            status=ComplaintStatus.RESOLVED,
            resolution_summary=resolution_summary or None,
        )
        events: list[DomainEvent] = [
            ComplaintResolvedEvent(
                complaint_id=complaint.id,
                resolution_summary=resolution_summary,
            )
        ]
        self._logger.info("complaint_resolved", complaint_id=str(complaint_id))
        return updated, events

    async def close_complaint(
        self, complaint_id: uuid.UUID, closure_reason: str = ""
    ) -> tuple[Complaint, list[DomainEvent]]:
        complaint = await self.get_complaint(complaint_id)

        if complaint.status == ComplaintStatus.CLOSED:
            raise ComplaintValidationError(
                message="Complaint is already closed.",
                context={"complaint_id": str(complaint_id)},
            )

        self._validate_transition(complaint.status, ComplaintStatus.CLOSED)

        updated = await self._repository.update(
            complaint_id,
            status=ComplaintStatus.CLOSED,
            closure_reason=closure_reason or None,
        )
        events: list[DomainEvent] = [
            ComplaintClosedEvent(
                complaint_id=complaint.id,
                closure_reason=closure_reason,
            )
        ]
        self._logger.info("complaint_closed", complaint_id=str(complaint_id))
        return updated, events

    async def archive_complaint(
        self, complaint_id: uuid.UUID
    ) -> tuple[Complaint, list[DomainEvent]]:
        complaint = await self.get_complaint(complaint_id)

        if complaint.status == ComplaintStatus.ARCHIVED:
            raise ComplaintValidationError(
                message="Complaint is already archived.",
                context={"complaint_id": str(complaint_id)},
            )

        self._validate_transition(complaint.status, ComplaintStatus.ARCHIVED)

        updated = await self._repository.update(complaint_id, status=ComplaintStatus.ARCHIVED)
        events: list[DomainEvent] = [ComplaintArchivedEvent(complaint_id=complaint.id)]
        self._logger.info("complaint_archived", complaint_id=str(complaint_id))
        return updated, events

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------
    def _assert_mutable(self, complaint: Complaint) -> None:
        if complaint.status in _IMMUTABLE_STATUSES:
            raise ComplaintValidationError(
                message=f"Cannot modify complaint in status '{complaint.status}'.",
                context={
                    "complaint_id": str(complaint.id),
                    "current_status": complaint.status,
                },
            )

    @staticmethod
    def _validate_transition(
        current: ComplaintStatus, target: ComplaintStatus
    ) -> None:
        allowed = _ALLOWED_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise ComplaintValidationError(
                message=f"Cannot transition from '{current}' to '{target}'.",
                context={
                    "current_status": current,
                    "target_status": target,
                },
            )

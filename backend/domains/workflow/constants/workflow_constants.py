"""Workflow Domain Constants."""

from enum import StrEnum
from typing import Final


DOMAIN_NAME: Final[str] = "workflow"
EXCHANGE_NAME: Final[str] = "lumay.workflow"

CACHE_PREFIX_WORKFLOW: Final[str] = "workflow"


class WorkflowStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class WorkflowStage(StrEnum):
    INITIATED = "initiated"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    APPROVAL = "approval"
    RESOLUTION = "resolution"
    COMPLETED = "completed"


class SLAStatus(StrEnum):
    WITHIN_SLA = "within_sla"
    AT_RISK = "at_risk"
    BREACHED = "breached"


class EscalationLevel(StrEnum):
    LEVEL_0 = "level_0"
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NOT_REQUIRED = "not_required"
"""Workflow REST API — endpoints for workflow lifecycle management."""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import CurrentUser, get_current_active_user, get_current_user
from app.dependencies.workflow import get_workflow_service
from domains.workflow.constants.workflow_constants import (
    EscalationLevel,
    SLAStatus,
    WorkflowStage,
    WorkflowStatus,
)
from domains.workflow.schemas.workflow_schemas import (
    WorkflowApproveRequest,
    WorkflowAssignRequest,
    WorkflowCreate,
    WorkflowEscalateRequest,
    WorkflowRejectRequest,
    WorkflowResponse,
    WorkflowSummary,
    WorkflowTransferRequest,
    WorkflowUpdate,
)
from domains.workflow.services.workflow_service import WorkflowService
from app.platform.logging import get_logger
from shared.response_schemas import PaginatedResponse, SuccessResponse

router = APIRouter(prefix="/workflows", tags=["Workflows"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=SuccessResponse[WorkflowResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a workflow",
    description="Creates a new workflow for a complaint. Only one active workflow per complaint is allowed.",
)
async def create_workflow(
    body: WorkflowCreate,
    service: WorkflowService = Depends(get_workflow_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[WorkflowResponse]:
    workflow, _ = await service.create_workflow(body)
    return SuccessResponse(data=WorkflowResponse.model_validate(workflow))


@router.get(
    "",
    response_model=PaginatedResponse[WorkflowSummary],
    summary="List workflows",
    description="Returns a paginated list of workflows with optional filters.",
)
async def list_workflows(
    workflow_status: WorkflowStatus | None = Query(
        None, description="Filter by workflow status"
    ),
    workflow_stage: WorkflowStage | None = Query(
        None, description="Filter by workflow stage"
    ),
    assigned_team: str | None = Query(
        None, description="Filter by assigned team"
    ),
    sla_status: SLAStatus | None = Query(
        None, description="Filter by SLA status"
    ),
    escalation_level: EscalationLevel | None = Query(
        None, description="Filter by escalation level"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        20, ge=1, le=100, description="Items per page"
    ),
    service: WorkflowService = Depends(get_workflow_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> PaginatedResponse[WorkflowSummary]:
    items, total = await service.list_workflows(
        workflow_status=workflow_status,
        workflow_stage=workflow_stage,
        assigned_team=assigned_team,
        sla_status=sla_status,
        escalation_level=escalation_level,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        data=[WorkflowSummary.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get(
    "/{workflow_id}",
    response_model=SuccessResponse[WorkflowResponse],
    summary="Get workflow by ID",
    description="Returns a single workflow by its unique identifier.",
)
async def get_workflow(
    workflow_id: uuid.UUID,
    service: WorkflowService = Depends(get_workflow_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[WorkflowResponse]:
    workflow = await service.get_workflow(workflow_id)
    return SuccessResponse(data=WorkflowResponse.model_validate(workflow))


@router.patch(
    "/{workflow_id}",
    response_model=SuccessResponse[WorkflowResponse],
    summary="Update a workflow",
    description="Updates an existing workflow. Terminal-status workflows are read-only.",
)
async def update_workflow(
    workflow_id: uuid.UUID,
    body: WorkflowUpdate,
    service: WorkflowService = Depends(get_workflow_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[WorkflowResponse]:
    workflow, _ = await service.update_workflow(workflow_id, body)

    from domains.conversation.integration_hooks import on_workflow_lifecycle

    # WorkflowService.update_workflow returns no DomainEvent today — the hook
    # still fires with a synthetic event_type so the timeline doesn't drop it.
    await on_workflow_lifecycle(service._repository._session, workflow, "workflow.updated")

    return SuccessResponse(data=WorkflowResponse.model_validate(workflow))


@router.post(
    "/{workflow_id}/assign",
    response_model=SuccessResponse[WorkflowResponse],
    summary="Assign a workflow",
    description="Assigns a workflow to an agent, optionally specifying team and queue.",
)
async def assign_workflow(
    workflow_id: uuid.UUID,
    body: WorkflowAssignRequest,
    service: WorkflowService = Depends(get_workflow_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[WorkflowResponse]:
    workflow, _ = await service.assign_workflow(
        workflow_id,
        agent_id=body.agent_id,
        team=body.team,
        queue=body.queue,
    )

    from domains.conversation.integration_hooks import on_workflow_lifecycle

    await on_workflow_lifecycle(
        service._repository._session,
        workflow,
        "workflow.assigned",
        {"assigned_team": body.team, "queue": body.queue},
        assigned_agent_id=body.agent_id,
    )

    return SuccessResponse(data=WorkflowResponse.model_validate(workflow))


@router.post(
    "/{workflow_id}/transfer",
    response_model=SuccessResponse[WorkflowResponse],
    summary="Transfer a workflow",
    description="Transfers a workflow from the current assignee to a new agent.",
)
async def transfer_workflow(
    workflow_id: uuid.UUID,
    body: WorkflowTransferRequest,
    service: WorkflowService = Depends(get_workflow_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[WorkflowResponse]:
    workflow, _ = await service.transfer_workflow(
        workflow_id,
        agent_id=body.agent_id,
        team=body.team,
        queue=body.queue,
    )

    from domains.conversation.integration_hooks import on_workflow_lifecycle

    # transfer_workflow reuses WorkflowAssigned (no dedicated event class) —
    # the hook uses its own "workflow.transferred" string so the timeline can
    # still tell assignment and transfer apart.
    await on_workflow_lifecycle(
        service._repository._session,
        workflow,
        "workflow.transferred",
        {"assigned_team": body.team, "queue": body.queue},
        assigned_agent_id=body.agent_id,
    )

    return SuccessResponse(data=WorkflowResponse.model_validate(workflow))


@router.post(
    "/{workflow_id}/escalate",
    response_model=SuccessResponse[WorkflowResponse],
    summary="Escalate a workflow",
    description="Increments the escalation level. Levels cannot decrease.",
)
async def escalate_workflow(
    workflow_id: uuid.UUID,
    body: WorkflowEscalateRequest | None = None,
    service: WorkflowService = Depends(get_workflow_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[WorkflowResponse]:
    workflow, _ = await service.escalate_workflow(
        workflow_id, reason=body.reason if body else ""
    )

    from domains.conversation.integration_hooks import on_workflow_lifecycle

    await on_workflow_lifecycle(
        service._repository._session,
        workflow,
        "workflow.escalated",
        {"reason": body.reason if body else "", "escalation_level": str(workflow.escalation_level)},
    )

    return SuccessResponse(data=WorkflowResponse.model_validate(workflow))


@router.post(
    "/{workflow_id}/approve",
    response_model=SuccessResponse[WorkflowResponse],
    summary="Approve a workflow",
    description="Sets the workflow approval status to APPROVED.",
)
async def approve_workflow(
    workflow_id: uuid.UUID,
    body: WorkflowApproveRequest,
    service: WorkflowService = Depends(get_workflow_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[WorkflowResponse]:
    workflow, _ = await service.approve_workflow(
        workflow_id, approved_by=body.approved_by
    )

    from domains.conversation.integration_hooks import on_workflow_lifecycle

    await on_workflow_lifecycle(service._repository._session, workflow, "workflow.approved")

    return SuccessResponse(data=WorkflowResponse.model_validate(workflow))


@router.post(
    "/{workflow_id}/reject",
    response_model=SuccessResponse[WorkflowResponse],
    summary="Reject a workflow",
    description="Sets the workflow approval status to REJECTED and returns to review stage.",
)
async def reject_workflow(
    workflow_id: uuid.UUID,
    body: WorkflowRejectRequest,
    service: WorkflowService = Depends(get_workflow_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[WorkflowResponse]:
    workflow, _ = await service.reject_workflow(
        workflow_id, rejected_by=body.rejected_by, reason=body.reason
    )

    from domains.conversation.integration_hooks import on_workflow_lifecycle

    await on_workflow_lifecycle(
        service._repository._session, workflow, "workflow.rejected", {"reason": body.reason}
    )

    return SuccessResponse(data=WorkflowResponse.model_validate(workflow))


@router.post(
    "/{workflow_id}/complete",
    response_model=SuccessResponse[WorkflowResponse],
    summary="Complete a workflow",
    description="Completes the workflow. Requires approval to be APPROVED or NOT_REQUIRED.",
)
async def complete_workflow(
    workflow_id: uuid.UUID,
    service: WorkflowService = Depends(get_workflow_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[WorkflowResponse]:
    workflow, _ = await service.complete_workflow(workflow_id)

    from domains.conversation.integration_hooks import on_workflow_lifecycle

    await on_workflow_lifecycle(service._repository._session, workflow, "workflow.completed")

    return SuccessResponse(data=WorkflowResponse.model_validate(workflow))


@router.post(
    "/{workflow_id}/archive",
    response_model=SuccessResponse[WorkflowResponse],
    summary="Archive a workflow",
    description="Archives a completed workflow. Archived workflows are read-only.",
)
async def archive_workflow(
    workflow_id: uuid.UUID,
    service: WorkflowService = Depends(get_workflow_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[WorkflowResponse]:
    workflow, _ = await service.archive_workflow(workflow_id)

    from domains.conversation.integration_hooks import on_workflow_lifecycle

    await on_workflow_lifecycle(service._repository._session, workflow, "workflow.archived")

    return SuccessResponse(data=WorkflowResponse.model_validate(workflow))
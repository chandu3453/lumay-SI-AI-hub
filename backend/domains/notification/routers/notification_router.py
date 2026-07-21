"""Notification REST API — endpoints for notification lifecycle management."""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import CurrentUser, get_current_active_user, get_current_user
from app.dependencies.notification import get_notification_service
from domains.notification.constants.notification_constants import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)
from domains.notification.schemas.notification_schemas import (
    NotificationCreate,
    NotificationDeliverRequest,
    NotificationFailRequest,
    NotificationQueueRequest,
    NotificationResponse,
    NotificationRetryRequest,
    NotificationSendRequest,
    NotificationSummary,
    NotificationUpdate,
)
from domains.notification.services.notification_service import NotificationService
from app.platform.logging import get_logger
from shared.response_schemas import PaginatedResponse, SuccessResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=SuccessResponse[NotificationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a notification",
    description="Creates a new notification. Workflow reference is optional.",
)
async def create_notification(
    body: NotificationCreate,
    service: NotificationService = Depends(get_notification_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[NotificationResponse]:
    notification, _ = await service.create_notification(body)

    from domains.conversation.integration_hooks import on_notification_recorded

    await on_notification_recorded(service._repository._session, notification)

    return SuccessResponse(data=NotificationResponse.model_validate(notification))


@router.get(
    "",
    response_model=PaginatedResponse[NotificationSummary],
    summary="List notifications",
    description="Returns a paginated list of notifications with optional filters.",
)
async def list_notifications(
    notification_status: NotificationStatus | None = Query(
        None, description="Filter by status"
    ),
    notification_type: NotificationType | None = Query(
        None, description="Filter by notification type"
    ),
    notification_channel: NotificationChannel | None = Query(
        None, description="Filter by channel"
    ),
    priority: NotificationPriority | None = Query(
        None, description="Filter by priority"
    ),
    workflow_id: uuid.UUID | None = Query(
        None, description="Filter by workflow ID"
    ),
    complaint_id: uuid.UUID | None = Query(
        None, description="Filter by complaint ID"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        20, ge=1, le=100, description="Items per page"
    ),
    service: NotificationService = Depends(get_notification_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> PaginatedResponse[NotificationSummary]:
    items, total = await service.list_notifications(
        notification_status=notification_status,
        notification_type=notification_type,
        notification_channel=notification_channel,
        priority=priority,
        workflow_id=workflow_id,
        complaint_id=complaint_id,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        data=[NotificationSummary.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get(
    "/{notification_id}",
    response_model=SuccessResponse[NotificationResponse],
    summary="Get notification by ID",
    description="Returns a single notification by its unique identifier.",
)
async def get_notification(
    notification_id: uuid.UUID,
    service: NotificationService = Depends(get_notification_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[NotificationResponse]:
    notification = await service.get_notification(notification_id)
    return SuccessResponse(data=NotificationResponse.model_validate(notification))


@router.patch(
    "/{notification_id}",
    response_model=SuccessResponse[NotificationResponse],
    summary="Update a notification",
    description="Updates an existing notification. Archived notifications are read-only.",
)
async def update_notification(
    notification_id: uuid.UUID,
    body: NotificationUpdate,
    service: NotificationService = Depends(get_notification_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[NotificationResponse]:
    notification, _ = await service.update_notification(notification_id, body)
    return SuccessResponse(data=NotificationResponse.model_validate(notification))


@router.post(
    "/{notification_id}/queue",
    response_model=SuccessResponse[NotificationResponse],
    summary="Queue a notification",
    description="Transitions a notification to QUEUED status.",
)
async def queue_notification(
    notification_id: uuid.UUID,
    body: NotificationQueueRequest | None = None,
    service: NotificationService = Depends(get_notification_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[NotificationResponse]:
    notification, _ = await service.queue_notification(
        notification_id, scheduled_at=body.scheduled_at if body else None
    )
    return SuccessResponse(data=NotificationResponse.model_validate(notification))


@router.post(
    "/{notification_id}/send",
    response_model=SuccessResponse[NotificationResponse],
    summary="Send a notification",
    description="Transitions a notification through SENDING to SENT status.",
)
async def send_notification(
    notification_id: uuid.UUID,
    body: NotificationSendRequest | None = None,
    service: NotificationService = Depends(get_notification_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[NotificationResponse]:
    notification, _ = await service.send_notification(
        notification_id, provider=body.provider if body else "default"
    )
    return SuccessResponse(data=NotificationResponse.model_validate(notification))


@router.post(
    "/{notification_id}/retry",
    response_model=SuccessResponse[NotificationResponse],
    summary="Retry a failed notification",
    description="Retries a failed notification. Validates max retry count.",
)
async def retry_notification(
    notification_id: uuid.UUID,
    body: NotificationRetryRequest | None = None,
    service: NotificationService = Depends(get_notification_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[NotificationResponse]:
    notification, _ = await service.retry_notification(
        notification_id, scheduled_at=body.scheduled_at if body else None
    )
    return SuccessResponse(data=NotificationResponse.model_validate(notification))


@router.post(
    "/{notification_id}/deliver",
    response_model=SuccessResponse[NotificationResponse],
    summary="Mark notification as delivered",
    description="Transitions a notification to DELIVERED status.",
)
async def mark_delivered(
    notification_id: uuid.UUID,
    body: NotificationDeliverRequest | None = None,
    service: NotificationService = Depends(get_notification_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[NotificationResponse]:
    notification, _ = await service.mark_delivered(
        notification_id, delivered_at=body.delivered_at if body else None
    )
    return SuccessResponse(data=NotificationResponse.model_validate(notification))


@router.post(
    "/{notification_id}/fail",
    response_model=SuccessResponse[NotificationResponse],
    summary="Mark notification as failed",
    description="Transitions a notification to FAILED status with a reason.",
)
async def mark_failed(
    notification_id: uuid.UUID,
    body: NotificationFailRequest,
    service: NotificationService = Depends(get_notification_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[NotificationResponse]:
    notification, _ = await service.mark_failed(
        notification_id, reason=body.reason
    )
    return SuccessResponse(data=NotificationResponse.model_validate(notification))


@router.post(
    "/{notification_id}/archive",
    response_model=SuccessResponse[NotificationResponse],
    summary="Archive a notification",
    description="Archives a notification. Archived notifications are read-only.",
)
async def archive_notification(
    notification_id: uuid.UUID,
    service: NotificationService = Depends(get_notification_service),
    _current_user: CurrentUser = Depends(get_current_active_user),
) -> SuccessResponse[NotificationResponse]:
    notification, _ = await service.archive_notification(notification_id)
    return SuccessResponse(data=NotificationResponse.model_validate(notification))
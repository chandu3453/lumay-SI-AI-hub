"""Notification domain dependency injection."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from domains.workflow.repositories.workflow_repository import WorkflowRepository
from domains.notification.repositories.notification_repository import NotificationRepository
from domains.notification.services.notification_service import NotificationService


async def get_notification_repository(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[NotificationRepository, None]:
    yield NotificationRepository(session=db)


async def get_notification_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[NotificationService, None]:
    notification_repo = NotificationRepository(session=db)
    workflow_repo = WorkflowRepository(session=db)
    yield NotificationService(
        repository=notification_repo,
        workflow_repository=workflow_repo,
    )
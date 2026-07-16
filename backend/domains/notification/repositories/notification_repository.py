"""Notification Repository — Notification domain."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.platform.database.repository import BaseRepository
from domains.notification.constants.notification_constants import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)
from domains.notification.models.notification import Notification


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Notification, session)

    async def create(self, **kwargs) -> Notification:
        entity = Notification(**kwargs)
        return await self.add(entity)

    async def update(
        self, notification_id: uuid.UUID, **kwargs
    ) -> Notification | None:
        entity = await self.get_by_id(notification_id)
        if entity is None:
            return None
        for key, value in kwargs.items():
            if value is not None:
                setattr(entity, key, value)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def list(
        self,
        *,
        notification_status: NotificationStatus | None = None,
        notification_type: NotificationType | None = None,
        notification_channel: NotificationChannel | None = None,
        priority: NotificationPriority | None = None,
        workflow_id: uuid.UUID | None = None,
        complaint_id: uuid.UUID | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[Notification], int]:
        query = select(Notification)
        count_query = select(func.count(Notification.id))

        if notification_status is not None:
            query = query.where(Notification.notification_status == notification_status)
            count_query = count_query.where(Notification.notification_status == notification_status)
        if notification_type is not None:
            query = query.where(Notification.notification_type == notification_type)
            count_query = count_query.where(Notification.notification_type == notification_type)
        if notification_channel is not None:
            query = query.where(Notification.notification_channel == notification_channel)
            count_query = count_query.where(Notification.notification_channel == notification_channel)
        if priority is not None:
            query = query.where(Notification.priority == priority)
            count_query = count_query.where(Notification.priority == priority)
        if workflow_id is not None:
            query = query.where(Notification.workflow_id == workflow_id)
            count_query = count_query.where(Notification.workflow_id == workflow_id)
        if complaint_id is not None:
            query = query.where(Notification.complaint_id == complaint_id)
            count_query = count_query.where(Notification.complaint_id == complaint_id)

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        query = query.order_by(Notification.created_at.desc())
        query = query.offset(offset).limit(page_size)

        result = await self._session.execute(query)
        items = result.scalars().all()

        return items, total

    async def delete(self, notification_id: uuid.UUID) -> bool:
        entity = await self.get_by_id(notification_id)
        if entity is None:
            return False
        await self._session.delete(entity)
        await self._session.flush()
        return True

    async def get_by_workflow_id(
        self, workflow_id: uuid.UUID
    ) -> Sequence[Notification]:
        result = await self._session.execute(
            select(Notification).where(Notification.workflow_id == workflow_id)
        )
        return result.scalars().all()

    async def get_by_complaint_id(
        self, complaint_id: uuid.UUID
    ) -> Sequence[Notification]:
        result = await self._session.execute(
            select(Notification).where(Notification.complaint_id == complaint_id)
        )
        return result.scalars().all()
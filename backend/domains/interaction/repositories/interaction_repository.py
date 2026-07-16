"""Interaction repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.interaction.constants.interaction_constants import (
    InteractionChannel,
    InteractionDirection,
    InteractionStatus,
)
from domains.interaction.models.interaction import Interaction
from app.platform.database.repository import BaseRepository


class InteractionRepository(BaseRepository[Interaction]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Interaction, session)

    async def create(self, **kwargs) -> Interaction:
        entity = Interaction(**kwargs)
        return await self.add(entity)

    async def update(
        self, interaction_id: uuid.UUID, **kwargs
    ) -> Interaction | None:
        entity = await self.get_by_id(interaction_id)
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
        channel: InteractionChannel | None = None,
        status: InteractionStatus | None = None,
        direction: InteractionDirection | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[Interaction], int]:
        query = select(Interaction)
        count_query = select(func.count(Interaction.id))

        if channel is not None:
            query = query.where(Interaction.channel == channel)
            count_query = count_query.where(Interaction.channel == channel)
        if status is not None:
            query = query.where(Interaction.status == status)
            count_query = count_query.where(Interaction.status == status)
        if direction is not None:
            query = query.where(Interaction.direction == direction)
            count_query = count_query.where(Interaction.direction == direction)

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        query = query.order_by(Interaction.created_at.desc())
        query = query.offset(offset).limit(page_size)

        result = await self._session.execute(query)
        items = result.scalars().all()

        return items, total

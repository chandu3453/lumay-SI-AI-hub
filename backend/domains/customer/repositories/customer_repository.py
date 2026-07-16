"""Customer Repository — Customer domain."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domains.customer.constants.customer_constants import (
    CommunicationChannel,
    CustomerStatus,
    CustomerType,
)
from domains.customer.models.customer import Customer
from app.platform.database.repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Customer, session)

    async def create(self, **kwargs) -> Customer:
        entity = Customer(**kwargs)
        return await self.add(entity)

    async def get_by_external_ref(self, external_ref: str) -> Customer | None:
        result = await self._session.execute(
            select(Customer).where(
                Customer.external_ref == external_ref,
                Customer.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Customer | None:
        result = await self._session.execute(
            select(Customer).where(
                Customer.email == email,
                Customer.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self, customer_id: uuid.UUID, **kwargs
    ) -> Customer | None:
        entity = await self.get_by_id(customer_id)
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
        customer_type: CustomerType | None = None,
        status: CustomerStatus | None = None,
        communication_channel: CommunicationChannel | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[Customer], int]:
        query = select(Customer).where(Customer.is_deleted.is_(False))
        count_query = select(func.count(Customer.id)).where(
            Customer.is_deleted.is_(False)
        )

        if customer_type is not None:
            query = query.where(Customer.customer_type == customer_type)
            count_query = count_query.where(
                Customer.customer_type == customer_type
            )
        if status is not None:
            query = query.where(Customer.status == status)
            count_query = count_query.where(Customer.status == status)
        if communication_channel is not None:
            query = query.where(
                Customer.communication_channel == communication_channel
            )
            count_query = count_query.where(
                Customer.communication_channel == communication_channel
            )

        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        query = query.order_by(Customer.created_at.desc())
        query = query.offset(offset).limit(page_size)

        result = await self._session.execute(query)
        items = result.scalars().all()

        return items, total

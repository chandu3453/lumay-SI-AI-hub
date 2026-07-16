"""Customer domain dependency injection."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from domains.customer.repositories.customer_repository import CustomerRepository
from domains.customer.services.customer_service import CustomerService


async def get_customer_repository(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[CustomerRepository, None]:
    yield CustomerRepository(session=db)


async def get_customer_service(
    repository: CustomerRepository = Depends(get_customer_repository),
) -> AsyncGenerator[CustomerService, None]:
    yield CustomerService(repository=repository)

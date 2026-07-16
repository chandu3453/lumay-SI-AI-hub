"""Complaint domain dependency injection."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from domains.customer.repositories.customer_repository import CustomerRepository
from domains.interaction.repositories.interaction_repository import InteractionRepository
from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.complaint.services.complaint_service import ComplaintService


async def get_complaint_repository(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ComplaintRepository, None]:
    yield ComplaintRepository(session=db)


async def get_complaint_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ComplaintService, None]:
    complaint_repo = ComplaintRepository(session=db)
    customer_repo = CustomerRepository(session=db)
    interaction_repo = InteractionRepository(session=db)
    yield ComplaintService(
        repository=complaint_repo,
        customer_repository=customer_repo,
        interaction_repository=interaction_repo,
    )

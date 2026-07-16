"""Workflow domain dependency injection."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from domains.complaint.repositories.complaint_repository import ComplaintRepository
from domains.workflow.repositories.workflow_repository import WorkflowRepository
from domains.workflow.services.workflow_service import WorkflowService


async def get_workflow_repository(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[WorkflowRepository, None]:
    yield WorkflowRepository(session=db)


async def get_workflow_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[WorkflowService, None]:
    workflow_repo = WorkflowRepository(session=db)
    complaint_repo = ComplaintRepository(session=db)
    yield WorkflowService(
        repository=workflow_repo,
        complaint_repository=complaint_repo,
    )
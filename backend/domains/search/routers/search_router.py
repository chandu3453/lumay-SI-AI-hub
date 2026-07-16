"""Search API router — unified search across all entities for both portals."""

from fastapi import APIRouter, Depends, Query

from app.dependencies.auth import CurrentUser, get_current_user
from app.platform.logging import get_logger
from domains.search.services.search_service import get_search_service
from shared.response_schemas import SuccessResponse

router = APIRouter(prefix="/search", tags=["Search"])
logger = get_logger(__name__)


@router.get(
    "",
    summary="Unified search across all entities",
    description="Searches complaints, customers, interactions, workflows, and knowledge base. "
                "Returns identical data for both Customer Portal and Employee Portal.",
)
async def search_all(
    q: str = Query("", description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results per entity type"),
    _current_user: CurrentUser | None = Depends(get_current_user),
):
    service = get_search_service()
    results = service.search_all(q, limit)
    return SuccessResponse(data=results)

"""
Identity User Router.
"""

import uuid

from fastapi import APIRouter, Depends, Query

from app.dependencies.auth import CurrentUser, get_current_user
from app.dependencies.identity import get_user_repository
from domains.identity.repositories.user_repository import UserRepository
from domains.identity.schemas.user_schema import UserResponse
from shared.response_schemas import SuccessResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "",
    response_model=SuccessResponse[list[UserResponse]],
    summary="Batch-resolve user ids to names",
    description="Sprint 29 — resolves `assigned_employee_id`-style UUIDs (Conversation, "
    "Reporting) to display names. Unknown ids are silently omitted, not 404s.",
)
async def list_users(
    ids: str = Query(..., description="Comma-separated UUIDs"),
    repository: UserRepository = Depends(get_user_repository),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[list[UserResponse]]:
    parsed_ids: list[uuid.UUID] = []
    for raw in ids.split(","):
        raw = raw.strip()
        if not raw:
            continue
        try:
            parsed_ids.append(uuid.UUID(raw))
        except ValueError:
            continue
    users = await repository.list_by_ids(parsed_ids)
    return SuccessResponse(data=[UserResponse.model_validate(u) for u in users])

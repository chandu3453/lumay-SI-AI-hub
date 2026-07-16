"""Root router — top-level endpoint and API metadata."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.config.settings import Settings
from app.dependencies.settings import get_app_settings
from app.config.constants import APP_DESCRIPTION

router = APIRouter()


@router.get("/", summary="API root — platform metadata")
async def root(settings: Annotated[Settings, Depends(get_app_settings)]) -> dict:
    return {
        "name": settings.application.name,
        "version": settings.application.version,
        "environment": settings.application.environment,
        "description": APP_DESCRIPTION,
    }

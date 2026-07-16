"""
Application Lifespan — FastAPI lifespan context manager.

Orchestrates startup and shutdown of all infrastructure services
via the bootstrap module.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.platform.logging import get_logger
from app.startup import shutdown, startup

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan_handler(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("lifespan_started")
    await startup()
    try:
        yield
    finally:
        await shutdown()
        logger.info("lifespan_ended")

"""Logging platform — structured logging via structlog."""

from app.platform.logging.config import configure_logging
from app.platform.logging.logger import get_logger

__all__ = ["configure_logging", "get_logger"]

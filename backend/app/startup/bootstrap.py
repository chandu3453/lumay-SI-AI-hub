"""
Application Bootstrap — startup and shutdown lifecycle.

This module is the single place where application-wide initialisation
and teardown logic is orchestrated.

All infrastructure managers are initialised here in dependency-safe
order (no cross-service dependencies at this layer).
"""

from app.config import get_settings
from app.platform.cache.client import init_redis, shutdown_redis
from app.platform.database.session import close_db_engine, init_db_engine
from app.platform.logging import configure_logging, get_logger
from app.platform.messaging.client import close_messaging, init_messaging
from app.platform.search.client import close_search_client, init_search_client
from app.platform.storage.client import close_storage_client, init_storage_client

logger = get_logger(__name__)


async def startup() -> None:
    settings = get_settings()

    configure_logging(settings)

    _init_prompts()
    await _init_infrastructure()
    await _init_demo_data()

    logger.info(
        "application_startup_complete",
        name=settings.application.name,
        version=settings.application.version,
        environment=settings.application.environment,
    )


async def _init_demo_data() -> None:
    try:
        from app.demo.synthetic import generate_synthetic_data
        store = generate_synthetic_data()
        sizes = store.size()
        logger.info("demo_data_loaded_on_startup", sizes=sizes)
    except Exception:
        logger.warning("demo_data_skipped_on_startup", exc_info=True)


async def shutdown() -> None:
    await _close_infrastructure()
    logger.info("application_shutdown_complete")


def _init_prompts() -> None:
    try:
        from ai.prompts.templates import register_default_prompts
        register_default_prompts()
        logger.info("default_prompts_registered")
    except Exception:
        logger.warning("default_prompts_skipped", exc_info=True)
    try:
        from ai.intelligence.prompts import register_complaint_prompts
        register_complaint_prompts()
        logger.info("complaint_prompts_registered")
    except Exception:
        logger.warning("complaint_prompts_skipped", exc_info=True)


async def _init_infrastructure() -> None:
    for name, coro in (
        ("database", init_db_engine()),
        ("redis", init_redis()),
        ("opensearch", init_search_client()),
        ("storage", init_storage_client()),
        ("messaging", init_messaging()),
    ):
        try:
            await coro
            logger.info("infrastructure_started", service=name)
        except Exception:
            logger.warning("infrastructure_skipped", service=name, exc_info=True)


async def _close_infrastructure() -> None:
    for name, coro in (
        ("messaging", close_messaging()),
        ("storage", close_storage_client()),
        ("opensearch", close_search_client()),
        ("redis", shutdown_redis()),
        ("database", close_db_engine()),
    ):
        try:
            await coro
            logger.info("infrastructure_stopped", service=name)
        except Exception:
            logger.warning("infrastructure_close_error", service=name, exc_info=True)

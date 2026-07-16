"""
Async Database Session Factory.

Manages the SQLAlchemy async engine and session factory lifecycle.
Provides a scoped session generator for FastAPI dependency injection.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.compiler import compiles

from app.config import get_settings
from app.platform.logging import get_logger
from app.platform.database.base import Base

logger = get_logger(__name__)


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(32)"

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_db_engine() -> None:
    """
    Initialises the async SQLAlchemy engine and session factory.
    Called once during application startup.
    """
    global _engine, _session_factory

    settings = get_settings()

    engine_kwargs = {
        "echo": settings.database.echo,
    }

    if not settings.database.url.startswith("sqlite"):
        engine_kwargs.update(
            {
                "pool_size": settings.database.pool_size,
                "max_overflow": settings.database.max_overflow,
                "pool_timeout": 30,
                "pool_recycle": 1800,
                "pool_pre_ping": True,
            }
        )

    _engine = create_async_engine(settings.database.url, **engine_kwargs)

    if settings.database.url.startswith("sqlite"):
        from domains.identity.models.user import User  # noqa: F401
        from domains.customer.models.customer import Customer  # noqa: F401
        from domains.interaction.models.interaction import Interaction  # noqa: F401
        from domains.complaint.models.complaint import Complaint  # noqa: F401
        from domains.workflow.models.workflow import Workflow  # noqa: F401
        from domains.notification.models.notification import Notification  # noqa: F401
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database_tables_created", engine="sqlite")

    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    logger.info("database_engine_initialized", url=settings.database.url.split("@")[-1])


async def close_db_engine() -> None:
    """Disposes the async engine. Called during application shutdown."""
    global _engine, _session_factory

    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("database_engine_disposed")


def get_engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError("Database engine is not initialised. Call init_db_engine() first.")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError("Session factory is not initialised. Call init_db_engine() first.")
    return _session_factory


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields a scoped async database session.
    Automatically commits on success and rolls back on error.
    """
    if _session_factory is None:
        raise RuntimeError("Session factory is not initialised. Call init_db_engine() first.")

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

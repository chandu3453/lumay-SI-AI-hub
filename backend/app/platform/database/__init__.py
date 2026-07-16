"""Database platform — SQLAlchemy engine, session, repository, and migration utilities."""

from app.platform.database.base import (
    AuditMixin,
    AuditModel,
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)
from app.platform.database.session import (
    close_db_engine,
    get_async_session,
    get_engine,
    get_session_factory,
    init_db_engine,
)

try:
    from app.platform.database.migrations import (  # noqa: F401 — alembic optional at runtime
        downgrade_migrations,
        get_alembic_config,
        run_migrations,
    )
except ImportError:
    downgrade_migrations = None  # type: ignore[assignment]
    get_alembic_config = None  # type: ignore[assignment]
    run_migrations = None  # type: ignore[assignment]

try:
    from app.platform.database.repository import BaseRepository  # noqa: F401
except ImportError:
    BaseRepository = None  # type: ignore[assignment]

__all__ = [
    "AuditMixin",
    "AuditModel",
    "Base",
    "BaseRepository",
    "close_db_engine",
    "downgrade_migrations",
    "get_alembic_config",
    "get_async_session",
    "get_engine",
    "init_db_engine",
    "run_migrations",
    "SoftDeleteMixin",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
]

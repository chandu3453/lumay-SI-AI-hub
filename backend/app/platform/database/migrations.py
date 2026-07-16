"""
Database Migration Utilities.

Helpers for running Alembic migrations programmatically —
used in test setup and CLI scripts.
"""

from alembic import command
from alembic.config import Config


def get_alembic_config(ini_path: str = "alembic.ini") -> Config:
    """Returns a configured Alembic Config object."""
    config = Config(ini_path)
    return config


def run_migrations(ini_path: str = "alembic.ini") -> None:
    """Applies all pending Alembic migrations (upgrade to head)."""
    config = get_alembic_config(ini_path)
    command.upgrade(config, "head")


def downgrade_migrations(revision: str, ini_path: str = "alembic.ini") -> None:
    """Downgrades to the specified Alembic revision."""
    config = get_alembic_config(ini_path)
    command.downgrade(config, revision)

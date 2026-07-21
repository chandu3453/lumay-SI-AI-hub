"""
Alembic Environment Configuration.

Supports both online (direct DB) and offline (SQL script) migration modes.
Auto-detects all domain models by importing shared.base_model.Base.
"""

import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Ensure backend/ root is on sys.path so all imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all domain models so Alembic can detect them
from shared.base_model import Base  # noqa: E402

# Import every domain model to register it on Base.metadata
# New domains: uncomment the import once the domain package exists.
# Each import is wrapped in try/except to allow incremental domain enablement.
try:
    from domains.identity.models.user import User  # noqa: E402, F401
except ImportError:
    pass
try:
    from domains.customer.models.customer import Customer  # noqa: E402, F401
except ImportError:
    pass
try:
    from domains.interaction.models.interaction import Interaction  # noqa: E402, F401
except ImportError:
    pass

try:
    from domains.complaint.models.complaint import Complaint  # noqa: E402, F401
except ImportError:
    pass

try:
    from domains.workflow.models.workflow import Workflow  # noqa: E402, F401
except ImportError:
    pass
try:
    from domains.notification.models.notification import Notification  # noqa: E402, F401
except ImportError:
    pass
try:
    from domains.conversation.models.conversation import Conversation  # noqa: E402, F401
    from domains.conversation.models.conversation_message import ConversationMessage  # noqa: E402, F401
    from domains.conversation.models.conversation_participant import ConversationParticipant  # noqa: E402, F401
    from domains.conversation.models.conversation_channel import ConversationChannelLink  # noqa: E402, F401
    from domains.conversation.models.conversation_event import ConversationEvent  # noqa: E402, F401
except ImportError:
    pass
# Domain models — uncomment as they are implemented:
# from domains.analytics.models.report import Report  # noqa: E402, F401
# from domains.search.models.document import SearchDocument  # noqa: E402, F401
# from domains.audit.models.audit_log import AuditLog  # noqa: E402, F401
# from domains.knowledge.models.article import KnowledgeArticle  # noqa: E402, F401
# from domains.configuration.models.setting import ConfigurationSetting  # noqa: E402, F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    from app.config import get_settings
    return get_settings().database.url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

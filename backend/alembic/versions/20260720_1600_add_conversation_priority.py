"""add priority to conversations (Sprint 28 Phase 3 — employee interaction center)

Revision ID: 20260720_1600
Revises: 20260720_1100
Create Date: 2026-07-20 16:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = "20260720_1600"
down_revision: str | None = "20260720_1100"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# create_type=False on the column itself — the type is created explicitly
# below via .create(). CREATE TABLE auto-creates an Enum's Postgres type as a
# side effect, but ADD COLUMN on an existing table does not; omitting this
# explicit create() fails with "type conversation_priority does not exist".
conversation_priority = postgresql.ENUM(
    "LOW", "MEDIUM", "HIGH", "CRITICAL", name="conversation_priority", create_type=False
)


def upgrade() -> None:
    conversation_priority.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "conversations",
        sa.Column("priority", conversation_priority, nullable=False, server_default="MEDIUM"),
    )
    op.create_index("ix_conversations_priority", "conversations", ["priority"])


def downgrade() -> None:
    op.drop_index("ix_conversations_priority", table_name="conversations")
    op.drop_column("conversations", "priority")
    conversation_priority.drop(op.get_bind(), checkfirst=True)

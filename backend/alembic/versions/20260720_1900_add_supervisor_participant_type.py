"""add supervisor to conversation participant/sender enums (Sprint 28 Phase 4)

Revision ID: 20260720_1900
Revises: 20260720_1600
Create Date: 2026-07-20 19:00:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic
revision: str = "20260720_1900"
down_revision: str | None = "20260720_1600"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ALTER TYPE ... ADD VALUE cannot run inside the same transaction as a
    # statement that uses the new value, but running it alone (as here) is
    # safe on Postgres 12+ even under Alembic's default transactional DDL.
    op.execute("ALTER TYPE conversation_participant_type ADD VALUE IF NOT EXISTS 'SUPERVISOR'")
    op.execute("ALTER TYPE conversation_message_sender_type ADD VALUE IF NOT EXISTS 'SUPERVISOR'")


def downgrade() -> None:
    # Postgres has no ALTER TYPE ... DROP VALUE — removing an enum value
    # requires rebuilding the type (create new type, migrate columns, drop
    # old type), which risks data loss if any row already uses 'SUPERVISOR'.
    # Left as a no-op, matching common Alembic practice for enum additions.
    pass

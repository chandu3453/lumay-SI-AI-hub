"""add low/medium/high labels to complaint_severity enum (Sprint 30 — the
ComplaintSeverity Python enum was renamed from minor/moderate/major to
low/medium/high (keeping the old names as aliases) but the Postgres enum
type was never migrated to match; ComplaintCreate's own default value
(MEDIUM) had no matching DB label, so creating a complaint without an
explicit legacy severity crashed with a 500 on every request)

Revision ID: 20260721_1000
Revises: 20260721_0900
Create Date: 2026-07-21 10:00:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic
revision: str = "20260721_1000"
down_revision: str | None = "20260721_0900"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE complaint_severity ADD VALUE IF NOT EXISTS 'LOW'")
        op.execute("ALTER TYPE complaint_severity ADD VALUE IF NOT EXISTS 'MEDIUM'")
        op.execute("ALTER TYPE complaint_severity ADD VALUE IF NOT EXISTS 'HIGH'")


def downgrade() -> None:
    # Postgres has no DROP VALUE for enum types — added labels are
    # harmless to leave in place; nothing to reverse.
    pass

"""add indexes on conversations.assigned_employee_id and conversations.updated_at
(Sprint 30 — both are hot filter/sort columns for the employee queue list,
ConversationFactory's per-customer merge lookup, and Employee Analytics, with
no index today)

Revision ID: 20260721_0900
Revises: 20260720_2300
Create Date: 2026-07-21 09:00:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic
revision: str = "20260721_0900"
down_revision: str | None = "20260720_2300"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_conversations_assigned_employee_id",
        "conversations",
        ["assigned_employee_id"],
    )
    op.create_index(
        "ix_conversations_updated_at",
        "conversations",
        ["updated_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_conversations_updated_at", table_name="conversations")
    op.drop_index("ix_conversations_assigned_employee_id", table_name="conversations")

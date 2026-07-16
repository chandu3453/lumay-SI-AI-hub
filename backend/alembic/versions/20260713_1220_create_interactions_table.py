"""create interactions table

Revision ID: 20260713_1220
Revises:
Create Date: 2026-07-13 12:20:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = "20260713_1220"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "interactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("customer_ref", sa.String(255), nullable=True, index=True),
        sa.Column(
            "channel",
            sa.Enum("EMAIL", "WHATSAPP", "VOICE", "TEAMS", "WEB_FORM", "API", name="interaction_channel", create_constraint=True),
            nullable=False,
        ),
        sa.Column(
            "direction",
            sa.Enum("INBOUND", "OUTBOUND", name="interaction_direction", create_constraint=True),
            nullable=False,
        ),
        sa.Column("subject", sa.Text, nullable=True),
        sa.Column("transcript", sa.Text, nullable=True),
        sa.Column("attachments", sa.JSON, nullable=True),
        sa.Column(
            "status",
            sa.Enum("RECEIVED", "PROCESSING", "CLASSIFIED", "LINKED", "COMPLETED", "FAILED", "ARCHIVED", name="interaction_status", create_constraint=True),
            nullable=False,
            index=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, index=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("interactions")
    op.execute("DROP TYPE IF EXISTS interaction_channel")
    op.execute("DROP TYPE IF EXISTS interaction_direction")
    op.execute("DROP TYPE IF EXISTS interaction_status")

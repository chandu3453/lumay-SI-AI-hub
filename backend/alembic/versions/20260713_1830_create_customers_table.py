"""create customers table

Revision ID: 20260713_1830
Revises: 20260713_1220
Create Date: 2026-07-13 18:30:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = "20260713_1830"
down_revision: str | None = "20260713_1220"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "customer_number",
            sa.String(50),
            unique=True,
            nullable=True,
            index=True,
        ),
        sa.Column(
            "external_ref",
            sa.String(100),
            unique=True,
            nullable=False,
            index=True,
        ),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True, index=True),
        sa.Column("mobile_number", sa.String(50), nullable=True),
        sa.Column(
            "communication_channel",
            sa.Enum(
                "EMAIL",
                "SMS",
                "WHATSAPP",
                "PHONE",
                "WEB_FORM",
                "API",
                name="communication_channel",
                create_constraint=True,
            ),
            nullable=True,
        ),
        sa.Column(
            "customer_type",
            sa.Enum(
                "PROSPECT",
                "ACTIVE",
                "FORMER",
                "CHURNED",
                name="customer_type",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "segment",
            sa.Enum(
                "INDIVIDUAL",
                "CORPORATE",
                "SME",
                "VIP",
                name="customer_segment",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "ACTIVE",
                "INACTIVE",
                "SUSPENDED",
                "DECEASED",
                "ARCHIVED",
                name="customer_status",
                create_constraint=True,
            ),
            nullable=False,
            index=True,
        ),
        sa.Column("profile_metadata", sa.JSON, nullable=True),
        sa.Column(
            "is_deleted",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "deleted_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("customers")
    op.execute("DROP TYPE IF EXISTS communication_channel")
    op.execute("DROP TYPE IF EXISTS customer_type")
    op.execute("DROP TYPE IF EXISTS customer_segment")
    op.execute("DROP TYPE IF EXISTS customer_status")

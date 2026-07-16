"""create complaints table

Revision ID: 20260713_1930
Revises: 20260713_1830
Create Date: 2026-07-13 19:30:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = "20260713_1930"
down_revision: str | None = "20260713_1830"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "complaints",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "complaint_number",
            sa.String(50),
            unique=True,
            nullable=True,
            index=True,
        ),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customers.id"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "interaction_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("interactions.id"),
            nullable=True,
            index=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "category",
            sa.Enum(
                "BILLING",
                "CLAIMS",
                "POLICY",
                "SERVICE",
                "TECHNICAL",
                "GENERAL",
                name="complaint_category",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("subcategory", sa.String(255), nullable=True),
        sa.Column(
            "priority",
            sa.Enum(
                "LOW",
                "MEDIUM",
                "HIGH",
                "CRITICAL",
                name="complaint_priority",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.Enum(
                "MINOR",
                "MODERATE",
                "MAJOR",
                "CRITICAL",
                name="complaint_severity",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "SUBMITTED",
                "UNDER_REVIEW",
                "INVESTIGATING",
                "ESCALATED",
                "RESOLVED",
                "CLOSED",
                "ARCHIVED",
                name="complaint_status",
                create_constraint=True,
            ),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "source",
            sa.Enum(
                "PHONE",
                "EMAIL",
                "WEB_FORM",
                "CHAT",
                "SOCIAL_MEDIA",
                "REGULATORY",
                name="complaint_source",
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("assigned_queue", sa.String(255), nullable=True),
        sa.Column(
            "assigned_agent_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("resolution_summary", sa.Text, nullable=True),
        sa.Column("closure_reason", sa.String(255), nullable=True),
        sa.Column("ai_summary", sa.Text, nullable=True),
        sa.Column("sentiment", sa.String(50), nullable=True),
        sa.Column("severity_score", sa.Float, nullable=True),
        sa.Column("theme", sa.String(255), nullable=True),
        sa.Column("recommendation", sa.Text, nullable=True),
        sa.Column("risk_score", sa.Float, nullable=True),
        sa.Column("profile_metadata", sa.JSON, nullable=True),
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
    op.drop_table("complaints")
    op.execute("DROP TYPE IF EXISTS complaint_category")
    op.execute("DROP TYPE IF EXISTS complaint_priority")
    op.execute("DROP TYPE IF EXISTS complaint_severity")
    op.execute("DROP TYPE IF EXISTS complaint_status")
    op.execute("DROP TYPE IF EXISTS complaint_source")

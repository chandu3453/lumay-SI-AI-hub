"""create workflows table

Revision ID: 20260713_2210
Revises: 20260713_1930
Create Date: 2026-07-13 22:10:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = "20260713_2210"
down_revision: str | None = "20260713_1930"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "workflows",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workflow_number", sa.String(50), unique=True, nullable=True, index=True),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("complaints.id"), nullable=False, index=True),
        sa.Column("current_queue", sa.String(255), nullable=True),
        sa.Column("assigned_team", sa.String(255), nullable=True),
        sa.Column("assigned_agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("workflow_status",
            sa.Enum("PENDING", "ACTIVE", "SUSPENDED", "COMPLETED", "CANCELLED", "ARCHIVED",
                    name="workflow_status", create_constraint=True), nullable=False, index=True),
        sa.Column("workflow_stage",
            sa.Enum("INITIATED", "QUEUED", "ASSIGNED", "IN_PROGRESS", "REVIEW", "APPROVAL", "RESOLUTION", "COMPLETED",
                    name="workflow_stage", create_constraint=True), nullable=False),
        sa.Column("priority", sa.String(50), nullable=True),
        sa.Column("sla_status",
            sa.Enum("WITHIN_SLA", "AT_RISK", "BREACHED",
                    name="sla_status", create_constraint=True), nullable=False),
        sa.Column("escalation_level",
            sa.Enum("LEVEL_0", "LEVEL_1", "LEVEL_2", "LEVEL_3",
                    name="escalation_level", create_constraint=True), nullable=False),
        sa.Column("approval_status",
            sa.Enum("PENDING", "APPROVED", "REJECTED", "NOT_REQUIRED",
                    name="approval_status", create_constraint=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("workflow_metadata", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, index=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("workflows")
    op.execute("DROP TYPE IF EXISTS workflow_status")
    op.execute("DROP TYPE IF EXISTS workflow_stage")
    op.execute("DROP TYPE IF EXISTS sla_status")
    op.execute("DROP TYPE IF EXISTS escalation_level")
    op.execute("DROP TYPE IF EXISTS approval_status")
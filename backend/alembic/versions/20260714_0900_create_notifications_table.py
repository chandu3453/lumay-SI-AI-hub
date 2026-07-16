"""create notifications table

Revision ID: 20260714_0900
Revises: 20260713_2210
Create Date: 2026-07-14 09:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = "20260714_0900"
down_revision: str | None = "20260713_2210"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("notification_number", sa.String(50), unique=True, nullable=True, index=True),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workflows.id"), nullable=True, index=True),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("complaints.id"), nullable=True, index=True),
        sa.Column("notification_type",
            sa.Enum("ALERT", "REMINDER", "CONFIRMATION", "STATUS_UPDATE", "ESCALATION", "RESOLUTION", "PROMOTIONAL", "SYSTEM",
                    name="notification_type", create_constraint=True), nullable=False),
        sa.Column("notification_channel",
            sa.Enum("EMAIL", "SMS", "WHATSAPP", "IN_APP", "PUSH",
                    name="notification_channel", create_constraint=True), nullable=False),
        sa.Column("recipient", sa.String(512), nullable=False),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("notification_status",
            sa.Enum("PENDING", "QUEUED", "SENDING", "SENT", "DELIVERED", "FAILED", "RETRYING", "ARCHIVED",
                    name="notification_status", create_constraint=True), nullable=False, index=True),
        sa.Column("priority",
            sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL",
                    name="notification_priority", create_constraint=True), nullable=False),
        sa.Column("retry_count", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.String(1024), nullable=True),
        sa.Column("notification_metadata", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, index=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.execute("DROP TYPE IF EXISTS notification_type")
    op.execute("DROP TYPE IF EXISTS notification_channel")
    op.execute("DROP TYPE IF EXISTS notification_status")
    op.execute("DROP TYPE IF EXISTS notification_priority")
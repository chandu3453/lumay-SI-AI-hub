"""create conversation tables (Sprint 28 Phase 1 — unified omnichannel conversation foundation)

Revision ID: 20260720_1100
Revises: 20260715_0930
Create Date: 2026-07-20 11:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = "20260720_1100"
down_revision: str | None = "20260715_0930"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("complaint_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("complaints.id"), nullable=True, index=True),
        sa.Column("current_status",
            sa.Enum("NEW", "ACTIVE", "WAITING_FOR_CUSTOMER", "WAITING_FOR_AGENT", "AI_HANDLING",
                    "HUMAN_HANDLING", "ESCALATED", "RESOLVED", "CLOSED",
                    name="conversation_status", create_constraint=True), nullable=False, index=True),
        sa.Column("current_channel",
            sa.Enum("WEB_CHAT", "VOICE", "WHATSAPP", "EMAIL", "COMPLAINT",
                    name="conversation_channel", create_constraint=True), nullable=False),
        sa.Column("assigned_employee_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("ai_handling", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("human_handling", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, index=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "conversation_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("sender_type",
            sa.Enum("CUSTOMER", "AI", "EMPLOYEE", "SYSTEM",
                    name="conversation_message_sender_type", create_constraint=True), nullable=False),
        sa.Column("channel",
            sa.Enum("WEB_CHAT", "VOICE", "WHATSAPP", "EMAIL", "COMPLAINT",
                    name="conversation_message_channel", create_constraint=True), nullable=False),
        sa.Column("message_type",
            sa.Enum("TEXT", "TRANSCRIPT", "ATTACHMENT", "EVENT", "SYSTEM_NOTIFICATION",
                    name="conversation_message_type", create_constraint=True), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("message_metadata", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, index=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "conversation_participants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("participant_type",
            sa.Enum("CUSTOMER", "AI", "EMPLOYEE", "SYSTEM",
                    name="conversation_participant_type", create_constraint=True), nullable=False),
        sa.Column("participant_ref", sa.String(255), nullable=True),
        sa.Column("role", sa.String(50), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, index=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "conversation_channels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("channel",
            sa.Enum("WEB_CHAT", "VOICE", "WHATSAPP", "EMAIL", "COMPLAINT",
                    name="conversation_channel_link_channel", create_constraint=True), nullable=False),
        sa.Column("external_ref_type", sa.String(50), nullable=False),
        sa.Column("external_ref_id", sa.String(255), nullable=False),
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, index=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_ref_type", "external_ref_id", name="uq_conversation_channel_ref"),
    )

    op.create_table(
        "conversation_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("source_domain", sa.String(50), nullable=False),
        sa.Column("payload", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, index=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("conversation_events")
    op.drop_table("conversation_channels")
    op.execute("DROP TYPE IF EXISTS conversation_channel_link_channel")
    op.drop_table("conversation_participants")
    op.execute("DROP TYPE IF EXISTS conversation_participant_type")
    op.drop_table("conversation_messages")
    op.execute("DROP TYPE IF EXISTS conversation_message_sender_type")
    op.execute("DROP TYPE IF EXISTS conversation_message_channel")
    op.execute("DROP TYPE IF EXISTS conversation_message_type")
    op.drop_table("conversations")
    op.execute("DROP TYPE IF EXISTS conversation_status")
    op.execute("DROP TYPE IF EXISTS conversation_channel")

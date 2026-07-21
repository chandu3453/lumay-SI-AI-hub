"""create agent_assist_insights table (Sprint 28 Phase 5 — AI Agent Assist & Conversation Intelligence)

Revision ID: 20260720_2200
Revises: 20260720_1900
Create Date: 2026-07-20 22:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = "20260720_2200"
down_revision: str | None = "20260720_1900"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "agent_assist_insights",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("message_count_at_generation", sa.Integer, nullable=False, server_default="0"),
        sa.Column("summary", sa.String, nullable=True),
        sa.Column("intent", sa.String(100), nullable=True),
        sa.Column("intent_confidence", sa.Float, nullable=True),
        sa.Column("sentiment", sa.String(50), nullable=True),
        sa.Column("sentiment_polarity", sa.Float, nullable=True),
        sa.Column("escalation_risk_score", sa.Integer, nullable=True),
        sa.Column("escalation_risk_level", sa.String(20), nullable=True),
        sa.Column("next_best_actions", sa.JSON, nullable=True),
        sa.Column("knowledge_articles", sa.JSON, nullable=True),
        sa.Column("suggested_replies", sa.JSON, nullable=True),
        sa.Column("insights", sa.JSON, nullable=True),
        sa.Column("alerts", sa.JSON, nullable=True),
        sa.Column("complaint_severity_at_generation", sa.String(20), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("agent_assist_insights")

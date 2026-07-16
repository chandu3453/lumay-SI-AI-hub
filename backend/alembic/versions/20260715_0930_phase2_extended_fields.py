"""phase2_extended_complaint_fields

FR-001: policy_id, policy_number, claim_id, claim_number, product, channel, interaction_ids
FR-007: acknowledged_time, acknowledgment_deadline, resolution_deadline
FR-010: customer_requested_outcome
FR-014: human_validation
FR-020: regulatory_flag

Revision ID: 20260715_0930
Revises: 9b1ab922e651
Create Date: 2026-07-15 09:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision: str = '20260715_0930'
down_revision: Union[str, None] = '9b1ab922e651'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # FR-001 — Policy & Claim linkage
    op.add_column('complaints', sa.Column('policy_id', sa.String(length=100), nullable=True))
    op.add_column('complaints', sa.Column('policy_number', sa.String(length=100), nullable=True))
    op.add_column('complaints', sa.Column('claim_id', sa.String(length=100), nullable=True))
    op.add_column('complaints', sa.Column('claim_number', sa.String(length=100), nullable=True))

    # FR-001 — Product type & explicit channel
    op.add_column('complaints', sa.Column('product', sa.String(length=50), nullable=True))
    op.add_column('complaints', sa.Column('channel', sa.String(length=50), nullable=True))

    # FR-001 — Multiple source interaction IDs
    op.add_column('complaints', sa.Column('interaction_ids', sa.JSON(), nullable=True))

    # FR-010 — Customer requested outcome
    op.add_column('complaints', sa.Column('customer_requested_outcome', sa.Text(), nullable=True))

    # FR-007 — SLA deadline fields
    op.add_column('complaints', sa.Column('acknowledged_time', sa.String(length=50), nullable=True))
    op.add_column('complaints', sa.Column('acknowledgment_deadline', sa.String(length=50), nullable=True))
    op.add_column('complaints', sa.Column('resolution_deadline', sa.String(length=50), nullable=True))

    # FR-020 — Regulatory compliance flag
    op.add_column('complaints', sa.Column('regulatory_flag', sa.Boolean(), nullable=True))

    # FR-014 — Human validation status
    op.add_column('complaints', sa.Column('human_validation', sa.String(length=20), nullable=True))

    # Indexes for new filterable fields
    op.create_index('ix_complaints_product', 'complaints', ['product'], unique=False)
    op.create_index('ix_complaints_channel', 'complaints', ['channel'], unique=False)
    op.create_index('ix_complaints_policy_number', 'complaints', ['policy_number'], unique=False)
    op.create_index('ix_complaints_claim_id', 'complaints', ['claim_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_complaints_claim_id', table_name='complaints')
    op.drop_index('ix_complaints_policy_number', table_name='complaints')
    op.drop_index('ix_complaints_channel', table_name='complaints')
    op.drop_index('ix_complaints_product', table_name='complaints')
    op.drop_column('complaints', 'human_validation')
    op.drop_column('complaints', 'regulatory_flag')
    op.drop_column('complaints', 'resolution_deadline')
    op.drop_column('complaints', 'acknowledgment_deadline')
    op.drop_column('complaints', 'acknowledged_time')
    op.drop_column('complaints', 'customer_requested_outcome')
    op.drop_column('complaints', 'interaction_ids')
    op.drop_column('complaints', 'channel')
    op.drop_column('complaints', 'product')
    op.drop_column('complaints', 'claim_number')
    op.drop_column('complaints', 'claim_id')
    op.drop_column('complaints', 'policy_number')
    op.drop_column('complaints', 'policy_id')

"""add missing labels to complaint_source enum (found live-testing the
WhatsApp/web-chat channels — the Postgres enum only had
{PHONE,EMAIL,WEB_FORM,CHAT,SOCIAL_MEDIA,REGULATORY} while the Python
ComplaintSource enum has 13 members; auto-triaged complaints from the two
most common real channels, WHATSAPP and WEB_CHAT, silently failed in the
background complaint-intelligence task every time)

Revision ID: 20260721_1100
Revises: 20260721_1000
Create Date: 2026-07-21 11:00:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic
revision: str = "20260721_1100"
down_revision: str | None = "20260721_1000"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_MISSING_LABELS = [
    "WHATSAPP",
    "WEB_CHAT",
    "AGENT_ENTERED",
    "SMART_CALL",
    "MOBILE_APP",
    "PORTAL",
    "IN_PERSON",
    "POSTAL_MAIL",
]


def upgrade() -> None:
    with op.get_context().autocommit_block():
        for label in _MISSING_LABELS:
            op.execute(f"ALTER TYPE complaint_source ADD VALUE IF NOT EXISTS '{label}'")


def downgrade() -> None:
    # Postgres has no DROP VALUE for enum types — added labels are
    # harmless to leave in place; nothing to reverse.
    pass

"""ConversationEvent ORM model — audit trail of complaint/workflow/notification/system
events that occurred inside a conversation's lifetime. `event_type` reuses the
`routing_key` strings already modeled by each domain's DomainEvent subclasses
(e.g. "complaint.created", "workflow.started") for consistency.
"""

import uuid

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.database.base import AuditModel


class ConversationEvent(AuditModel):
    __tablename__ = "conversation_events"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    source_domain: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)

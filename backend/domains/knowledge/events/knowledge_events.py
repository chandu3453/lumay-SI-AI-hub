"""
Knowledge Domain Events.
"""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from shared.base_event import DomainEvent


@dataclass(frozen=True)
class KnowledgeArticlePublishedEvent(DomainEvent):
    article_id: UUID = field(default_factory=uuid4)
    category_id: UUID = field(default_factory=uuid4)
    published_by: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="knowledge.article_published")


@dataclass(frozen=True)
class KnowledgeArticleUpdatedEvent(DomainEvent):
    article_id: UUID = field(default_factory=uuid4)
    updated_by: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="knowledge.article_updated")


@dataclass(frozen=True)
class KnowledgeArticleArchivedEvent(DomainEvent):
    article_id: UUID = field(default_factory=uuid4)
    archived_by: UUID = field(default_factory=uuid4)
    routing_key: str = field(init=False, default="knowledge.article_archived")

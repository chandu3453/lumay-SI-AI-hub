"""Search Service — abstraction over synthetic data.

Fully replaceable with OpenSearch after demo phase.
Architecture: SearchService → KnowledgeService → SyntheticKnowledgeRepository
"""

from __future__ import annotations

from typing import Any

from knowledge.repository import get_knowledge_repository
from app.demo.synthetic import get_synthetic_store
from app.platform.logging import get_logger

logger = get_logger(__name__)


class SearchService:
    def __init__(self) -> None:
        self._store = get_synthetic_store()
        self._knowledge = get_knowledge_repository()

    def search_complaints(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        if not query:
            return []
        q = query.lower()
        results = []
        for c in self._store.get("complaints", []):
            if q in c.get("title", "").lower() or q in c.get("description", "").lower() or q in c.get("category", ""):
                results.append({"source": "complaint", "id": c["id"], "title": c.get("title"), "status": c.get("status"), "category": c.get("category")})
        return results[:limit]

    def search_customers(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        if not query:
            return []
        q = query.lower()
        results = []
        for c in self._store.get("customers", []):
            if q in c.get("full_name", "").lower() or q in c.get("email", "").lower() or q in c.get("customer_number", "").lower():
                results.append({"source": "customer", "id": c["id"], "name": c.get("full_name"), "email": c.get("email"), "segment": c.get("segment")})
        return results[:limit]

    def search_interactions(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        if not query:
            return []
        q = query.lower()
        results = []
        for c in self._store.get("interactions", []):
            if q in c.get("subject", "").lower() or q in c.get("transcript", "").lower():
                results.append({"source": "interaction", "id": c["id"], "subject": c.get("subject"), "channel": c.get("channel")})
        return results[:limit]

    def search_workflows(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        if not query:
            return []
        q = query.lower()
        results = []
        for w in self._store.get("workflows", []):
            if q in w.get("workflow_number", "").lower() or q in w.get("assigned_team", "").lower():
                results.append({"source": "workflow", "id": w["id"], "status": w.get("workflow_status"), "stage": w.get("workflow_stage"), "team": w.get("assigned_team")})
        return results[:limit]

    def search_knowledge(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        if not query:
            return []
        results = self._knowledge.search_all(query)
        return results[:limit]

    def search_all(self, query: str, limit: int = 20) -> dict[str, Any]:
        return {
            "query": query,
            "complaints": self.search_complaints(query, limit),
            "customers": self.search_customers(query, limit),
            "interactions": self.search_interactions(query, limit),
            "workflows": self.search_workflows(query, limit),
            "knowledge": self.search_knowledge(query, limit),
        }


_search_service: SearchService | None = None


def get_search_service() -> SearchService:
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service


def reset_search_service() -> None:
    global _search_service
    _search_service = None
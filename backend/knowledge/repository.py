"""Knowledge Repository — loads demo data from JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.platform.logging import get_logger

logger = get_logger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class KnowledgeRepository:
    def __init__(self) -> None:
        self._policies: list[dict[str, Any]] = []
        self._faq: list[dict[str, Any]] = []
        self._products: list[dict[str, Any]] = []

    def load_all(self) -> None:
        self._policies = self._load_json("policies.json")
        self._faq = self._load_json("faq.json")
        self._products = self._load_json("products.json")
        logger.info(
            "knowledge_data_loaded",
            policies=len(self._policies),
            faq=len(self._faq),
            products=len(self._products),
        )

    def _load_json(self, filename: str) -> list[dict[str, Any]]:
        path = DATA_DIR / filename
        if not path.exists():
            logger.warning("knowledge_file_not_found", path=str(path))
            return []
        with open(path) as f:
            return json.load(f)

    @property
    def policies(self) -> list[dict[str, Any]]:
        return list(self._policies)

    @property
    def faq(self) -> list[dict[str, Any]]:
        return list(self._faq)

    @property
    def products(self) -> list[dict[str, Any]]:
        return list(self._products)

    def search_policies(self, query: str) -> list[dict[str, Any]]:
        q = query.lower()
        return [
            p for p in self._policies
            if q in p["title"].lower() or q in p["summary"].lower() or any(q in t.lower() for t in p.get("tags", []))
        ]

    def search_faq(self, query: str) -> list[dict[str, Any]]:
        q = query.lower()
        return [
            f for f in self._faq
            if q in f["question"].lower() or q in f["answer"].lower() or q in f.get("category", "").lower()
        ]

    def search_products(self, query: str) -> list[dict[str, Any]]:
        q = query.lower()
        return [
            p for p in self._products
            if q in p["name"].lower() or q in p["description"].lower() or any(q in t.lower() for t in p.get("tags", []))
        ]

    def search_all(self, query: str) -> list[dict[str, Any]]:
        results = []
        for item in self.search_policies(query):
            results.append({"source": "policy", "score": 1.0, **item})
        for item in self.search_faq(query):
            results.append({"source": "faq", "score": 1.0, **item})
        for item in self.search_products(query):
            results.append({"source": "product", "score": 1.0, **item})
        return results

    def get_policy(self, policy_id: str) -> dict[str, Any] | None:
        for p in self._policies:
            if p["id"] == policy_id:
                return p
        return None

    def get_faq(self, faq_id: str) -> dict[str, Any] | None:
        for f in self._faq:
            if f["id"] == faq_id:
                return f
        return None

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        for p in self._products:
            if p["id"] == product_id:
                return p
        return None


_repository: KnowledgeRepository | None = None


def get_knowledge_repository() -> KnowledgeRepository:
    global _repository
    if _repository is None:
        _repository = KnowledgeRepository()
        _repository.load_all()
    return _repository


def reset_knowledge_repository() -> None:
    global _repository
    _repository = None
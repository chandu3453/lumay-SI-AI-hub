"""Knowledge service unit tests."""

import pytest

from knowledge.models import KnowledgeSearchResult, PolicyArticle, FAQEntry, ProductInfo
from knowledge.repository import KnowledgeRepository
from knowledge.service import KnowledgeService


class TestKnowledgeModels:
    def test_policy_article_creation(self) -> None:
        p = PolicyArticle(id="POL-001", title="Test", type="auto", summary="Test policy", tags=["test"])
        assert p.id == "POL-001"
        assert "auto" in p.type

    def test_faq_entry_creation(self) -> None:
        f = FAQEntry(id="FAQ-001", question="Q?", answer="A", category="general")
        assert f.question == "Q?"
        assert f.answer == "A"

    def test_product_info_creation(self) -> None:
        p = ProductInfo(id="PROD-001", name="Test Product", type="auto", features=["Feature1"])
        assert p.name == "Test Product"
        assert len(p.features) == 1

    def test_search_result_creation(self) -> None:
        r = KnowledgeSearchResult(query="test", results=[{"id": "1"}], total=1, source="faq")
        assert r.total == 1
        assert r.source == "faq"


class TestKnowledgeRepository:
    def setup_method(self) -> None:
        self.repo = KnowledgeRepository()
        self.repo._policies = [
            {"id": "POL-001", "title": "Auto Policy", "type": "auto", "summary": "Auto insurance", "tags": ["auto"]},
            {"id": "POL-002", "title": "Home Policy", "type": "home", "summary": "Home insurance", "tags": ["home"]},
        ]
        self.repo._faq = [
            {"id": "FAQ-001", "question": "How to file a claim?", "answer": "Call us", "category": "claims", "tags": ["claims"]},
        ]
        self.repo._products = [
            {"id": "PROD-001", "name": "Auto Shield", "type": "auto", "description": "Auto product", "tags": ["auto"]},
        ]

    def test_search_policies(self) -> None:
        results = self.repo.search_policies("auto")
        assert len(results) == 1
        assert results[0]["id"] == "POL-001"

    def test_search_faq(self) -> None:
        results = self.repo.search_faq("claim")
        assert len(results) == 1

    def test_search_products(self) -> None:
        results = self.repo.search_products("shield")
        assert len(results) == 1

    def test_search_all(self) -> None:
        results = self.repo.search_all("auto")
        assert len(results) == 2

    def test_get_policy(self) -> None:
        p = self.repo.get_policy("POL-001")
        assert p is not None
        assert p["title"] == "Auto Policy"

    def test_get_faq(self) -> None:
        f = self.repo.get_faq("FAQ-001")
        assert f is not None
        assert f["question"] == "How to file a claim?"

    def test_get_product(self) -> None:
        p = self.repo.get_product("PROD-001")
        assert p is not None
        assert p["name"] == "Auto Shield"

    def test_search_nonexistent(self) -> None:
        results = self.repo.search_policies("nonexistent")
        assert len(results) == 0


class TestKnowledgeService:
    def setup_method(self) -> None:
        self.service = KnowledgeService()
        self.service._repo._policies = [
            {"id": "POL-001", "title": "Auto Policy", "type": "auto", "summary": "Auto insurance", "tags": ["auto"]},
        ]
        self.service._repo._faq = [
            {"id": "FAQ-001", "question": "How to file a claim?", "answer": "Call us", "category": "claims"},
        ]
        self.service._repo._products = [
            {"id": "PROD-001", "name": "Auto Shield", "type": "auto", "description": "Auto product", "tags": ["auto"]},
        ]

    def test_search_returns_results(self) -> None:
        result = self.service.search("auto")
        assert result.total > 0

    def test_search_filtered_by_source(self) -> None:
        result = self.service.search("policy", source="policy")
        assert result.source == "policy"

    def test_get_all_policies(self) -> None:
        policies = self.service.get_all_policies()
        assert len(policies) == 1

    def test_get_all_faq(self) -> None:
        faq = self.service.get_all_faq()
        assert len(faq) == 1

    def test_get_all_products(self) -> None:
        products = self.service.get_all_products()
        assert len(products) == 1
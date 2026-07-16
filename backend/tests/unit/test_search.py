"""Search service unit tests."""

from app.demo.synthetic import generate_synthetic_data, get_synthetic_store
from domains.search.services.search_service import SearchService, get_search_service


class TestSearchService:
    def setup_method(self) -> None:
        get_synthetic_store().clear()
        generate_synthetic_data()
        self.service = SearchService()

    def test_search_complaints(self) -> None:
        results = self.service.search_complaints("billing")
        assert len(results) > 0
        for r in results:
            assert r["source"] == "complaint"

    def test_search_customers(self) -> None:
        results = self.service.search_customers("Smith")
        assert len(results) > 0

    def test_search_interactions(self) -> None:
        results = self.service.search_interactions("claim")
        assert len(results) > 0

    def test_search_workflows(self) -> None:
        results = self.service.search_workflows("claims")
        assert len(results) > 0

    def test_search_knowledge(self) -> None:
        results = self.service.search_knowledge("policy")
        assert len(results) > 0

    def test_search_all(self) -> None:
        results = self.service.search_all("billing")
        assert "complaints" in results
        assert "customers" in results
        assert "knowledge" in results
        assert len(results["complaints"]) > 0

    def test_search_empty_query(self) -> None:
        results = self.service.search_all("")
        assert len(results["complaints"]) == 0

    def test_search_service_singleton(self) -> None:
        s1 = get_search_service()
        s2 = get_search_service()
        assert s1 is s2
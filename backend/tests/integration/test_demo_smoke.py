"""Demo platform — comprehensive smoke tests for client demo readiness.

Tests cover: data loading, dashboard, scenarios, search, knowledge, health, and full walkthrough.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestDemoSmoke:
    """Smoke tests verifying every demo endpoint works with loaded data."""

    async def test_health_before_load_returns_no_data(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/demo/health")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "status" in data

    async def test_load_demo_data_returns_correct_counts(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/demo/load")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        counts = body["data"]["counts"]
        assert counts["customers"] == 500
        assert counts["interactions"] == 1500
        assert counts["complaints"] == 800
        assert counts["workflows"] == 800
        assert counts["notifications"] == 800

    async def test_run_demo_returns_kpis(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/demo/run")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["message"] == "Demo ready"
        assert "kpis" in data
        assert data["kpis"]["total_customers"] == 500

    async def test_health_after_load_returns_ready(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/health")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "ready"
        assert data["data_loaded"] is True

    async def test_dashboard_overview_returns_all_kpis(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/overview")
        assert response.status_code == 200
        kpis = response.json()["data"]
        assert kpis["total_customers"] == 500
        assert kpis["total_complaints"] == 800
        assert kpis["total_workflows"] == 800
        assert kpis["sla_compliance_rate"] >= 0

    async def test_dashboard_trends_daily(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/trends?granularity=daily")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["daily"]) > 0
        assert len(data["category_distribution"]) == 6

    async def test_dashboard_trends_weekly(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/trends?granularity=weekly")
        assert response.status_code == 200
        assert len(response.json()["data"]["weekly"]) > 0

    async def test_dashboard_trends_monthly(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/trends?granularity=monthly")
        assert response.status_code == 200
        assert len(response.json()["data"]["monthly"]) > 0

    async def test_dashboard_search_billing(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/search?query=billing")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["complaints"]) > 0
        assert "query" in data

    async def test_dashboard_search_empty_returns_empty(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/search?query=nonexistent_xyz")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["complaints"]) == 0
        assert len(data["customers"]) == 0

    async def test_dashboard_knowledge_faq(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/knowledge?query=claim&source=faq")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["source"] == "faq"
        assert data["total"] >= 0

    async def test_dashboard_knowledge_all(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/knowledge?query=insurance")
        assert response.status_code == 200
        assert "results" in response.json()["data"]

    async def test_dashboard_reports_full(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/reports")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "kpis" in data
        assert "trends" in data
        assert "sla" in data
        assert "departments" in data
        assert "customers" in data
        assert "workflows" in data
        assert "notifications" in data

    async def test_reset_demo_data(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.post("/api/v1/demo/reset")
        assert response.status_code == 200
        assert response.json()["data"]["message"] == "Demo data reset successfully"

    async def test_scenario_customer_complaint(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.post("/api/v1/demo/scenario/customer-complaint")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "scenario" in data
        assert "customer" in data
        assert "complaint" in data
        assert "workflow" in data
        assert "ai_analysis" in data

    async def test_scenario_knowledge_search(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.post(
            "/api/v1/demo/scenario/knowledge-search",
            json={"query": "How to file a claim?"},
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["scenario"] == "Knowledge Base Search"
        assert "faq" in data
        assert "policies" in data
        assert "rag_demo" in data

    async def test_scenario_duplicate_detection(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.post("/api/v1/demo/scenario/duplicate-detection")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["scenario"] == "Duplicate Complaint Detection"
        assert "complaint_a" in data
        assert "complaint_b" in data
        assert "analysis" in data

    async def test_scenario_dashboard(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.post("/api/v1/demo/scenario/dashboard")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["scenario"] == "Executive Dashboard Overview"
        assert "kpis" in data
        assert "trends" in data
        assert "sla" in data
        assert "departments" in data
        assert "workflows" in data

    async def test_scenario_full_demo(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.post("/api/v1/demo/scenario/full-demo")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["scenario"] == "Complete Platform Demo"
        assert "executive_dashboard" in data
        assert "complaint_lifecycle" in data
        assert "analytics" in data
        assert "available_apis" in data
        assert len(data["available_apis"]) > 0

    async def test_analytics_all_endpoints(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        for path in ["/api/v1/analytics/kpis", "/api/v1/analytics/trends",
                      "/api/v1/analytics/sla", "/api/v1/analytics/departments",
                      "/api/v1/analytics/resolution", "/api/v1/analytics/customers",
                      "/api/v1/analytics/workflows", "/api/v1/analytics/notifications",
                      "/api/v1/analytics/report"]:
            response = await client.get(path)
            assert response.status_code == 200, f"Failed: {path}"

    async def test_swagger_available(self, client: AsyncClient) -> None:
        response = await client.get("/docs")
        assert response.status_code in (200, 307)

    async def test_openapi_schema_includes_demo_paths(self, client: AsyncClient) -> None:
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        paths = response.json()["paths"]
        assert "/api/v1/demo/load" in paths
        assert "/api/v1/demo/reset" in paths
        assert "/api/v1/demo/run" in paths
        assert "/api/v1/demo/health" in paths
        assert "/api/v1/demo/scenario/customer-complaint" in paths
        assert "/api/v1/demo/scenario/knowledge-search" in paths
        assert "/api/v1/demo/scenario/duplicate-detection" in paths
        assert "/api/v1/demo/scenario/dashboard" in paths
        assert "/api/v1/demo/scenario/full-demo" in paths

    async def test_concurrent_demo_workflow(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        import asyncio
        async def call(path: str) -> int:
            r = await client.get(path)
            return r.status_code
        paths = [
            "/api/v1/demo/dashboard/overview",
            "/api/v1/demo/dashboard/kpis",
            "/api/v1/demo/dashboard/trends",
            "/api/v1/demo/dashboard/reports",
        ]
        results = await asyncio.gather(*[call(p) for p in paths])
        assert all(r == 200 for r in results)
"""Demo API integration tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestDemoAPI:
    async def test_load_demo_data_200(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/demo/load")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["message"] == "Demo data loaded successfully"
        assert body["data"]["counts"]["customers"] == 500

    async def test_dashboard_overview_200(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/overview")
        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_dashboard_kpis_200(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/kpis")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["total_customers"] == 500

    async def test_dashboard_trends_200(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/trends")
        assert response.status_code == 200
        assert "daily" in response.json()["data"]

    async def test_dashboard_search_200(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/search?query=billing")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["complaints"]) > 0

    async def test_dashboard_knowledge_200(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/knowledge?query=claim")
        assert response.status_code == 200
        assert response.json()["data"]["total"] >= 0

    async def test_dashboard_reports_200(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/reports")
        assert response.status_code == 200
        assert "kpis" in response.json()["data"]

    async def test_run_demo_200(self, client: AsyncClient) -> None:
        response = await client.post("/api/v1/demo/run")
        assert response.status_code == 200
        assert response.json()["data"]["message"] == "Demo ready"

    async def test_reset_demo_200(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.post("/api/v1/demo/reset")
        assert response.status_code == 200
        assert response.json()["data"]["message"] == "Demo data reset successfully"

    async def test_empty_search_returns_empty_results(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/demo/dashboard/search?query=nonexistent12345")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["complaints"]) == 0

    async def test_analytics_kpis_endpoint(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/analytics/kpis")
        assert response.status_code == 200

    async def test_analytics_trends_endpoint(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/analytics/trends?granularity=daily")
        assert response.status_code == 200

    async def test_analytics_report_endpoint(self, client: AsyncClient) -> None:
        await client.post("/api/v1/demo/load")
        response = await client.get("/api/v1/analytics/report")
        assert response.status_code == 200
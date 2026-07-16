"""Customer REST API unit tests."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCustomerAPI:
    async def test_create_customer_201(self, client: AsyncClient) -> None:
        payload = {
            "external_ref": "CUST-001",
            "full_name": "John Doe",
            "email": "john@example.com",
            "mobile_number": "+1234567890",
            "customer_type": "active",
            "segment": "individual",
        }
        response = await client.post("/api/v1/customers", json=payload)
        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["external_ref"] == "CUST-001"
        assert body["data"]["full_name"] == "John Doe"
        assert body["data"]["email"] == "john@example.com"
        assert body["data"]["mobile_number"] == "+1234567890"
        assert body["data"]["customer_type"] == "active"
        assert body["data"]["status"] == "active"
        assert "id" in body["data"]
        assert "created_at" in body["data"]

    async def test_create_customer_missing_external_ref_422(
        self, client: AsyncClient,
    ) -> None:
        payload = {"full_name": "No Ref"}
        response = await client.post("/api/v1/customers", json=payload)
        assert response.status_code == 422

    async def test_create_customer_missing_full_name_422(
        self, client: AsyncClient,
    ) -> None:
        payload = {"external_ref": "NO-NAME"}
        response = await client.post("/api/v1/customers", json=payload)
        assert response.status_code == 422

    async def test_create_customer_invalid_email_422(
        self, client: AsyncClient,
    ) -> None:
        payload = {
            "external_ref": "BAD-EMAIL",
            "full_name": "Bad Email",
            "email": "not-an-email",
        }
        response = await client.post("/api/v1/customers", json=payload)
        assert response.status_code == 422

    async def test_create_customer_duplicate_external_ref_409(
        self, client: AsyncClient,
    ) -> None:
        payload = {
            "external_ref": "DUP-REF",
            "full_name": "First",
            "email": "first@example.com",
        }
        await client.post("/api/v1/customers", json=payload)
        response = await client.post("/api/v1/customers", json=payload)
        assert response.status_code == 409
        body = response.json()
        assert body["error_code"] == "CUSTOMER__ALREADY_EXISTS"

    async def test_create_customer_duplicate_email_409(
        self, client: AsyncClient,
    ) -> None:
        payload1 = {
            "external_ref": "USR-001",
            "full_name": "User One",
            "email": "shared@example.com",
        }
        payload2 = {
            "external_ref": "USR-002",
            "full_name": "User Two",
            "email": "shared@example.com",
        }
        await client.post("/api/v1/customers", json=payload1)
        response = await client.post("/api/v1/customers", json=payload2)
        assert response.status_code == 409
        assert response.json()["error_code"] == "CUSTOMER__ALREADY_EXISTS"

    async def test_get_customer_200(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/customers",
            json={"external_ref": "GET-001", "full_name": "Getter"},
        )
        customer_id = create_resp.json()["data"]["id"]

        response = await client.get(f"/api/v1/customers/{customer_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] == customer_id
        assert body["data"]["full_name"] == "Getter"

    async def test_get_customer_404(self, client: AsyncClient) -> None:
        response = await client.get(f"/api/v1/customers/{uuid.uuid4()}")
        assert response.status_code == 404
        body = response.json()
        assert body["success"] is False
        assert body["error_code"] == "CUSTOMER__NOT_FOUND"

    async def test_list_customers_200(self, client: AsyncClient) -> None:
        await client.post(
            "/api/v1/customers",
            json={"external_ref": "LST-001", "full_name": "Alpha"},
        )
        await client.post(
            "/api/v1/customers",
            json={"external_ref": "LST-002", "full_name": "Beta"},
        )

        response = await client.get("/api/v1/customers")
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert body["total"] >= 2
        assert body["page"] == 1
        assert body["page_size"] == 20

    async def test_list_customers_with_filters(
        self, client: AsyncClient,
    ) -> None:
        await client.post(
            "/api/v1/customers",
            json={
                "external_ref": "FLT-001",
                "full_name": "Filtered",
                "customer_type": "prospect",
            },
        )
        await client.post(
            "/api/v1/customers",
            json={
                "external_ref": "FLT-002",
                "full_name": "Not Filtered",
                "customer_type": "active",
            },
        )

        response = await client.get(
            "/api/v1/customers?customer_type=prospect",
        )
        assert response.status_code == 200
        body = response.json()
        assert all(i["customer_type"] == "prospect" for i in body["data"])

    async def test_update_customer_200(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/customers",
            json={
                "external_ref": "UPD-001",
                "full_name": "Original",
            },
        )
        customer_id = create_resp.json()["data"]["id"]

        response = await client.patch(
            f"/api/v1/customers/{customer_id}",
            json={"full_name": "Updated"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["full_name"] == "Updated"

    async def test_update_nonexistent_customer_404(
        self, client: AsyncClient,
    ) -> None:
        response = await client.patch(
            f"/api/v1/customers/{uuid.uuid4()}",
            json={"full_name": "Nope"},
        )
        assert response.status_code == 404

    async def test_deactivate_customer_200(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/customers",
            json={"external_ref": "DEACT-001", "full_name": "Deactivator"},
        )
        customer_id = create_resp.json()["data"]["id"]

        response = await client.post(
            f"/api/v1/customers/{customer_id}/deactivate",
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["status"] == "inactive"

    async def test_activate_customer_200(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/customers",
            json={"external_ref": "ACT-001", "full_name": "Activator"},
        )
        customer_id = create_resp.json()["data"]["id"]

        await client.post(f"/api/v1/customers/{customer_id}/deactivate")
        response = await client.post(
            f"/api/v1/customers/{customer_id}/activate",
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["status"] == "active"

    async def test_archive_customer_200(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/api/v1/customers",
            json={"external_ref": "ARCH-001", "full_name": "Archer"},
        )
        customer_id = create_resp.json()["data"]["id"]

        response = await client.post(
            f"/api/v1/customers/{customer_id}/archive",
        )
        assert response.status_code == 200
        body = response.json()
        assert body["data"]["status"] == "archived"

    async def test_archive_archived_customer_422(
        self, client: AsyncClient,
    ) -> None:
        create_resp = await client.post(
            "/api/v1/customers",
            json={"external_ref": "ARCH-002", "full_name": "Double Arch"},
        )
        customer_id = create_resp.json()["data"]["id"]

        await client.post(f"/api/v1/customers/{customer_id}/archive")
        response = await client.post(
            f"/api/v1/customers/{customer_id}/archive",
        )
        assert response.status_code == 422
        body = response.json()
        assert body["error_code"] == "CUSTOMER__VALIDATION_ERROR"

    async def test_update_archived_customer_422(
        self, client: AsyncClient,
    ) -> None:
        create_resp = await client.post(
            "/api/v1/customers",
            json={"external_ref": "ARCH-UPD", "full_name": "Archived"},
        )
        customer_id = create_resp.json()["data"]["id"]

        await client.post(f"/api/v1/customers/{customer_id}/archive")
        response = await client.patch(
            f"/api/v1/customers/{customer_id}",
            json={"full_name": "Nope"},
        )
        assert response.status_code == 422
        body = response.json()
        assert body["error_code"] == "CUSTOMER__VALIDATION_ERROR"

"""Synthetic data and demo API unit tests."""

from app.demo.synthetic import generate_synthetic_data, get_synthetic_store


class TestSyntheticData:
    def setup_method(self) -> None:
        get_synthetic_store().clear()

    def test_generates_correct_counts(self) -> None:
        store = generate_synthetic_data()
        sizes = store.size()
        assert sizes["customers"] == 500
        assert sizes["interactions"] == 1500
        assert sizes["complaints"] == 800
        assert sizes["workflows"] == 800
        assert sizes["notifications"] == 800

    def test_customers_have_required_fields(self) -> None:
        store = generate_synthetic_data()
        for c in store.get("customers"):
            assert "id" in c
            assert "full_name" in c
            assert "email" in c
            assert "segment" in c
            assert "status" in c

    def test_complaints_have_required_fields(self) -> None:
        store = generate_synthetic_data()
        for c in store.get("complaints"):
            assert "id" in c
            assert "customer_id" in c
            assert "title" in c
            assert "category" in c
            assert "priority" in c
            assert "status" in c

    def test_complaints_have_link_to_customers(self) -> None:
        store = generate_synthetic_data()
        customer_ids = {c["id"] for c in store.get("customers")}
        for c in store.get("complaints"):
            assert c["customer_id"] in customer_ids

    def test_workflows_have_link_to_complaints(self) -> None:
        store = generate_synthetic_data()
        complaint_ids = {c["id"] for c in store.get("complaints")}
        for w in store.get("workflows"):
            assert w["complaint_id"] in complaint_ids

    def test_notifications_have_links(self) -> None:
        store = generate_synthetic_data()
        workflow_ids = {w["id"] for w in store.get("workflows")}
        complaint_ids = {c["id"] for c in store.get("complaints")}
        for n in store.get("notifications"):
            assert n["workflow_id"] in workflow_ids
            assert n["complaint_id"] in complaint_ids

    def test_clear_resets_data(self) -> None:
        generate_synthetic_data()
        get_synthetic_store().clear()
        assert len(get_synthetic_store().get("customers")) == 0

    def test_store_is_singleton(self) -> None:
        s1 = get_synthetic_store()
        s2 = get_synthetic_store()
        assert s1 is s2
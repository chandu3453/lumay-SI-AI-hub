"""Analytics service unit tests."""

from app.demo.synthetic import generate_synthetic_data, get_synthetic_store
from domains.analytics.services.analytics_service import AnalyticsService


class TestAnalyticsService:
    def setup_method(self) -> None:
        get_synthetic_store().clear()
        generate_synthetic_data()
        self.service = AnalyticsService()

    def test_compute_kpis(self) -> None:
        kpis = self.service.compute_kpis()
        assert kpis.total_customers == 500
        assert kpis.total_interactions == 1500
        assert kpis.total_complaints == 800
        assert kpis.total_workflows == 800
        assert kpis.total_notifications == 800

    def test_compute_trends(self) -> None:
        trends = self.service.compute_trends()
        assert len(trends.daily) > 0
        assert len(trends.category_distribution) > 0
        assert len(trends.sentiment_distribution) > 0

    def test_category_distribution_sum_to_100(self) -> None:
        trends = self.service.compute_trends()
        total_pct = sum(d.percentage for d in trends.category_distribution)
        assert abs(total_pct - 100.0) < 1.0

    def test_sla_compliance(self) -> None:
        sla = self.service.compute_sla()
        assert sla.within_sla >= 0
        assert sla.compliance_rate >= 0

    def test_department_workload(self) -> None:
        depts = self.service.compute_department_workload()
        assert len(depts) > 0

    def test_resolution_metrics(self) -> None:
        metrics = self.service.compute_resolution_metrics()
        assert metrics.avg_resolution_time_hours >= 0

    def test_customer_metrics(self) -> None:
        metrics = self.service.compute_customer_metrics()
        assert metrics.total_customers > 0
        assert len(metrics.customer_segments) > 0

    def test_workflow_analytics(self) -> None:
        analytics = self.service.compute_workflow_analytics()
        assert analytics.total > 0

    def test_notification_analytics(self) -> None:
        analytics = self.service.compute_notification_analytics()
        assert analytics.total > 0

    def test_generate_report(self) -> None:
        report = self.service.generate_report()
        assert report.kpis is not None
        assert report.trends is not None
        assert report.sla is not None
        assert report.report_generated_at != ""
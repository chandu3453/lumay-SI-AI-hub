"""Analytics Pydantic schemas — Analytics domain."""

from datetime import datetime
from typing import Any

from shared.base_schema import AppBaseModel


class DashboardKPIs(AppBaseModel):
    total_customers: int = 0
    total_interactions: int = 0
    total_complaints: int = 0
    total_workflows: int = 0
    total_notifications: int = 0
    open_complaints: int = 0
    resolved_complaints: int = 0
    avg_resolution_time_hours: float = 0.0
    sla_compliance_rate: float = 0.0
    active_workflows: int = 0
    avg_sentiment_score: float = 0.0
    critical_complaints: int = 0


class TrendPoint(AppBaseModel):
    date: str
    value: int | float


class CategoryDistribution(AppBaseModel):
    category: str
    count: int
    percentage: float


class SentimentDistribution(AppBaseModel):
    sentiment: str
    count: int
    percentage: float


class SeverityDistribution(AppBaseModel):
    severity: str
    count: int
    percentage: float


class PriorityDistribution(AppBaseModel):
    priority: str
    count: int
    percentage: float


class ComplaintTrends(AppBaseModel):
    daily: list[TrendPoint] = []
    weekly: list[TrendPoint] = []
    monthly: list[TrendPoint] = []
    category_distribution: list[CategoryDistribution] = []
    sentiment_distribution: list[SentimentDistribution] = []
    severity_distribution: list[SeverityDistribution] = []
    priority_distribution: list[PriorityDistribution] = []


class SLACompliance(AppBaseModel):
    within_sla: int = 0
    at_risk: int = 0
    breached: int = 0
    compliance_rate: float = 0.0


class DepartmentWorkload(AppBaseModel):
    department: str
    active_cases: int
    avg_resolution_time_hours: float
    backlog: int


class ResolutionMetrics(AppBaseModel):
    avg_resolution_time_hours: float = 0.0
    median_resolution_time_hours: float = 0.0
    resolved_last_7_days: int = 0
    resolved_last_30_days: int = 0
    resolution_by_category: list[CategoryDistribution] = []


class CustomerMetrics(AppBaseModel):
    total_customers: int = 0
    active_customers: int = 0
    customers_with_complaints: int = 0
    avg_complaints_per_customer: float = 0.0
    customer_segments: list[CategoryDistribution] = []


class WorkflowAnalytics(AppBaseModel):
    total: int = 0
    active: int = 0
    completed: int = 0
    by_status: list[CategoryDistribution] = []
    by_stage: list[CategoryDistribution] = []
    avg_completion_time_hours: float = 0.0


class NotificationAnalytics(AppBaseModel):
    total: int = 0
    sent: int = 0
    delivered: int = 0
    failed: int = 0
    by_channel: list[CategoryDistribution] = []
    delivery_rate: float = 0.0


class AIAnalytics(AppBaseModel):
    total_ai_requests: int = 0
    avg_latency_ms: float = 0.0
    total_tokens_used: int = 0
    estimated_cost: float = 0.0


class AnalyticsReport(AppBaseModel):
    kpis: DashboardKPIs = None
    trends: ComplaintTrends = None
    sla: SLACompliance = None
    departments: list[DepartmentWorkload] = []
    resolution: ResolutionMetrics = None
    customers: CustomerMetrics = None
    workflows: WorkflowAnalytics = None
    notifications: NotificationAnalytics = None
    ai: AIAnalytics = None
    report_generated_at: str = ""
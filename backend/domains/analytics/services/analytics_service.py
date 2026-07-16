"""Analytics Service — computes dashboard KPIs and trends from synthetic data."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.demo.synthetic import get_synthetic_store
from app.platform.logging import get_logger
from domains.analytics.schemas.analytics_schemas import (
    AIAnalytics,
    AnalyticsReport,
    CategoryDistribution,
    ComplaintTrends,
    CustomerMetrics,
    DashboardKPIs,
    DepartmentWorkload,
    NotificationAnalytics,
    PriorityDistribution,
    ResolutionMetrics,
    SLACompliance,
    SentimentDistribution,
    SeverityDistribution,
    TrendPoint,
    WorkflowAnalytics,
)

logger = get_logger(__name__)

COMPLAINT_STATUS_MAP = {
    "submitted": "open",
    "under_review": "open",
    "investigating": "open",
    "escalated": "open",
    "resolved": "resolved",
    "closed": "resolved",
    "archived": "resolved",
}


class AnalyticsService:
    def __init__(self) -> None:
        self._store = get_synthetic_store()

    def compute_kpis(self) -> DashboardKPIs:
        store = self._store
        customers = store.get("customers", [])
        interactions = store.get("interactions", [])
        complaints = store.get("complaints", [])
        workflows = store.get("workflows", [])
        notifications = store.get("notifications", [])

        open_complaints = sum(1 for c in complaints if COMPLAINT_STATUS_MAP.get(c.get("status", ""), "open") == "open")
        resolved_complaints = len(complaints) - open_complaints
        active_workflows = sum(1 for w in workflows if w.get("workflow_status") == "active")
        critical = sum(1 for c in complaints if c.get("priority") == "critical")

        sentiment_scores = [c.get("metadata", {}).get("ai_sentiment_polarity", 0.0) for c in complaints if c.get("metadata", {}).get("ai_sentiment_polarity") is not None]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0

        sla_ok = sum(1 for w in workflows if w.get("sla_status") == "within_sla")
        total_wf = len(workflows) or 1
        sla_rate = round((sla_ok / total_wf) * 100, 1)

        resolution_times = []
        for w in workflows:
            if w.get("workflow_status") == "completed" and w.get("started_at") and w.get("completed_at"):
                try:
                    start = datetime.fromisoformat(w["started_at"])
                    end = datetime.fromisoformat(w["completed_at"])
                    hours = (end - start).total_seconds() / 3600
                    resolution_times.append(hours)
                except (ValueError, TypeError):
                    pass
        avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else 0.0

        return DashboardKPIs(
            total_customers=len(customers),
            total_interactions=len(interactions),
            total_complaints=len(complaints),
            total_workflows=len(workflows),
            total_notifications=len(notifications),
            open_complaints=open_complaints,
            resolved_complaints=resolved_complaints,
            avg_resolution_time_hours=round(avg_resolution, 1),
            sla_compliance_rate=sla_rate,
            active_workflows=active_workflows,
            avg_sentiment_score=round(avg_sentiment, 2),
            critical_complaints=critical,
        )

    def compute_trends(self, granularity: str = "daily") -> ComplaintTrends:
        complaints = self._store.get("complaints", [])
        daily_map: dict[str, int] = {}
        weekly_map: dict[str, int] = {}
        monthly_map: dict[str, int] = {}
        cat_map: dict[str, int] = {}
        sent_map: dict[str, int] = {}
        sev_map: dict[str, int] = {}
        pri_map: dict[str, int] = {}

        for c in complaints:
            created = c.get("created_at", "")
            if created:
                try:
                    dt = datetime.fromisoformat(created)
                    daily_map[dt.strftime("%Y-%m-%d")] = daily_map.get(dt.strftime("%Y-%m-%d"), 0) + 1
                    weekly_map[dt.strftime("%Y-W%W")] = weekly_map.get(dt.strftime("%Y-W%W"), 0) + 1
                    monthly_map[dt.strftime("%Y-%m")] = monthly_map.get(dt.strftime("%Y-%m"), 0) + 1
                except (ValueError, TypeError):
                    pass
            cat = c.get("category", "unknown")
            cat_map[cat] = cat_map.get(cat, 0) + 1
            sent = c.get("metadata", {}).get("ai_sentiment", "neutral")
            sent_map[sent] = sent_map.get(sent, 0) + 1
            sev = c.get("severity", "moderate")
            sev_map[sev] = sev_map.get(sev, 0) + 1
            pri = c.get("priority", "medium")
            pri_map[pri] = pri_map.get(pri, 0) + 1

        total = len(complaints) or 1
        return ComplaintTrends(
            daily=[TrendPoint(date=d, value=v) for d, v in sorted(daily_map.items())],
            weekly=[TrendPoint(date=d, value=v) for d, v in sorted(weekly_map.items())],
            monthly=[TrendPoint(date=d, value=v) for d, v in sorted(monthly_map.items())],
            category_distribution=[CategoryDistribution(category=k, count=v, percentage=round(v / total * 100, 1)) for k, v in sorted(cat_map.items())],
            sentiment_distribution=[SentimentDistribution(sentiment=k, count=v, percentage=round(v / total * 100, 1)) for k, v in sorted(sent_map.items())],
            severity_distribution=[SeverityDistribution(severity=k, count=v, percentage=round(v / total * 100, 1)) for k, v in sorted(sev_map.items())],
            priority_distribution=[PriorityDistribution(priority=k, count=v, percentage=round(v / total * 100, 1)) for k, v in sorted(pri_map.items())],
        )

    def compute_sla(self) -> SLACompliance:
        workflows = self._store.get("workflows", [])
        within = sum(1 for w in workflows if w.get("sla_status") == "within_sla")
        at_risk = sum(1 for w in workflows if w.get("sla_status") == "at_risk")
        breached = sum(1 for w in workflows if w.get("sla_status") == "breached")
        total = len(workflows) or 1
        return SLACompliance(
            within_sla=within,
            at_risk=at_risk,
            breached=breached,
            compliance_rate=round((within / total) * 100, 1),
        )

    def compute_department_workload(self) -> list[DepartmentWorkload]:
        dept_map: dict[str, dict] = {}
        for w in self._store.get("workflows", []):
            team = w.get("assigned_team", "unassigned")
            if team not in dept_map:
                dept_map[team] = {"active_cases": 0, "resolution_times": [], "backlog": 0}
            if w.get("workflow_status") == "active":
                dept_map[team]["active_cases"] += 1
            if w.get("workflow_status") in ("pending", "suspended"):
                dept_map[team]["backlog"] += 1
            if w.get("workflow_status") == "completed" and w.get("started_at") and w.get("completed_at"):
                try:
                    start = datetime.fromisoformat(w["started_at"])
                    end = datetime.fromisoformat(w["completed_at"])
                    hours = (end - start).total_seconds() / 3600
                    dept_map[team]["resolution_times"].append(hours)
                except (ValueError, TypeError):
                    pass
        return [
            DepartmentWorkload(
                department=dept,
                active_cases=data["active_cases"],
                avg_resolution_time_hours=round(sum(data["resolution_times"]) / len(data["resolution_times"]), 1) if data["resolution_times"] else 0.0,
                backlog=data["backlog"],
            )
            for dept, data in sorted(dept_map.items())
        ]

    def compute_resolution_metrics(self) -> ResolutionMetrics:
        workflows = self._store.get("workflows", [])
        times = []
        for w in workflows:
            if w.get("workflow_status") == "completed" and w.get("started_at") and w.get("completed_at"):
                try:
                    start = datetime.fromisoformat(w["started_at"])
                    end = datetime.fromisoformat(w["completed_at"])
                    hours = (end - start).total_seconds() / 3600
                    times.append(hours)
                except (ValueError, TypeError):
                    pass
        avg = sum(times) / len(times) if times else 0.0
        sorted_times = sorted(times)
        median = sorted_times[len(sorted_times) // 2] if sorted_times else 0.0
        return ResolutionMetrics(
            avg_resolution_time_hours=round(avg, 1),
            median_resolution_time_hours=round(median, 1),
            resolved_last_7_days=sum(1 for w in workflows if w.get("completed_at") and self._within_days(w["completed_at"], 7)),
            resolved_last_30_days=sum(1 for w in workflows if w.get("completed_at") and self._within_days(w["completed_at"], 30)),
        )

    def compute_customer_metrics(self) -> CustomerMetrics:
        customers = self._store.get("customers", [])
        complaints = self._store.get("complaints", [])
        customer_ids = {c.get("id") for c in complaints}
        seg_map: dict[str, int] = {}
        for c in customers:
            seg = c.get("segment", "individual")
            seg_map[seg] = seg_map.get(seg, 0) + 1
        total = len(customers) or 1
        return CustomerMetrics(
            total_customers=len(customers),
            active_customers=sum(1 for c in customers if c.get("status") == "active"),
            customers_with_complaints=len(customer_ids),
            avg_complaints_per_customer=round(len(complaints) / max(len(customer_ids), 1), 2),
            customer_segments=[CategoryDistribution(category=k, count=v, percentage=round(v / total * 100, 1)) for k, v in sorted(seg_map.items())],
        )

    def compute_workflow_analytics(self) -> WorkflowAnalytics:
        workflows = self._store.get("workflows", [])
        status_map: dict[str, int] = {}
        stage_map: dict[str, int] = {}
        times = []
        for w in workflows:
            s = w.get("workflow_status", "unknown")
            status_map[s] = status_map.get(s, 0) + 1
            st = w.get("workflow_stage", "unknown")
            stage_map[st] = stage_map.get(st, 0) + 1
            if w.get("workflow_status") == "completed" and w.get("started_at") and w.get("completed_at"):
                try:
                    start = datetime.fromisoformat(w["started_at"])
                    end = datetime.fromisoformat(w["completed_at"])
                    hours = (end - start).total_seconds() / 3600
                    times.append(hours)
                except (ValueError, TypeError):
                    pass
        total = len(workflows) or 1
        return WorkflowAnalytics(
            total=len(workflows),
            active=sum(1 for w in workflows if w.get("workflow_status") == "active"),
            completed=sum(1 for w in workflows if w.get("workflow_status") == "completed"),
            by_status=[CategoryDistribution(category=k, count=v, percentage=round(v / total * 100, 1)) for k, v in sorted(status_map.items())],
            by_stage=[CategoryDistribution(category=k, count=v, percentage=round(v / total * 100, 1)) for k, v in sorted(stage_map.items())],
            avg_completion_time_hours=round(sum(times) / len(times), 1) if times else 0.0,
        )

    def compute_notification_analytics(self) -> NotificationAnalytics:
        notifications = self._store.get("notifications", [])
        channel_map: dict[str, int] = {}
        for n in notifications:
            ch = n.get("notification_channel", "unknown")
            channel_map[ch] = channel_map.get(ch, 0) + 1
        total = len(notifications) or 1
        sent = sum(1 for n in notifications if n.get("notification_status") in ("sent", "delivered"))
        delivered = sum(1 for n in notifications if n.get("notification_status") == "delivered")
        failed = sum(1 for n in notifications if n.get("notification_status") == "failed")
        return NotificationAnalytics(
            total=len(notifications),
            sent=sent,
            delivered=delivered,
            failed=failed,
            by_channel=[CategoryDistribution(category=k, count=v, percentage=round(v / total * 100, 1)) for k, v in sorted(channel_map.items())],
            delivery_rate=round((delivered / max(sent, 1)) * 100, 1),
        )

    def compute_ai_analytics(self) -> AIAnalytics:
        return AIAnalytics(
            total_ai_requests=0,
            avg_latency_ms=0.0,
            total_tokens_used=0,
            estimated_cost=0.0,
        )

    def generate_report(self) -> AnalyticsReport:
        return AnalyticsReport(
            kpis=self.compute_kpis(),
            trends=self.compute_trends(),
            sla=self.compute_sla(),
            departments=self.compute_department_workload(),
            resolution=self.compute_resolution_metrics(),
            customers=self.compute_customer_metrics(),
            workflows=self.compute_workflow_analytics(),
            notifications=self.compute_notification_analytics(),
            ai=self.compute_ai_analytics(),
            report_generated_at=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def _within_days(iso_date: str, days: int) -> bool:
        try:
            dt = datetime.fromisoformat(iso_date)
            delta = datetime.now(timezone.utc) - dt
            return delta.total_seconds() <= days * 86400
        except (ValueError, TypeError):
            return False

    # -----------------------------------------------------------------------
    # Phase 2 Analytics Methods (FR-004, FR-006, FR-007, FR-008, FR-003, FR-019)
    # -----------------------------------------------------------------------

    def compute_theme_distribution(self, days: int = 30) -> dict:
        """FR-004 / FR-015: 7-bucket theme distribution with counts and percentages."""
        complaints = self._store.get("complaints", [])
        recent = [c for c in complaints if self._within_days(c.get("created_at", ""), days)]
        themes = [
            "claims", "policy_and_coverage", "renewal_and_pricing",
            "customer_service", "provider_and_network", "digital_experience", "financial",
        ]
        theme_counts: dict[str, int] = {t: 0 for t in themes}

        for c in recent:
            t = c.get("theme") or c.get("metadata", {}).get("theme")
            if t and t in theme_counts:
                theme_counts[t] += 1

        total = max(sum(theme_counts.values()), 1)
        distribution = [
            {
                "theme": t,
                "label": t.replace("_", " ").title(),
                "count": cnt,
                "percentage": round(cnt / total * 100, 1),
            }
            for t, cnt in sorted(theme_counts.items(), key=lambda x: -x[1])
        ]
        return {
            "window_days": days,
            "total_complaints": len(recent),
            "distribution": distribution,
        }

    def compute_escalation_heatmap(self) -> dict:
        """FR-006 / FR-015: Escalation risk breakdown by band."""
        complaints = self._store.get("complaints", [])
        bands = {
            "critical": {"range": "76-100", "count": 0, "color": "#ef4444"},
            "high":     {"range": "51-75",  "count": 0, "color": "#f97316"},
            "medium":   {"range": "26-50",  "count": 0, "color": "#eab308"},
            "low":      {"range": "0-25",   "count": 0, "color": "#22c55e"},
        }
        for c in complaints:
            score = c.get("escalation_risk_score") or c.get("metadata", {}).get("escalation_risk_score") or 0
            if score >= 76:
                bands["critical"]["count"] += 1
            elif score >= 51:
                bands["high"]["count"] += 1
            elif score >= 26:
                bands["medium"]["count"] += 1
            else:
                bands["low"]["count"] += 1

        total = max(sum(b["count"] for b in bands.values()), 1)
        for band in bands.values():
            band["percentage"] = round(band["count"] / total * 100, 1)

        return {
            "total_complaints": len(complaints),
            "high_risk_count": bands["critical"]["count"] + bands["high"]["count"],
            "bands": bands,
        }

    def compute_sla_breach_summary(self) -> dict:
        """FR-007 / FR-015: SLA breach probability distribution."""
        complaints = self._store.get("complaints", [])
        within_sla = at_risk = breached = 0
        total_prob = 0
        count_with_prob = 0

        for c in complaints:
            sla_risk = c.get("sla_risk") or c.get("metadata", {}).get("sla_risk", "within_sla")
            prob = c.get("sla_breach_probability") or c.get("metadata", {}).get("sla_breach_probability") or 0
            if prob:
                total_prob += prob
                count_with_prob += 1
            if sla_risk == "breached":
                breached += 1
            elif sla_risk == "at_risk":
                at_risk += 1
            else:
                within_sla += 1

        total = max(len(complaints), 1)
        return {
            "total": len(complaints),
            "within_sla": within_sla,
            "at_risk": at_risk,
            "breached": breached,
            "within_sla_pct": round(within_sla / total * 100, 1),
            "at_risk_pct": round(at_risk / total * 100, 1),
            "breached_pct": round(breached / total * 100, 1),
            "avg_breach_probability": round(total_prob / count_with_prob, 1) if count_with_prob else 0,
        }

    def compute_repeat_rate(self) -> dict:
        """FR-008 / FR-015: Repeat complaint rate by time window."""
        complaints = self._store.get("complaints", [])
        repeat_30 = repeat_60 = repeat_90 = 0
        total = len(complaints)

        for c in complaints:
            is_repeat = c.get("is_repeat") or c.get("metadata", {}).get("is_repeat", False)
            window = c.get("repeat_window_days") or c.get("metadata", {}).get("repeat_window_days")
            if is_repeat and window:
                if window <= 30:
                    repeat_30 += 1
                elif window <= 60:
                    repeat_60 += 1
                elif window <= 90:
                    repeat_90 += 1

        total_repeats = repeat_30 + repeat_60 + repeat_90
        return {
            "total_complaints": total,
            "total_repeat": total_repeats,
            "repeat_rate_pct": round(total_repeats / max(total, 1) * 100, 1),
            "by_window": {
                "30_days": {"count": repeat_30, "pct": round(repeat_30 / max(total, 1) * 100, 1)},
                "60_days": {"count": repeat_60, "pct": round(repeat_60 / max(total, 1) * 100, 1)},
                "90_days": {"count": repeat_90, "pct": round(repeat_90 / max(total, 1) * 100, 1)},
            },
        }

    def compute_sentiment_trend(self, days: int = 30) -> dict:
        """FR-003 / FR-015: Rolling sentiment distribution and trend direction."""
        complaints = self._store.get("complaints", [])
        recent = [c for c in complaints if self._within_days(c.get("created_at", ""), days)]

        sentiment_counts: dict[str, int] = {
            "very_positive": 0, "positive": 0, "neutral": 0, "negative": 0, "very_negative": 0,
        }
        improving = declining = stable = 0

        for c in recent:
            s = c.get("sentiment") or c.get("metadata", {}).get("sentiment", "neutral")
            if s in sentiment_counts:
                sentiment_counts[s] += 1
            trend = c.get("sentiment_trend") or c.get("metadata", {}).get("sentiment_trend")
            if trend == "improving":
                improving += 1
            elif trend == "declining":
                declining += 1
            else:
                stable += 1

        total = max(len(recent), 1)
        weights = {"very_positive": 2, "positive": 1, "neutral": 0, "negative": -1, "very_negative": -2}
        polarity = sum(sentiment_counts[s] * w for s, w in weights.items()) / total

        return {
            "window_days": days,
            "total": len(recent),
            "sentiment_distribution": {
                s: {"count": cnt, "pct": round(cnt / total * 100, 1)}
                for s, cnt in sentiment_counts.items()
            },
            "trend_distribution": {"improving": improving, "declining": declining, "stable": stable},
            "avg_polarity": round(polarity, 3),
            "overall_trend": "improving" if polarity > 0.2 else "declining" if polarity < -0.2 else "stable",
        }

    def compute_language_split(self) -> dict:
        """FR-019 / FR-015: Language distribution (AR / EN / Mixed)."""
        complaints = self._store.get("complaints", [])
        lang_counts: dict[str, int] = {"en": 0, "ar": 0, "mixed": 0, "other": 0}

        for c in complaints:
            lang = c.get("detected_language") or c.get("metadata", {}).get("detected_language", "en")
            key = lang if lang in lang_counts else "other"
            lang_counts[key] += 1

        total = max(sum(lang_counts.values()), 1)
        return {
            "total": len(complaints),
            "distribution": {
                lang: {"count": cnt, "pct": round(cnt / total * 100, 1)}
                for lang, cnt in lang_counts.items()
            },
            "arabic_complaint_percentage": round(
                (lang_counts["ar"] + lang_counts["mixed"]) / total * 100, 1
            ),
        }

    def compute_spike_detection(self, window_days: int = 7, baseline_days: int = 30) -> dict:
        """FR-015: Detect complaint volume spikes vs historical baseline."""
        complaints = self._store.get("complaints", [])
        current_window = [c for c in complaints if self._within_days(c.get("created_at", ""), window_days)]
        baseline_window = [c for c in complaints if self._within_days(c.get("created_at", ""), baseline_days)]

        current_count = len(current_window)
        baseline_avg = len(baseline_window) / max(baseline_days / window_days, 1)
        spike_ratio = round(current_count / max(baseline_avg, 1), 2)
        is_spike = spike_ratio >= 1.5

        # Theme spikes
        theme_current: dict[str, int] = {}
        theme_baseline: dict[str, int] = {}
        for c in current_window:
            t = c.get("theme") or "unknown"
            theme_current[t] = theme_current.get(t, 0) + 1
        for c in baseline_window:
            t = c.get("theme") or "unknown"
            theme_baseline[t] = theme_baseline.get(t, 0) + 1

        emerging_themes = []
        for theme, cnt in theme_current.items():
            baseline_cnt = theme_baseline.get(theme, 0) / max(baseline_days / window_days, 1)
            ratio = round(cnt / max(baseline_cnt, 1), 2)
            if ratio >= 1.5:
                emerging_themes.append({
                    "theme": theme,
                    "label": theme.replace("_", " ").title(),
                    "current_count": cnt,
                    "baseline_avg": round(baseline_cnt, 1),
                    "spike_ratio": ratio,
                })

        emerging_themes.sort(key=lambda x: -x["spike_ratio"])

        return {
            "window_days": window_days,
            "baseline_days": baseline_days,
            "current_count": current_count,
            "baseline_avg": round(baseline_avg, 1),
            "spike_ratio": spike_ratio,
            "is_spike": is_spike,
            "spike_severity": "critical" if spike_ratio >= 2.0 else "high" if spike_ratio >= 1.5 else "normal",
            "emerging_themes": emerging_themes[:5],
        }

    def compute_provider_breakdown(self, days: int = 30) -> dict:
        """FR-015: Complaints by provider/garage theme with volume."""
        complaints = self._store.get("complaints", [])
        recent = [c for c in complaints if self._within_days(c.get("created_at", ""), days)]

        provider_complaints = [
            c for c in recent
            if c.get("theme") == "provider_and_network"
            or (c.get("metadata", {}) or {}).get("theme") == "provider_and_network"
        ]

        subcategory_map: dict[str, int] = {}
        for c in provider_complaints:
            sub = c.get("subcategory") or c.get("metadata", {}).get("subcategory", "Unknown Provider")
            subcategory_map[sub] = subcategory_map.get(sub, 0) + 1

        total = max(len(provider_complaints), 1)
        breakdown = sorted(
            [
                {
                    "provider": k,
                    "count": v,
                    "pct": round(v / total * 100, 1),
                }
                for k, v in subcategory_map.items()
            ],
            key=lambda x: -x["count"],
        )

        return {
            "window_days": days,
            "total_provider_complaints": len(provider_complaints),
            "total_complaints": len(recent),
            "provider_complaint_rate_pct": round(len(provider_complaints) / max(len(recent), 1) * 100, 1),
            "breakdown": breakdown[:10],
        }

    def compute_product_breakdown(self, days: int = 30) -> dict:
        """FR-015: Complaints by insurance product type."""
        complaints = self._store.get("complaints", [])
        recent = [c for c in complaints if self._within_days(c.get("created_at", ""), days)]

        product_map: dict[str, int] = {}
        for c in recent:
            product = (
                c.get("product")
                or c.get("metadata", {}).get("product")
                or c.get("category")
                or "general"
            )
            product_map[product] = product_map.get(product, 0) + 1

        total = max(sum(product_map.values()), 1)
        breakdown = sorted(
            [
                {
                    "product": k,
                    "label": k.replace("_", " ").title(),
                    "count": v,
                    "pct": round(v / total * 100, 1),
                }
                for k, v in product_map.items()
            ],
            key=lambda x: -x["count"],
        )

        return {
            "window_days": days,
            "total_complaints": len(recent),
            "breakdown": breakdown,
        }
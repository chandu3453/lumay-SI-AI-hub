import { api } from "@/services/api-client";

export const analyticsService = {
  async getDashboardSummary() {
    return api.get("/analytics/dashboard");
  },

  async getReport(type: string, params?: { from?: string; to?: string }) {
    return api.get(`/analytics/reports/${type}`, { params });
  },

  // Core analytics
  async getKPIs() {
    return api.get("/analytics/kpis");
  },

  async getTrends(granularity: "daily" | "weekly" | "monthly" = "daily") {
    return api.get("/analytics/trends", { params: { granularity } });
  },

  async getSLA() {
    return api.get("/analytics/sla");
  },

  async getDepartments() {
    return api.get("/analytics/departments");
  },

  async getResolution() {
    return api.get("/analytics/resolution");
  },

  async getCustomerMetrics() {
    return api.get("/analytics/customers");
  },

  async getWorkflowAnalytics() {
    return api.get("/analytics/workflows");
  },

  async getNotificationAnalytics() {
    return api.get("/analytics/notifications");
  },

  async getFullReport() {
    return api.get("/analytics/report");
  },

  // Phase 2 analytics (FR-015)
  async getThemeDistribution(days = 30) {
    return api.get("/analytics/themes", { params: { days } });
  },

  async getEscalationHeatmap() {
    return api.get("/analytics/escalation-heatmap");
  },

  async getSLABreachSummary() {
    return api.get("/analytics/sla-breach-summary");
  },

  async getRepeatRate() {
    return api.get("/analytics/repeat-rate");
  },

  async getSentimentTrend(days = 30) {
    return api.get("/analytics/sentiment-trend", { params: { days } });
  },

  async getLanguageSplit() {
    return api.get("/analytics/language-split");
  },

  // FR-015 — Spike detection & breakdown
  async getSpikeDetection(windowDays = 7, baselineDays = 30) {
    return api.get("/analytics/spikes", {
      params: { window_days: windowDays, baseline_days: baselineDays },
    });
  },

  async getProviderBreakdown(days = 30) {
    return api.get("/analytics/provider-breakdown", { params: { days } });
  },

  async getProductBreakdown(days = 30) {
    return api.get("/analytics/product-breakdown", { params: { days } });
  },
};

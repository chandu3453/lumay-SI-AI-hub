import { api } from "@/services/api-client";
import type { DashboardKPIs, ComplaintTrends, AnalyticsReport, SearchResults, KnowledgeSearchResult, ScenarioResult } from "@/types/domain";

export const demoService = {
  async loadData() {
    return api.post("/demo/load");
  },

  async reset() {
    return api.post("/demo/reset");
  },

  async run() {
    return api.post("/demo/run");
  },

  async health() {
    return api.get("/demo/health");
  },

  async getOverview() {
    return api.get("/demo/dashboard/overview");
  },

  async getKPIs() {
    return api.get("/demo/dashboard/kpis");
  },

  async getTrends(granularity = "daily") {
    return api.get(`/demo/dashboard/trends`, { params: { granularity } });
  },

  async search(query: string, limit = 20) {
    return api.get(`/demo/dashboard/search`, { params: { query, limit } });
  },

  async knowledge(query: string, source?: string) {
    return api.get(`/demo/dashboard/knowledge`, { params: { query, source } });
  },

  async askQuestion(question: string) {
    return api.get(`/demo/dashboard/knowledge/ask`, { params: { question } });
  },

  async getReports() {
    return api.get("/demo/dashboard/reports");
  },

  async scenarioCustomerComplaint() {
    return api.post("/demo/scenario/customer-complaint");
  },

  async scenarioKnowledgeSearch(query: string) {
    return api.post("/demo/scenario/knowledge-search", { query });
  },

  async scenarioDuplicateDetection() {
    return api.post("/demo/scenario/duplicate-detection");
  },

  async scenarioDashboard() {
    return api.post("/demo/scenario/dashboard");
  },

  async scenarioFullDemo() {
    return api.post("/demo/scenario/full-demo");
  },

  // Simulation endpoints (Sprint 19)
  async simulateComplaint() {
    return api.post("/demo/simulate/complaint");
  },
  async simulateInteraction() {
    return api.post("/demo/simulate/interaction");
  },
  async simulateAIDecision() {
    return api.post("/demo/simulate/ai-decision");
  },
  async simulateFull() {
    return api.post("/demo/simulate/full");
  },
  async getEventHistory(limit = 50) {
    return api.get("/demo/events/history", { params: { limit } });
  },
};
export const APP_NAME = "lumay-si-ai-hub";
export const APP_DESCRIPTION = "Enterprise AI-Powered Insurance Complaints & Sentiment Intelligence Platform";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";
export const API_PREFIX = "/api/v1";

export const PAGINATION_DEFAULT_PAGE_SIZE = 20;
export const PAGINATION_MAX_PAGE_SIZE = 500;

export const TOAST_DURATION = 5000;

export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  DASHBOARD: "/dashboard",
  CUSTOMERS: "/customers",
  INTERACTIONS: "/interactions",
  COMPLAINTS: "/complaints",
  COMPLAINT_CASES: "/complaint-cases",
  WORKFLOW: "/workflow",
  LIVE_ALERTS: "/live-alerts",
  NOTIFICATIONS: "/notifications",
  REPORTS: "/reports",
  ANALYTICS: "/analytics",
  ENTERPRISE_ANALYTICS: "/enterprise-analytics",
  SEARCH: "/search",
  KNOWLEDGE: "/knowledge",
  ADMINISTRATION: "/administration",
  SETTINGS: "/settings",
} as const;
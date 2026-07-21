import { api } from "@/services/api-client";
import { API_BASE_URL, API_PREFIX } from "@/lib/constants";
import type {
  ConversationAnalyticsSummary,
  ConversationDistributions,
  ConversationTrends,
  Customer360Response,
  CustomerActivityTimelineResponse,
  EmployeeAnalyticsItem,
  ExportFormat,
  ExportReport,
  ReportingQueryFilters,
  SupervisorDashboard,
} from "@/features/reporting/types";

interface SuccessResponse<T> {
  success: boolean;
  data: T;
}

export const reportingService = {
  async getCustomer360(customerId: string) {
    return api.get<SuccessResponse<Customer360Response>>(`/customers/${customerId}/360`);
  },

  async getCustomerActivity(customerId: string, page = 1, pageSize = 50) {
    return api.get<SuccessResponse<CustomerActivityTimelineResponse>>(
      `/customers/${customerId}/activity`,
      { params: { page, page_size: pageSize } },
    );
  },

  async getConversationSummary(filters?: ReportingQueryFilters) {
    return api.get<SuccessResponse<ConversationAnalyticsSummary>>(
      "/reporting/conversations/summary",
      { params: filters },
    );
  },

  async getDistributions(filters?: ReportingQueryFilters) {
    return api.get<SuccessResponse<ConversationDistributions>>(
      "/reporting/conversations/distributions",
      { params: filters },
    );
  },

  async getTrends(granularity: "day" | "week" | "month" = "day", filters?: ReportingQueryFilters) {
    return api.get<SuccessResponse<ConversationTrends>>("/reporting/conversations/trends", {
      params: { granularity, date_from: filters?.date_from, date_to: filters?.date_to },
    });
  },

  async getEmployeeAnalytics(filters?: ReportingQueryFilters) {
    return api.get<SuccessResponse<EmployeeAnalyticsItem[]>>("/reporting/employees", {
      params: filters,
    });
  },

  async getSupervisorDashboard() {
    return api.get<SuccessResponse<SupervisorDashboard>>("/reporting/supervisor/dashboard");
  },

  /** Not a fetch — builds the download URL for a plain `<a href>`/`window.open`,
   * so no CSV/Excel library is needed on the frontend at all (the backend
   * generates the file). Absolute backend origin, same as
   * conversations.service.ts's streamUrl() — this app has no dev-server
   * rewrite proxying /api/v1 to the backend. */
  exportUrl(report: ExportReport, format: ExportFormat, filters?: ReportingQueryFilters): string {
    const params = new URLSearchParams({ format, ...sanitizeFilters(filters) });
    return `${API_BASE_URL}${API_PREFIX}/reporting/export/${report}?${params.toString()}`;
  },
};

function sanitizeFilters(filters?: ReportingQueryFilters): Record<string, string> {
  if (!filters) return {};
  const out: Record<string, string> = {};
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== null && value !== "") out[key] = String(value);
  }
  return out;
}

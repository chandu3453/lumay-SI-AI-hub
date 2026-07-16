import { api } from "@/services/api-client";

export type AlertItem = {
  id: string;
  created_at: string;
  updated_at: string;
  channel?: string;
  customer_name?: string;
  policy_number?: string;
  product?: string;
  alert_type?: string;
  ai_summary?: string;
  severity?: string;
  sla_risk?: string;
  status?: string;
  complaint_id?: string | null;
  customer_id?: string | null;
  workflow_id?: string | null;
  notification_id?: string | null;
};

export const liveAlertsService = {
  async list(params?: {
    page?: number;
    page_size?: number;
    severity?: string;
    channel?: string;
    status?: string;
  }) {
    return api.get("/notifications", { params });
  },
};
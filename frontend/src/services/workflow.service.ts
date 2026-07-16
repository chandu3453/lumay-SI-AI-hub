import { api } from "@/services/api-client";
import type { PaginatedResponse } from "@/types/common";
import type { Workflow } from "@/types/domain";

export const workflowService = {
  async list(params?: {
    page?: number;
    page_size?: number;
    status?: string;
    search?: string;
    channel?: string;
    theme?: string;
    severity?: string;
    sla_status?: string;
    assigned_to?: string;
    date_from?: string;
    date_to?: string;
    sort_by?: string;
    sort_dir?: string;
  }) {
    return api.get<PaginatedResponse<Workflow>>("/workflows", { params });
  },

  async getById(id: string) {
    return api.get(`/workflows/${id}`);
  },
};

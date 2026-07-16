import { api } from "@/services/api-client";
import type { PaginatedResponse } from "@/types/common";
import type { Customer } from "@/types/domain";

export const customersService = {
  async list(params?: {
    page?: number;
    page_size?: number;
    search?: string;
    segment?: string;
    risk_level?: string;
    customer_type?: string;
    date_from?: string;
    date_to?: string;
    sort_by?: string;
    sort_dir?: string;
  }) {
    return api.get<PaginatedResponse<Customer>>("/customers", { params });
  },

  async getById(id: string) {
    return api.get(`/customers/${id}`);
  },

  async create(data: Partial<Customer>) {
    return api.post("/customers", data);
  },
};

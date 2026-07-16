import { api } from "@/services/api-client";
import type { Notification } from "@/types/domain";

export const notificationsService = {
  async list(params?: { page?: number; page_size?: number; status?: string }) {
    return api.get("/notifications", { params });
  },
  async getById(id: string) {
    return api.get(`/notifications/${id}`);
  },
};
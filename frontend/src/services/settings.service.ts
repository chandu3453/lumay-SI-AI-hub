import { api } from "@/services/api-client";

export const settingsService = {
  async getConfig() {
    return api.get("/config");
  },

  async updateConfig(key: string, value: unknown) {
    return api.put(`/config/${key}`, { value });
  },
};

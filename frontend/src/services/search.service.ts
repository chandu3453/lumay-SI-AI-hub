import { api } from "@/services/api-client";

export const searchService = {
  async search(query: string, index?: string, params?: { page?: number; page_size?: number }) {
    return api.get<{ data: { query: string; complaints: unknown[]; customers: unknown[]; interactions: unknown[]; workflows: unknown[]; knowledge: unknown[] } }>("/search", {
      params: { q: query, index, ...params },
    });
  },
};

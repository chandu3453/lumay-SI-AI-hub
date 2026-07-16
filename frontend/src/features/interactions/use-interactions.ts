"use client";

import { useQuery } from "@tanstack/react-query";
import { interactionsService } from "@/services/interactions.service";

export function useInteractions(params?: {
  page?: number;
  page_size?: number;
  channel?: string;
  status?: string;
  priority?: string;
  search?: string;
  sort_by?: string;
  sort_dir?: string;
}) {
  return useQuery({
    queryKey: ["interactions", params],
    queryFn: async () => {
      const res = await interactionsService.list(params);
      const data = res.data.data ?? [];
      const total = (res.data as any).total ?? data.length;
      return { items: data, total };
    },
    retry: 1,
  });
}
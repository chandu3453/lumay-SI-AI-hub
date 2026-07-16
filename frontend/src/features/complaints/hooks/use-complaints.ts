"use client";

import { useQuery } from "@tanstack/react-query";
import { complaintsService } from "@/services/complaints.service";

export function useComplaintList(params?: {
  page?: number;
  page_size?: number;
  status?: string;
  priority?: string;
  search?: string;
  channel?: string;
  theme?: string;
  severity?: string;
  sla_status?: string;
  date_from?: string;
  date_to?: string;
  sort_by?: string;
  sort_dir?: string;
  assigned_to_me?: boolean;
  tab?: string;
}) {
  return useQuery({
    queryKey: ["complaints", "list", params],
    queryFn: async () => {
      const res = await complaintsService.list(params);
      const data = res.data.data ?? [];
      const total = (res.data as any).total ?? data.length;
      return { items: data, total };
    },
    retry: 1,
  });
}

export function useComplaintKPIs() {
  return useQuery({
    queryKey: ["complaints", "kpis"],
    queryFn: async () => {
      const res = await complaintsService.list({ page: 1, page_size: 1 });
      const total = (res.data as any).total ?? 0;
      return {
        total_complaints: total,
        high_risk: Math.round(total * 0.15),
        sla_at_risk: Math.round(total * 0.22),
        overdue: Math.round(total * 0.08),
        resolved_this_week: Math.round(total * 0.12),
      };
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useComplaintTabCounts() {
  return useQuery({
    queryKey: ["complaints", "tab-counts"],
    queryFn: async () => {
      const res = await complaintsService.list({ page: 1, page_size: 1000 });
      const items = res.data.data ?? [];
      const total = items.length;
      return {
        all: total,
        open: items.filter((c: any) => c.status === "open" || c.status === "submitted" || c.status === "under_review" || c.status === "investigating").length,
        open_count: items.filter((c: any) => c.status === "open" || c.status === "submitted" || c.status === "under_review" || c.status === "investigating").length,
        assigned_to_me: items.filter((c: any) => c.assigned_agent_id).length,
        high_risk: items.filter((c: any) => c.priority === "high" || c.priority === "critical" || c.is_high_risk).length,
        critical: items.filter((c: any) => c.priority === "critical" || c.severity === "critical").length,
        overdue: items.filter((c: any) => c.is_overdue || c.sla_status === "overdue" || c.sla_status === "breached").length,
        resolved: items.filter((c: any) => c.status === "resolved").length,
        closed: items.filter((c: any) => c.status === "closed" || c.status === "archived").length,
        repeat: items.filter((c: any) => c.is_repeat).length,
      };
    },
    staleTime: 15_000,
    retry: 1,
  });
}
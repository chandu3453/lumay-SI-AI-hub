"use client";

import { useQuery } from "@tanstack/react-query";
import { complaintsService } from "@/services/complaints.service";

// Mirrors the real `ComplaintSummary` shape returned by GET /complaints —
// no customer/agent identity fields exist at list scope (that requires a
// per-complaint fetch), so the table shows queue/category identifiers
// instead of fabricating a name, same "honest placeholder" pattern Customer
// 360 already uses for data that isn't available at this scope.
export type CaseItem = {
  id: string;
  created_at: string;
  case_number: string | null;
  category: string;
  priority: string;
  severity: string;
  status: string;
  assigned_queue: string | null;
  theme: string | null;
  channel: string | null;
  product: string | null;
  sla_risk: string | null;
  is_repeat: boolean | null;
};

const STATUS_TAB_FILTER: Record<string, string | undefined> = {
  all: undefined,
  new: "submitted",
  acknowledged: "under_review",
  in_progress: "investigating",
  pending_review: "under_review",
  resolved: "resolved",
  closed: "closed",
  escalated: "escalated",
  overdue: undefined,
};

export function tabToComplaintFilter(tab: string): { status?: string; sla_risk?: string } {
  if (tab === "overdue") return { sla_risk: "breached" };
  const status = STATUS_TAB_FILTER[tab];
  return status ? { status } : {};
}

export function useComplaintCases(params?: {
  page?: number;
  page_size?: number;
  status?: string;
  search?: string;
  channel?: string;
  theme?: string;
  severity?: string;
  sla_risk?: string;
  product?: string;
}) {
  return useQuery({
    queryKey: ["complaint-cases", params],
    queryFn: async () => {
      const res = await complaintsService.list(params);
      const items = (res.data.data ?? []) as unknown as CaseItem[];
      const total = (res.data as { total?: number }).total ?? items.length;
      return { items, total };
    },
    retry: 1,
  });
}

export function useComplaintCaseKPIs() {
  return useQuery({
    queryKey: ["complaint-cases", "kpis"],
    queryFn: async () => {
      const res = await complaintsService.list({ page: 1, page_size: 200 });
      const items = (res.data.data ?? []) as unknown as CaseItem[];
      const total = (res.data as { total?: number }).total ?? items.length;
      const inProgress = items.filter((c) => c.status === "investigating" || c.status === "under_review").length;
      const overdue = items.filter((c) => c.sla_risk === "breached").length;
      const resolved = items.filter((c) => c.status === "resolved" || c.status === "closed").length;
      return {
        total_cases: total,
        in_progress: inProgress,
        overdue,
        avg_resolution_time: null as number | null,
        resolved_this_month: resolved,
      };
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useComplaintCaseTabCounts() {
  return useQuery({
    queryKey: ["complaint-cases", "tab-counts"],
    queryFn: async () => {
      const res = await complaintsService.list({ page: 1, page_size: 200 });
      const items = (res.data.data ?? []) as unknown as CaseItem[];
      return {
        all: items.length,
        new: items.filter((c) => c.status === "submitted").length,
        acknowledged: items.filter((c) => c.status === "under_review").length,
        in_progress: items.filter((c) => c.status === "investigating").length,
        pending_review: items.filter((c) => c.status === "under_review").length,
        resolved: items.filter((c) => c.status === "resolved").length,
        closed: items.filter((c) => c.status === "closed" || c.status === "archived").length,
        escalated: items.filter((c) => c.status === "escalated").length,
        overdue: items.filter((c) => c.sla_risk === "breached").length,
      };
    },
    staleTime: 15_000,
    retry: 1,
  });
}

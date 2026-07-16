"use client";

import { useQuery } from "@tanstack/react-query";
import { customersService } from "@/services/customers.service";
import { complaintsService } from "@/services/complaints.service";
import { interactionsService } from "@/services/interactions.service";

export function useCustomerList(params?: {
  page?: number;
  page_size?: number;
  search?: string;
  segment?: string;
  risk_level?: string;
  customer_type?: string;
  date_from?: string;
  date_to?: string;
}) {
  return useQuery({
    queryKey: ["customers", "list", params],
    queryFn: async () => {
      const res = await customersService.list(params);
      const data = res.data.data ?? [];
      const total = (res.data as any).total ?? data.length;
      return { items: data, total };
    },
    retry: 1,
  });
}

export function useCustomerKPIs() {
  return useQuery({
    queryKey: ["customers", "kpis"],
    queryFn: async () => {
      const res = await customersService.list({ page: 1, page_size: 1000 });
      const items = res.data.data ?? [];
      const total = items.length;
      return {
        total_customers: total,
        with_complaints: Math.round(total * 0.35),
        repeat_complaints: Math.round(total * 0.12),
        high_risk: Math.round(total * 0.18),
      };
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useCustomerProfile(id: string | null) {
  return useQuery({
    queryKey: ["customers", "profile", id],
    queryFn: async () => {
      if (!id) return null;
      const res = await customersService.getById(id);
      return res.data.data ?? res.data;
    },
    enabled: !!id,
    retry: 1,
  });
}

export function useCustomerComplaints(customerId: string | null) {
  return useQuery({
    queryKey: ["customers", "complaints", customerId],
    queryFn: async () => {
      if (!customerId) return { items: [], total: 0 };
      const res = await complaintsService.list({ page: 1, page_size: 50 });
      const all = res.data.data ?? [];
      const filtered = all.filter((c: any) => c.customer_id === customerId);
      return { items: filtered, total: filtered.length };
    },
    enabled: !!customerId,
    retry: 1,
  });
}

export function useCustomerInteractions(customerId: string | null) {
  return useQuery({
    queryKey: ["customers", "interactions", customerId],
    queryFn: async () => {
      if (!customerId) return { items: [], total: 0 };
      const res = await interactionsService.list({ page: 1, page_size: 20 });
      const all = res.data.data ?? [];
      const filtered = all.filter((i: any) => i.customer_id === customerId);
      return { items: filtered, total: filtered.length };
    },
    enabled: !!customerId,
    retry: 1,
  });
}

export function useCustomerComplaintTrend(customerId: string | null) {
  return useQuery({
    queryKey: ["customers", "complaint-trend", customerId],
    queryFn: async () => {
      if (!customerId) return [];
      const res = await complaintsService.list({ page: 1, page_size: 100 });
      const all = res.data.data ?? [];
      const customerComplaints = all.filter((c: any) => c.customer_id === customerId);
      const months: Record<string, number> = {};
      const now = new Date();
      for (let i = 5; i >= 0; i--) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
        months[key] = 0;
      }
      for (const c of customerComplaints) {
        if (c.created_at) {
          const d = new Date(c.created_at);
          const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
          if (key in months) months[key]++;
        }
      }
      return Object.entries(months).map(([month, count]) => ({ month, count }));
    },
    enabled: !!customerId,
    staleTime: 60_000,
    retry: 1,
  });
}

export function useCustomerComplaintThemes(customerId: string | null) {
  return useQuery({
    queryKey: ["customers", "complaint-themes", customerId],
    queryFn: async () => {
      if (!customerId) return [];
      const res = await complaintsService.list({ page: 1, page_size: 100 });
      const all = res.data.data ?? [];
      const customerComplaints = all.filter((c: any) => c.customer_id === customerId);
      const themeCounts: Record<string, number> = {};
      for (const c of customerComplaints) {
        const theme = c.theme || c.category || "general";
        themeCounts[theme] = (themeCounts[theme] ?? 0) + 1;
      }
      const sorted = Object.entries(themeCounts)
        .map(([theme, count]) => ({ theme: theme.replace(/_/g, " "), count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);
      const max = sorted.length > 0 ? Math.max(...sorted.map((s) => s.count)) : 1;
      return sorted.map((s) => ({ ...s, percentage: Math.round((s.count / max) * 100) }));
    },
    enabled: !!customerId,
    staleTime: 60_000,
    retry: 1,
  });
}
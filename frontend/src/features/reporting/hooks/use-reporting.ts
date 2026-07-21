"use client";

import { useQuery } from "@tanstack/react-query";

import { reportingService } from "@/services/reporting.service";
import type { ReportingQueryFilters } from "@/features/reporting/types";

export const reportingKeys = {
  all: ["reporting"] as const,
  customer360: (id: string) => ["reporting", "customer360", id] as const,
  customerActivity: (id: string, page: number) => ["reporting", "customer-activity", id, page] as const,
  summary: (filters?: ReportingQueryFilters) => ["reporting", "summary", filters] as const,
  distributions: (filters?: ReportingQueryFilters) => ["reporting", "distributions", filters] as const,
  trends: (granularity: string, filters?: ReportingQueryFilters) =>
    ["reporting", "trends", granularity, filters] as const,
  employees: (filters?: ReportingQueryFilters) => ["reporting", "employees", filters] as const,
  supervisorDashboard: ["reporting", "supervisor-dashboard"] as const,
};

export function useCustomer360(customerId: string | null) {
  return useQuery({
    queryKey: reportingKeys.customer360(customerId ?? ""),
    queryFn: async () => {
      if (!customerId) return null;
      const res = await reportingService.getCustomer360(customerId);
      return res.data.data;
    },
    enabled: !!customerId,
    retry: 1,
  });
}

export function useCustomerActivity(customerId: string | null, page = 1, pageSize = 50) {
  return useQuery({
    queryKey: reportingKeys.customerActivity(customerId ?? "", page),
    queryFn: async () => {
      if (!customerId) return { items: [], total: 0, page: 1, page_size: pageSize };
      const res = await reportingService.getCustomerActivity(customerId, page, pageSize);
      return res.data.data;
    },
    enabled: !!customerId,
    retry: 1,
  });
}

export function useConversationSummary(filters?: ReportingQueryFilters) {
  return useQuery({
    queryKey: reportingKeys.summary(filters),
    queryFn: async () => (await reportingService.getConversationSummary(filters)).data.data,
    retry: 1,
  });
}

export function useConversationDistributions(filters?: ReportingQueryFilters) {
  return useQuery({
    queryKey: reportingKeys.distributions(filters),
    queryFn: async () => (await reportingService.getDistributions(filters)).data.data,
    retry: 1,
  });
}

export function useConversationTrends(
  granularity: "day" | "week" | "month" = "day",
  filters?: ReportingQueryFilters,
) {
  return useQuery({
    queryKey: reportingKeys.trends(granularity, filters),
    queryFn: async () => (await reportingService.getTrends(granularity, filters)).data.data,
    retry: 1,
  });
}

export function useEmployeeAnalytics(filters?: ReportingQueryFilters) {
  return useQuery({
    queryKey: reportingKeys.employees(filters),
    queryFn: async () => (await reportingService.getEmployeeAnalytics(filters)).data.data,
    retry: 1,
  });
}

export function useSupervisorDashboard() {
  return useQuery({
    queryKey: reportingKeys.supervisorDashboard,
    queryFn: async () => (await reportingService.getSupervisorDashboard()).data.data,
    // Live view — poll rather than wait for an SSE wire-up (Supervisor
    // Dashboard is a snapshot read, not a per-conversation subscription).
    refetchInterval: 15_000,
    retry: 1,
  });
}

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { demoService } from "@/services/demo.service";
import { complaintsService } from "@/services/complaints.service";
import { customersService } from "@/services/customers.service";
import { workflowService } from "@/services/workflow.service";
import { notificationsService } from "@/services/notifications.service";
import { searchService } from "@/services/search.service";

export function useDemoHealth() {
  return useQuery({
    queryKey: ["demo", "health"],
    queryFn: async () => {
      const res = await demoService.health();
      return res.data.data;
    },
    retry: 1,
    staleTime: 10_000,
  });
}

export function useLoadDemo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const res = await demoService.loadData();
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["demo"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["complaints"] });
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      queryClient.invalidateQueries({ queryKey: ["workflows"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      window.dispatchEvent(new CustomEvent("demo-data-loaded"));
    },
  });
}

export function useDemoReady() {
  const health = useDemoHealth();
  const loadDemo = useLoadDemo();

  const needsLoad = health.isSuccess && !health.data?.data_loaded;
  const isLoading = health.isLoading || loadDemo.isPending;

  if (needsLoad && !loadDemo.isPending && !loadDemo.isSuccess) {
    loadDemo.mutate();
  }

  return {
    isReady: health.isSuccess && health.data?.data_loaded,
    isLoading,
    entityCounts: health.data?.entity_counts ?? {},
    totalEntities: health.data?.total_entities ?? 0,
    reload: () => loadDemo.mutate(),
  };
}

export function useDashboardKPIs() {
  return useQuery({
    queryKey: ["dashboard", "kpis"],
    queryFn: async () => {
      const res = await demoService.getOverview();
      return res.data.data;
    },
    refetchInterval: 30_000,
    retry: 2,
  });
}

export function useDashboardTrends(granularity = "daily") {
  return useQuery({
    queryKey: ["dashboard", "trends", granularity],
    queryFn: async () => {
      const res = await demoService.getTrends(granularity);
      return res.data.data;
    },
    retry: 2,
  });
}

export function useDashboardReport() {
  return useQuery({
    queryKey: ["dashboard", "report"],
    queryFn: async () => {
      const res = await demoService.getReports();
      return res.data.data;
    },
    retry: 2,
  });
}

export function useSearch(query: string) {
  return useQuery({
    queryKey: ["search", query],
    queryFn: async () => {
      if (!query) return { query: "", complaints: [], customers: [], interactions: [], workflows: [], knowledge: [] };
      const res = await demoService.search(query);
      return res.data.data;
    },
    enabled: query.length > 0,
    retry: 1,
  });
}

export function useAskQuestion(question: string) {
  return useQuery({
    queryKey: ["ai", "ask", question],
    queryFn: async () => {
      const res = await demoService.askQuestion(question);
      return res.data.data;
    },
    enabled: question.length > 0,
    retry: 1,
  });
}

export function useKnowledgeSearch(query: string, source?: string) {
  return useQuery({
    queryKey: ["knowledge", query, source],
    queryFn: async () => {
      const res = await demoService.knowledge(query, source);
      return res.data.data;
    },
    enabled: query.length > 0,
    retry: 1,
  });
}

export function useComplaints(params?: { page?: number; page_size?: number; status?: string }) {
  return useQuery({
    queryKey: ["complaints", params],
    queryFn: async () => {
      const res = await complaintsService.list(params);
      const data = res.data.data ?? [];
      const total = (res.data as any).total ?? data.length;
      return { items: data, total };
    },
    retry: 1,
  });
}

export function useCustomers(params?: { page?: number; page_size?: number }) {
  return useQuery({
    queryKey: ["customers", params],
    queryFn: async () => {
      const res = await customersService.list(params);
      const data = res.data.data ?? [];
      const total = (res.data as any).total ?? data.length;
      return { items: data, total };
    },
    retry: 1,
  });
}

export function useWorkflows(params?: { page?: number; page_size?: number; status?: string }) {
  return useQuery({
    queryKey: ["workflows", params],
    queryFn: async () => {
      const res = await workflowService.list(params);
      const data = res.data.data ?? [];
      const total = (res.data as any).total ?? data.length;
      return { items: data, total };
    },
    retry: 1,
  });
}

export function useNotifications(params?: { page?: number; page_size?: number; status?: string }) {
  return useQuery({
    queryKey: ["notifications", params],
    queryFn: async () => {
      const res = await notificationsService.list(params);
      const data = res.data.data ?? [];
      const total = (res.data as any).total ?? data.length;
      return { items: data, total };
    },
    retry: 1,
  });
}

export function useScenarioCustomerComplaint() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const res = await demoService.scenarioCustomerComplaint();
      return res.data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["complaints"] });
      queryClient.invalidateQueries({ queryKey: ["complaint-cases"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["workflows"] });
    },
  });
}

export function useScenarioDuplicateDetection() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const res = await demoService.scenarioDuplicateDetection();
      return res.data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["complaints"] });
      queryClient.invalidateQueries({ queryKey: ["complaint-cases"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useScenarioFullDemo() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const res = await demoService.scenarioFullDemo();
      return res.data.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["demo"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["complaints"] });
      queryClient.invalidateQueries({ queryKey: ["complaint-cases"] });
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      queryClient.invalidateQueries({ queryKey: ["workflows"] });
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
      queryClient.invalidateQueries({ queryKey: ["analytics"] });
    },
  });
}
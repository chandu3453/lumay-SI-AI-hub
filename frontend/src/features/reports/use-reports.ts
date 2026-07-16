"use client";

import { useQuery } from "@tanstack/react-query";
import { demoService } from "@/services/demo.service";
import { analyticsService } from "@/services/analytics.service";

const TYPES = ["Complaint Overview", "SLA Performance", "Sentiment Analysis", "Theme & Root Cause", "Channel Performance", "Escalation & Risk"] as const;
const FORMATS = ["PDF", "XLSX", "CSV"] as const;

function randomItem<T>(arr: readonly T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomDate(daysBack: number): string {
  const d = new Date(Date.now() - Math.floor(Math.random() * daysBack * 86400000));
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function randomName(): string {
  const first = ["Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry", "Iris", "Jack"];
  const last = ["Smith", "Jones", "Lee", "Garcia", "Brown", "Wilson", "Taylor", "Thomas", "White", "Harris"];
  return `${first[Math.floor(Math.random() * first.length)]} ${last[Math.floor(Math.random() * last.length)]}`;
}

export type ReportItem = {
  id: string;
  name: string;
  description: string;
  type: string;
  period: string;
  generated_on: string;
  generated_by: string;
  format: string;
};

export type ScheduledReport = {
  id: string;
  name: string;
  frequency: string;
  next_run: string;
  format: string;
  recipients: string[];
  status: "active" | "paused" | "error";
};

export function useReportsList(tab: string = "my-reports") {
  return useQuery({
    queryKey: ["reports", "list", tab],
    queryFn: async () => {
      const res = await demoService.getReports();
      const backend = res.data.data ?? {};
      const reports = backend.reports ?? backend.items ?? [];
      if (Array.isArray(reports) && reports.length > 0) {
        return reports.map((r: any, i: number) => ({
          id: r.id ?? `r-${i}`,
          name: r.name ?? r.title ?? `Report ${i + 1}`,
          description: r.description ?? "",
          type: r.type ?? randomItem(TYPES),
          period: r.period ?? "Last 30 days",
          generated_on: r.generated_on ?? r.created_at ?? randomDate(30),
          generated_by: r.generated_by ?? randomName(),
          format: r.format ?? randomItem(FORMATS),
        }));
      }
      return Array.from({ length: 12 }).map((_, i) => ({
        id: `r-${i + 1}`,
        name: `${randomItem(TYPES)} - ${new Date(Date.now() - i * 86400000 * 3).toLocaleDateString("en-US", { month: "short", day: "numeric" })}`,
        description: `Detailed analysis of ${["complaint trends", "SLA metrics", "sentiment shifts", "root causes", "channel efficiency", "risk patterns"][i % 6]}`,
        type: TYPES[i % TYPES.length],
        period: ["Last 7 days", "Last 30 days", "Last 90 days", "Custom Range"][i % 4],
        generated_on: randomDate(30),
        generated_by: randomName(),
        format: randomItem(FORMATS),
      }));
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useScheduledReports() {
  return useQuery({
    queryKey: ["reports", "scheduled"],
    queryFn: async () => {
      return Array.from({ length: 5 }).map((_, i) => ({
        id: `sched-${i + 1}`,
        name: ["Daily High Risk Alert Report", "Weekly SLA Compliance Report", "Monthly Sentiment Analysis", "Weekly Complaint Overview", "Monthly Executive Summary"][i],
        frequency: ["Daily", "Weekly", "Monthly", "Weekly", "Monthly"][i],
        next_run: ["Tomorrow 08:00", "Mon, Jul 21 08:00", "Aug 1, 2026 09:00", "Mon, Jul 21 08:00", "Aug 1, 2026 09:00"][i],
        format: ["PDF", "PDF", "XLSX", "PDF", "PDF"][i],
        recipients: [["alerts@lumay.ai"], ["compliance@lumay.ai"], ["exec@lumay.ai"], ["managers@lumay.ai"], ["board@lumay.ai"]][i],
        status: (["active", "active", "active", "paused", "active"] as const)[i],
      }));
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useReportTrends() {
  return useQuery<{ date: string; total: number; resolved: number; high_risk: number }[]>({
    queryKey: ["reports", "trends"],
    queryFn: async () => {
      const res = await demoService.getTrends("daily");
      const data = res.data.data ?? {};
      const daily = data.daily ?? [];
      return daily.map((d: any, i: number) => ({
        date: d.date,
        total: d.value ?? Math.round(Math.random() * 30 + 10),
        resolved: Math.round((d.value ?? 10) * 0.4),
        high_risk: Math.round((d.value ?? 10) * 0.18),
      }));
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useSeverityDistribution() {
  return useQuery<{ name: string; value: number; color: string }[]>({
    queryKey: ["reports", "severity"],
    queryFn: async () => {
      const res = await demoService.getTrends("daily");
      const data = res.data.data ?? {};
      const sev = data.severity_distribution ?? [];
      if (sev.length > 0) {
        return sev.map((s: any) => ({ name: s.severity ?? s.category ?? "Unknown", value: s.count, color: s.severity === "high" || s.severity === "critical" ? "#DC2626" : s.severity === "medium" ? "#F59E0B" : "#16A34A" }));
      }
      return [
        { name: "High", value: Math.round(120 * 0.32), color: "#DC2626" },
        { name: "Medium", value: Math.round(120 * 0.41), color: "#F59E0B" },
        { name: "Low", value: Math.round(120 * 0.27), color: "#16A34A" },
      ];
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useTopThemes() {
  return useQuery<{ name: string; count: number }[]>({
    queryKey: ["reports", "themes"],
    queryFn: async () => {
      const res = await demoService.getReports();
      const data = res.data.data ?? {};
      const themes = data.themes ?? data.category_distribution ?? [];
      if (themes.length > 0) {
        return themes.slice(0, 5).map((t: any) => ({ name: t.category ?? t.theme ?? t.name ?? "Unknown", count: t.count ?? t.value ?? 0 }));
      }
      return [
        { name: "Claim Delays", count: 42 },
        { name: "Service Quality", count: 35 },
        { name: "Payments", count: 28 },
        { name: "Communication", count: 22 },
        { name: "Policy Coverage", count: 18 },
      ];
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useInsuranceReport(reportType: string) {
  return useQuery({
    queryKey: ["reports", "insurance", reportType],
    queryFn: async () => {
      return {
        generated: true,
        type: reportType,
        timestamp: new Date().toISOString(),
        entries: Array.from({ length: 20 }).map((_, i) => ({
          id: `ir-${i}`,
          insurance_line: ["Motor", "Medical & Health", "Travel", "Home", "Life", "Business Insurance"][i % 6],
          complaint_count: Math.round(Math.random() * 50 + 5),
          resolved: Math.round(Math.random() * 30 + 2),
          avg_resolution_hours: Math.round(Math.random() * 48 + 4),
          sla_compliance: Math.round(Math.random() * 30 + 65),
        })),
      };
    },
    staleTime: 60_000,
    retry: 1,
  });
}

export type { TYPES, FORMATS };

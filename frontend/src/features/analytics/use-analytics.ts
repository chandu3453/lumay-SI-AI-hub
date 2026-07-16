"use client";

import { useQuery } from "@tanstack/react-query";
import { demoService } from "@/services/demo.service";
import { complaintsService } from "@/services/complaints.service";
import { workflowService } from "@/services/workflow.service";

export function useAnalyticsKPIs() {
  return useQuery({
    queryKey: ["analytics", "kpis"],
    queryFn: async () => {
      try {
        const res = await demoService.getOverview();
        const overview = res.data.data ?? {};
        const complaintsRes = await complaintsService.list({ page: 1, page_size: 1 });
        const totalComplaints = (complaintsRes.data as any).total ?? 0;
        
        if (!totalComplaints) {
          return {
            total_complaints: 2456,
            high_risk: 312,
            resolved: 642,
            avg_resolution_time_hours: 86,
            sla_breach_rate: 7.4,
            escalated_cases: 186,
            escalation_rate: 7.6,
            regulatory_risk_cases: 28,
            repeat_complaint_rate: 24.3,
          };
        }

        return {
          total_complaints: totalComplaints,
          high_risk: overview.critical_complaints ?? Math.round(totalComplaints * 0.15),
          resolved: overview.resolved_complaints ?? Math.round(totalComplaints * 0.35),
          avg_resolution_time_hours: overview.avg_resolution_time_hours ?? 48,
          sla_breach_rate: overview.sla_compliance_rate != null ? 100 - overview.sla_compliance_rate : 7.4,
          escalated_cases: Math.round(totalComplaints * 0.08) || 186,
          escalation_rate: 7.6,
          regulatory_risk_cases: Math.round(totalComplaints * 0.01) || 28,
          repeat_complaint_rate: 24.3,
        };
      } catch {}
      return {
        total_complaints: 2456,
        high_risk: 312,
        resolved: 642,
        avg_resolution_time_hours: 86,
        sla_breach_rate: 7.4,
        escalated_cases: 186,
        escalation_rate: 7.6,
        regulatory_risk_cases: 28,
        repeat_complaint_rate: 24.3,
      };
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useAnalyticsTrends(granularity = "daily") {
  return useQuery({
    queryKey: ["analytics", "trends", granularity],
    queryFn: async () => {
      const res = await demoService.getTrends(granularity);
      const data = res.data.data ?? {};
      const daily = data.daily ?? [];
      const weekly = data.weekly ?? [];
      const monthly = data.monthly ?? [];
      const categoryDist = data.category_distribution ?? [];
      const sentimentDist = data.sentiment_distribution ?? [];

      const trendData = daily.map((d: any, i: number) => ({
        date: d.date,
        total: d.value ?? Math.round(Math.random() * 30 + 10),
        high_risk: Math.round((d.value ?? 10) * 0.2),
        resolved: Math.round((d.value ?? 10) * 0.35),
      }));

      return {
        daily: trendData,
        weekly,
        monthly,
        category_distribution: categoryDist,
        sentiment_distribution: sentimentDist,
      };
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useAnalyticsReport() {
  return useQuery({
    queryKey: ["analytics", "report"],
    queryFn: async () => {
      const res = await demoService.getReports();
      return res.data.data ?? {};
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useChannelDistribution() {
  return useQuery({
    queryKey: ["analytics", "channel-distribution"],
    queryFn: async () => {
      const res = await complaintsService.list({ page: 1, page_size: 500 });
      const items = res.data.data ?? [];
      const channelCounts: Record<string, number> = {};
      for (const c of items) {
        const ch = c.channel || c.source || "other";
        channelCounts[ch] = (channelCounts[ch] ?? 0) + 1;
      }
      const total = items.length || 1;
      const channels = ["voice", "whatsapp", "email", "web_chat", "smart_call", "crm", "manual"];
      const others = ["other", "in_app", "mobile_chat"];
      const result: { name: string; value: number; percentage: number; color: string }[] = [];
      const colors = ["#2563EB", "#16A34A", "#8B5CF6", "#F59E0B", "#EC4899", "#06B6D4", "#F97316"];
      let otherCount = 0;
      channels.forEach((ch, i) => {
        const count = channelCounts[ch] ?? 0;
        if (count > 0) result.push({ name: ch.replace(/_/g, " "), value: count, percentage: Math.round((count / total) * 100), color: colors[i % colors.length] });
        else otherCount += channelCounts[ch] ?? 0;
      });
      others.forEach((ch) => { otherCount += channelCounts[ch] ?? 0; });
      if (otherCount > 0) result.push({ name: "Others", value: otherCount, percentage: Math.round((otherCount / total) * 100), color: "#94A3B8" });
      return { items: result, total: items.length };
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useSLAStatus() {
  return useQuery({
    queryKey: ["analytics", "sla-status"],
    queryFn: async () => {
      const res = await workflowService.list({ page: 1, page_size: 500 });
      const items = res.data.data ?? [];
      let onTrack = 0, atRisk = 0, overdue = 0;
      for (const w of items) {
        if (w.sla_status === "on_track" || w.sla_status === "completed") onTrack++;
        else if (w.sla_status === "at_risk") atRisk++;
        else if (w.sla_status === "overdue" || w.sla_status === "breached") overdue++;
        else onTrack++;
      }
      const total = items.length || 1;
      return [
        { name: "On Track", value: onTrack, percentage: Math.round((onTrack / total) * 100), color: "#16A34A" },
        { name: "At Risk", value: atRisk, percentage: Math.round((atRisk / total) * 100), color: "#F59E0B" },
        { name: "Overdue", value: overdue, percentage: Math.round((overdue / total) * 100), color: "#DC2626" },
      ];
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useSentimentTrend(days = 30) {
  return useQuery({
    queryKey: ["analytics", "sentiment-trend", days],
    queryFn: async () => {
      try {
        const res = await analyticsService.getSentimentTrend(days);
        const data = (res as any)?.data?.data ?? (res as any)?.data;
        if (data && (data.history || data.daily)) {
          return data;
        }
      } catch {}
      return {
        history: [
          { date: "May 10", positive: 45, neutral: 35, negative: 20 },
          { date: "May 11", positive: 48, neutral: 34, negative: 18 },
          { date: "May 12", positive: 47, neutral: 33, negative: 20 },
          { date: "May 13", positive: 50, neutral: 32, negative: 18 },
          { date: "May 14", positive: 52, neutral: 33, negative: 15 },
          { date: "May 15", positive: 49, neutral: 34, negative: 17 },
          { date: "May 16", positive: 53, neutral: 32, negative: 15 },
        ]
      };
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useBranchAnalytics() {
  return useQuery({
    queryKey: ["analytics", "branches"],
    queryFn: async () => {
      const res = await complaintsService.list({ page: 1, page_size: 500 });
      const items = res.data.data ?? [];
      const branches = ["Main Branch", "North Branch", "South Branch", "East Branch", "West Branch", "Central Hub", "City Office"];
      return branches.map((name, i) => {
        const total = Math.round(items.length * (0.1 + Math.random() * 0.15));
        const highRisk = Math.round(total * (0.1 + Math.random() * 0.2));
        const resolved = Math.round(total * (0.3 + Math.random() * 0.3));
        const breached = Math.round(total * (0.05 + Math.random() * 0.15));
        return { name, total, high_risk: highRisk, resolved, sla_breach_rate: Math.round((breached / Math.max(total, 1)) * 100) };
      }).sort((a, b) => b.total - a.total);
    },
    staleTime: 60_000,
    retry: 1,
  });
}

export function useRecurringIssues() {
  return useQuery({
    queryKey: ["analytics", "recurring-issues"],
    queryFn: async () => {
      const issues = [
        { issue: "Claim processing delays", trend: 12.5 },
        { issue: "Poor customer service response", trend: -5.2 },
        { issue: "Payment refund delays", trend: 8.3 },
        { issue: "Policy coverage disputes", trend: -2.1 },
        { issue: "Communication breakdown", trend: 15.7 },
      ];
      return issues.map((item, i) => ({
        issue: item.issue,
        related_cases: Math.round(20 + Math.random() * 80),
        trend: item.trend,
        sparkline: Array.from({ length: 8 }, () => Math.round(Math.random() * 50 + 10)),
      }));
    },
    staleTime: 60_000,
    retry: 1,
  });
}

export function useComplaintsByInsurance() {
  return useQuery({
    queryKey: ["analytics", "complaints-by-insurance"],
    queryFn: async () => {
      return [
        { name: "Motor", value: 145, color: "#2563EB" },
        { name: "Medical & Health", value: 98, color: "#16A34A" },
        { name: "Travel", value: 67, color: "#8B5CF6" },
        { name: "Home", value: 52, color: "#F59E0B" },
        { name: "Life", value: 38, color: "#EC4899" },
        { name: "Business Insurance", value: 29, color: "#06B6D4" },
        { name: "Other", value: 44, color: "#94A3B8" },
      ];
    },
    staleTime: 60_000,
    retry: 1,
  });
}

export function useCasesByInsurance() {
  return useQuery({
    queryKey: ["analytics", "cases-by-insurance"],
    queryFn: async () => {
      return [
        { name: "Motor", open: 42, resolved: 88, color: "#2563EB" },
        { name: "Medical & Health", open: 28, resolved: 62, color: "#16A34A" },
        { name: "Travel", open: 19, resolved: 41, color: "#8B5CF6" },
        { name: "Home", open: 15, resolved: 33, color: "#F59E0B" },
        { name: "Life", open: 11, resolved: 24, color: "#EC4899" },
        { name: "Business Insurance", open: 8, resolved: 19, color: "#06B6D4" },
      ];
    },
    staleTime: 60_000,
    retry: 1,
  });
}

export function useHighRiskByInsurance() {
  return useQuery({
    queryKey: ["analytics", "high-risk-by-insurance"],
    queryFn: async () => {
      return [
        { name: "Motor", value: 32, color: "#DC2626" },
        { name: "Medical & Health", value: 21, color: "#F59E0B" },
        { name: "Travel", value: 14, color: "#F97316" },
        { name: "Home", value: 11, color: "#EC4899" },
        { name: "Life", value: 7, color: "#8B5CF6" },
        { name: "Business Insurance", value: 5, color: "#06B6D4" },
      ];
    },
    staleTime: 60_000,
    retry: 1,
  });
}

export function useResolutionByInsurance() {
  return useQuery({
    queryKey: ["analytics", "resolution-by-insurance"],
    queryFn: async () => {
      return [
        { name: "Motor", hours: 28, color: "#2563EB" },
        { name: "Medical & Health", hours: 22, color: "#16A34A" },
        { name: "Travel", hours: 18, color: "#8B5CF6" },
        { name: "Home", hours: 32, color: "#F59E0B" },
        { name: "Life", hours: 26, color: "#EC4899" },
        { name: "Business Insurance", hours: 36, color: "#06B6D4" },
      ];
    },
    staleTime: 60_000,
    retry: 1,
  });
}

// ---------------------------------------------------------------------------
// Phase 2 Analytics Hooks — live from backend API (FR-015)
// ---------------------------------------------------------------------------

import { analyticsService } from "@/services/analytics.service";

export function useThemeDistribution(days = 30) {
  return useQuery({
    queryKey: ["analytics", "themes", days],
    queryFn: async () => {
      const res = await analyticsService.getThemeDistribution(days);
      return (res as any)?.data?.data ?? (res as any)?.data ?? null;
    },
    staleTime: 60_000,
    retry: 1,
  });
}

export function useEscalationHeatmap() {
  return useQuery({
    queryKey: ["analytics", "escalation-heatmap"],
    queryFn: async () => {
      const res = await analyticsService.getEscalationHeatmap();
      return (res as any)?.data?.data ?? (res as any)?.data ?? null;
    },
    staleTime: 60_000,
    retry: 1,
  });
}

export function useSLABreachSummary() {
  return useQuery({
    queryKey: ["analytics", "sla-breach-summary"],
    queryFn: async () => {
      const res = await analyticsService.getSLABreachSummary();
      return (res as any)?.data?.data ?? (res as any)?.data ?? null;
    },
    staleTime: 60_000,
    retry: 1,
  });
}

export function useRepeatRate() {
  return useQuery({
    queryKey: ["analytics", "repeat-rate"],
    queryFn: async () => {
      const res = await analyticsService.getRepeatRate();
      return (res as any)?.data?.data ?? (res as any)?.data ?? null;
    },
    staleTime: 60_000,
    retry: 1,
  });
}

export function useLanguageSplit() {
  return useQuery({
    queryKey: ["analytics", "language-split"],
    queryFn: async () => {
      const res = await analyticsService.getLanguageSplit();
      return (res as any)?.data?.data ?? (res as any)?.data ?? null;
    },
    staleTime: 60_000,
    retry: 1,
  });
}

export function useSpikeDetection(windowDays = 7, baselineDays = 30) {
  return useQuery({
    queryKey: ["analytics", "spikes", windowDays, baselineDays],
    queryFn: async () => {
      const res = await analyticsService.getSpikeDetection(windowDays, baselineDays);
      return (res as any)?.data?.data ?? (res as any)?.data ?? null;
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useProviderBreakdown(days = 30) {
  return useQuery({
    queryKey: ["analytics", "provider-breakdown", days],
    queryFn: async () => {
      const res = await analyticsService.getProviderBreakdown(days);
      return (res as any)?.data?.data ?? (res as any)?.data ?? null;
    },
    staleTime: 60_000,
    retry: 1,
  });
}

export function useProductBreakdown(days = 30) {
  return useQuery({
    queryKey: ["analytics", "product-breakdown", days],
    queryFn: async () => {
      const res = await analyticsService.getProductBreakdown(days);
      return (res as any)?.data?.data ?? (res as any)?.data ?? null;
    },
    staleTime: 60_000,
    retry: 1,
  });
}
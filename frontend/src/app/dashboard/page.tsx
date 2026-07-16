"use client";

import { useEffect } from "react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { KPICard } from "@/components/dashboard/KPICard";
import { TrendChart } from "@/components/dashboard/TrendChart";
import { SentimentChart } from "@/components/dashboard/SentimentChart";
import { ComplaintThemes } from "@/components/dashboard/ComplaintThemes";
import { RecentComplaintsTable } from "@/components/dashboard/RecentComplaintsTable";
import { LiveAlertsPanel } from "@/components/dashboard/LiveAlertsPanel";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { useLoadDemo } from "@/features/dashboard/use-dashboard";
import { DemoModeToggle } from "@/components/demo/demo-mode-toggle";
import { DemoScenarios } from "@/components/demo/demo-scenarios";
import { DemoTimeline } from "@/components/demo/demo-timeline";
import { LiveInteractionBadge } from "@/components/demo/live-interaction-badge";
import { AIDecisionPanel } from "@/components/demo/ai-decision-panel";
import { CustomerJourneyTimeline } from "@/components/demo/customer-journey-timeline";
import { ExecutiveMetrics } from "@/components/demo/executive-metrics";
import { useDemoSSE } from "@/hooks/use-demo-sse";
import { useDemoStore } from "@/stores/demo.store";
import { Calendar, SlidersHorizontal, FileText, AlertTriangle, Clock, Gauge, FolderClosed, RefreshCw } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "@/services/analytics.service";

function useLiveKPIs() {
  return useQuery({
    queryKey: ["analytics", "kpis"],
    queryFn: () => analyticsService.getKPIs().then((r: any) => r?.data?.data ?? r?.data ?? null),
    refetchInterval: 60_000,
  });
}

function fmt(n: number | null | undefined, suffix = ""): string {
  if (n == null) return "—";
  if (n >= 1000) return (n / 1000).toFixed(1) + "K" + suffix;
  return n.toString() + suffix;
}

export default function DashboardPage() {
  const loadDemo = useLoadDemo();
  const { data: kpis, isLoading: kpisLoading } = useLiveKPIs();
  const demoEnabled = useDemoStore((s) => s.enabled);

  useDemoSSE();

  useEffect(() => {
    if (loadDemo.isIdle) loadDemo.mutate();
  }, []);

  return (
    <DashboardShell>
      <LiveInteractionBadge />
      <div className="space-y-8 animate-fade-in">
        {/* Top Header Row with Filters */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-5">
          <div className="space-y-0.5 text-left">
            <h1 className="text-2xl font-extrabold tracking-tight text-[#0F172A]">Dashboard</h1>
            <p className="text-sm font-medium text-[#64748B]">Overview of complaint intelligence</p>
          </div>
          <div className="flex items-center gap-3">
            <DemoModeToggle />
            <button className="flex h-10 items-center gap-2.5 rounded-xl border border-[#E2E8F0] bg-white px-4 py-2 text-xs font-bold text-[#334155] shadow-sm hover:bg-[#F8FAFC] transition-all">
              <Calendar className="h-4 w-4 text-[#64748B]" />
              <span>Today</span>
            </button>
            <button className="flex h-10 items-center gap-2.5 rounded-xl border border-[#E2E8F0] bg-white px-4 py-2 text-xs font-bold text-[#334155] shadow-sm hover:bg-[#F8FAFC] transition-all">
              <SlidersHorizontal className="h-4 w-4 text-[#64748B]" />
              <span>All Channels</span>
            </button>
            {kpisLoading && (
              <span className="flex items-center gap-1 text-xs text-[#64748B]">
                <RefreshCw className="h-3.5 w-3.5 animate-spin" /> Loading live data...
              </span>
            )}
          </div>
        </div>

        {/* Stats Row (5 Cards) — live from /analytics/kpis */}
        <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-5">
          <KPICard
            icon={<FileText className="h-5 w-5 text-[#0052FF]" />}
            iconBg="bg-blue-50 border-blue-100"
            label="Total Complaints"
            value={kpis ? fmt(kpis.total_complaints ?? 2568) : "2,568"}
            trend={18.4}
            trendUp={true}
            trendColor="green"
            trendSuffix="vs last 7 days"
          />
          <KPICard
            icon={<AlertTriangle className="h-5 w-5 text-red-600" />}
            iconBg="bg-red-50 border-red-100"
            label="High Risk"
            value={kpis ? fmt(kpis.critical_complaints ?? 128) : "128"}
            trend={12.3}
            trendUp={true}
            trendColor="red"
            trendSuffix="vs last 7 days"
          />
          <KPICard
            icon={<Clock className="h-5 w-5 text-amber-600" />}
            iconBg="bg-amber-50 border-amber-100"
            label="SLA at Risk"
            value={kpis ? fmt(kpis.sla_at_risk ?? 96) : "96"}
            trend={8.7}
            trendUp={true}
            trendColor="orange"
            trendSuffix="vs last 7 days"
          />
          <KPICard
            icon={<Gauge className="h-5 w-5 text-green-600" />}
            iconBg="bg-green-50 border-green-100"
            label="Avg. Resolution Time"
            value={kpis ? `${kpis.avg_resolution_time_days ?? 3.6} Days` : "3.6 Days"}
            trend={5.2}
            trendUp={false}
            trendColor="green"
            trendSuffix="vs last 7 days"
          />
          <KPICard
            icon={<FolderClosed className="h-5 w-5 text-purple-600" />}
            iconBg="bg-purple-50 border-purple-100"
            label="Open Complaints"
            value={kpis ? fmt(kpis.open_complaints ?? 1543) : "1,543"}
            trend={0}
            trendColor="gray"
            trendSuffix="no change"
          />
        </div>

        {/* Live Executive Metrics (shown when Demo Mode is on) */}
        {demoEnabled && <ExecutiveMetrics />}

        {/* Main Content: split into main + demo sidebar when demo mode is on */}
        <div className={demoEnabled ? "grid gap-8 lg:grid-cols-[1fr_320px]" : ""}>
          <div className="space-y-8">
            {/* Middle Charts Grid Layout */}
            <div className="grid gap-8 lg:grid-cols-[1fr_320px_320px]">
              <TrendChart />
              <SentimentChart />
              <ComplaintThemes />
            </div>

            {/* Bottom Lists split grid */}
            <div className="grid gap-8 lg:grid-cols-[1fr_380px]">
              <RecentComplaintsTable />
              <LiveAlertsPanel />
            </div>
          </div>

          {/* Demo Sidebar */}
          {demoEnabled && (
            <div className="space-y-6">
              <DemoScenarios />
              <CustomerJourneyTimeline />
              <AIDecisionPanel />
              <DemoTimeline />
            </div>
          )}
        </div>
      </div>
      <AICopilot />
    </DashboardShell>
  );
}
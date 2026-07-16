"use client";

import { useState, useCallback, useMemo, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { useAlerts, useAlertKPIs, useAlertSeverityCounts } from "@/features/live-alerts/use-live-alerts";
import { InsuranceFilter } from "@/components/insurance/InsuranceFilter";
import { LiveAlertsHeader, ChannelFilter, SeverityTabs, AlertKPICards, AlertsTable, RealtimeIndicator } from "@/components/live-alerts";
import { Phase2AlertBanner } from "@/components/live-alerts/Phase2AlertBanner";
import type { SeverityTabId } from "@/components/live-alerts";
import type { AlertItem } from "@/features/live-alerts/use-live-alerts";

const PAGE_SIZE = 10;

function LiveAlertsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const severityFromUrl = (searchParams.get("severity") as SeverityTabId) ?? "all";
  const channelFromUrl = searchParams.get("channel") ?? "";
  const pageFromUrl = parseInt(searchParams.get("page") ?? "1", 10);

  const [activeSeverity, setActiveSeverity] = useState<SeverityTabId>(severityFromUrl);
  const [channel, setChannel] = useState(channelFromUrl);
  const [page, setPage] = useState(pageFromUrl);

  useEffect(() => {
    const params = new URLSearchParams();
    if (activeSeverity !== "all") params.set("severity", activeSeverity);
    if (channel) params.set("channel", channel);
    if (page > 1) params.set("page", String(page));
    const qs = params.toString();
    router.replace(`/live-alerts${qs ? `?${qs}` : ""}`, { scroll: false });
  }, [activeSeverity, channel, page, router]);

  const { data, isLoading } = useAlerts({
    page,
    page_size: 50,
    severity: activeSeverity === "all" ? undefined : activeSeverity,
    channel: channel || undefined,
  });

  const { data: kpis } = useAlertKPIs();
  const { data: severityCounts } = useAlertSeverityCounts();

  const handleSeverityChange = useCallback((tab: SeverityTabId) => {
    setActiveSeverity(tab);
    setPage(1);
  }, []);

  const handleChannelChange = useCallback((value: string) => {
    setChannel(value);
    setPage(1);
  }, []);

  const items = (data?.items ?? []) as AlertItem[];

  return (
    <div className="space-y-8 animate-fade-in text-left">
      {/* Header row: Title+subtitle on left, Channel filter + Severity tabs on right */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <LiveAlertsHeader />
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
          <ChannelFilter value={channel} onChange={handleChannelChange} />
          <SeverityTabs
            activeTab={activeSeverity}
            onTabChange={handleSeverityChange}
          />
        </div>
      </div>

      <AlertKPICards
        highRiskAlerts={kpis?.high_risk_alerts ?? 2}
        slaAtRisk={kpis?.sla_at_risk ?? 3}
        regulatoryRisk={kpis?.regulatory_risk ?? 1}
        newAlertsLastHour={kpis?.new_alerts_last_hour ?? 6}
      />

      <AlertsTable
        data={items}
        isLoading={isLoading}
        total={data?.total}
        page={page}
        pageSize={PAGE_SIZE}
        onPageChange={setPage}
        onOpenComplaint={(item: any) => { if (item.complaint_id) router.push(`/complaint-cases/${item.complaint_id}`); }}
        onViewCustomer={() => {}}
        onViewWorkflow={() => {}}
        onAssignOfficer={() => {}}
        onAcknowledge={() => {}}
        onEscalate={() => {}}
        onArchive={() => {}}
      />

      <div className="flex justify-end">
        <RealtimeIndicator />
      </div>
    </div>
  );
}

function LoadingFallback() {
  return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in">
        <div className="page-header"><h1>Live Alerts</h1><p>Real-time AI alerts for high-risk complaints and customer escalations.</p></div>
        <div className="flex items-center gap-4">
          <div className="h-9 w-40 rounded-lg bg-muted animate-pulse" />
          <div className="flex gap-1"><div className="h-9 w-16 rounded-lg bg-muted animate-pulse" /><div className="h-9 w-16 rounded-lg bg-muted animate-pulse" /><div className="h-9 w-16 rounded-lg bg-muted animate-pulse" /></div>
        </div>
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="h-24 rounded-xl bg-muted animate-pulse" />)}
        </div>
        <div className="h-64 rounded-xl bg-muted animate-pulse" />
      </div>
      <AICopilot />
    </DashboardShell>
  );
}

export default function LiveAlertsPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <DashboardShell>
        <LiveAlertsContent />
        <AICopilot />
      </DashboardShell>
    </Suspense>
  );
}
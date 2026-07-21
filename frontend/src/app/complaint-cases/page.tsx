"use client";

import { useState, useCallback, useMemo, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { useComplaintCases, useComplaintCaseKPIs, useComplaintCaseTabCounts, tabToComplaintFilter } from "@/features/complaint-cases/use-complaint-cases";
import { useDebounce } from "@/hooks/use-debounce";
import { ComplaintCaseHeader, ComplaintCaseTabs, ComplaintCaseFilters, ComplaintCaseKPIs, ComplaintCaseTable, ComplaintCaseToolbar } from "@/components/complaint-cases";
import { InsuranceFilter } from "@/components/insurance/InsuranceFilter";
import { InsuranceBadge } from "@/components/insurance/InsuranceBadge";
import type { CaseTabId } from "@/components/complaint-cases";
import { SlidersHorizontal, Download, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

const PAGE_SIZE = 10;

function getTabFilter(tab: CaseTabId): { status?: string; sla_risk?: string } {
  return tabToComplaintFilter(tab);
}

function CasesContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const tabFromUrl = (searchParams.get("tab") as CaseTabId) ?? "all";
  const pageFromUrl = parseInt(searchParams.get("page") ?? "1", 10);
  const searchFromUrl = searchParams.get("search") ?? "";
  const channelFromUrl = searchParams.get("channel") ?? "";
  const themeFromUrl = searchParams.get("theme") ?? "";
  const severityFromUrl = searchParams.get("severity") ?? "";
  const slaFromUrl = searchParams.get("sla") ?? "";
  const assignedFromUrl = searchParams.get("assigned") ?? "";

  const [activeTab, setActiveTab] = useState<CaseTabId>(tabFromUrl);
  const [search, setSearch] = useState(searchFromUrl);
  const [page, setPage] = useState(pageFromUrl);
  const [channel, setChannel] = useState(channelFromUrl);
  const [theme, setTheme] = useState(themeFromUrl);
  const [severity, setSeverity] = useState(severityFromUrl);
  const [slaStatus, setSlaStatus] = useState(slaFromUrl);
  const [assignedTo, setAssignedTo] = useState(assignedFromUrl);
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const debouncedSearch = useDebounce(search, 300);

  useEffect(() => { setPage(1); setSelectedIds(new Set()); }, [activeTab]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (activeTab !== "all") params.set("tab", activeTab);
    if (page > 1) params.set("page", String(page));
    if (search) params.set("search", search);
    if (channel) params.set("channel", channel);
    if (theme) params.set("theme", theme);
    if (severity) params.set("severity", severity);
    if (slaStatus) params.set("sla", slaStatus);
    if (assignedTo) params.set("assigned", assignedTo);
    const qs = params.toString();
    router.replace(`/complaint-cases${qs ? `?${qs}` : ""}`, { scroll: false });
  }, [activeTab, page, search, channel, theme, severity, slaStatus, assignedTo, router]);

  const tabFilter = getTabFilter(activeTab);
  const { data, isLoading } = useComplaintCases({
    page, page_size: PAGE_SIZE,
    channel: channel || undefined, theme: theme || undefined, severity: severity || undefined,
    sla_risk: slaStatus || undefined,
    ...tabFilter,
  });
  const { data: kpis } = useComplaintCaseKPIs();

  const handleTabChange = useCallback((tab: CaseTabId) => { setActiveTab(tab); }, []);
  const handleClearFilters = useCallback(() => { setChannel(""); setTheme(""); setSeverity(""); setSlaStatus(""); setAssignedTo(""); setDateFrom(""); setDateTo(""); setSearch(""); setPage(1); }, []);
  const handleApplyFilters = useCallback(() => { setPage(1); }, []);

  const handleExport = useCallback(() => {
    const items = data?.items ?? [];
    if (items.length === 0) return;
    const headers = ["Case ID", "Category", "Channel", "Theme", "Severity", "SLA Risk", "Queue", "Status", "Created"];
    const csv = [headers.join(","), ...items.map((item) => [
      item.case_number ?? item.id,
      item.category, item.channel ?? "", item.theme ?? "", item.severity,
      item.sla_risk ?? "", item.assigned_queue ?? "", item.status,
      item.created_at,
    ].map((v) => `"${String(v).replace(/"/g, '""')}"`).join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = `complaint-cases-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click(); URL.revokeObjectURL(url);
  }, [data]);

  return (
    <div className="space-y-8 animate-fade-in text-left">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <ComplaintCaseHeader />
        
        {/* Right side page actions buttons */}
        <div className="flex items-center gap-3">
          <button className="flex h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-all shadow-sm">
            <SlidersHorizontal className="h-4 w-4 text-[#94A3B8]" />
            <span>Filters</span>
          </button>
          <button onClick={handleExport} className="flex h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-all shadow-sm">
            <Download className="h-4 w-4 text-[#94A3B8]" />
            <span>Export</span>
          </button>
          <button onClick={() => router.push("/complaint-cases?tab=escalated")}
            className="flex h-10 items-center gap-2 rounded-xl bg-[#EF4444] px-4.5 text-xs font-bold text-white shadow-md hover:bg-red-700 transition-all active:scale-[0.98]">
            <AlertTriangle className="h-4 w-4" />
            <span>View Escalations</span>
          </button>
        </div>
      </div>

      <ComplaintCaseTabs activeTab={activeTab} onTabChange={handleTabChange} />

      <ComplaintCaseFilters
        search={search} onSearchChange={setSearch}
        channel={channel} onChannelChange={setChannel}
        theme={theme} onThemeChange={setTheme}
        severity={severity} onSeverityChange={setSeverity}
        slaStatus={slaStatus} onSlaStatusChange={setSlaStatus}
        assignedTo={assignedTo} onAssignedToChange={setAssignedTo}
        dateFrom={dateFrom} dateTo={dateTo} onDateFromChange={setDateFrom} onDateToChange={setDateTo}
        onClear={handleClearFilters} onApply={handleApplyFilters}
      />

      <ComplaintCaseKPIs
        totalCases={kpis?.total_cases ?? 0}
        inProgress={kpis?.in_progress ?? 0}
        overdue={kpis?.overdue ?? 0}
        avgResolutionTime={kpis?.avg_resolution_time ?? null}
        resolvedThisMonth={kpis?.resolved_this_month ?? 0}
      />

      <ComplaintCaseTable
        data={data?.items}
        total={data?.total ?? 0}
        pageSize={PAGE_SIZE}
        isLoading={isLoading}
        page={page}
        onPageChange={setPage}
        selectedIds={selectedIds}
        onSelectionChange={setSelectedIds}
      />
    </div>
  );
}

function LoadingFallback() {
  return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in">
        <div className="page-header"><h1>Complaint Cases</h1><p>View, track and manage all complaint cases.</p></div>
        <div className="flex gap-1 border-b border-border">{Array.from({ length: 7 }).map((_, i) => <div key={i} className="h-9 w-28 rounded-t-lg bg-muted animate-pulse" />)}</div>
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-5">{Array.from({ length: 5 }).map((_, i) => <div key={i} className="h-24 rounded-xl bg-muted animate-pulse" />)}</div>
        <div className="h-64 rounded-xl bg-muted animate-pulse" />
      </div>
      <AICopilot />
    </DashboardShell>
  );
}

export default function ComplaintCasesPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <DashboardShell>
        <CasesContent />
        <AICopilot />
      </DashboardShell>
    </Suspense>
  );
}
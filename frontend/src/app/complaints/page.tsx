"use client";

import { useState, useCallback, useMemo, useEffect, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { useComplaintList, useComplaintKPIs, useComplaintTabCounts } from "@/features/complaints/hooks/use-complaints";
import { useDebounce } from "@/hooks/use-debounce";
import { ComplaintHeader, ComplaintTabs, ComplaintKPICards, ComplaintTable, BulkToolbar, ExportButton } from "@/components/complaints";
import type { ComplaintTabId } from "@/components/complaints";
import type { Complaint } from "@/types/domain";
import { SlidersHorizontal, Search, Calendar, X, Download, Plus } from "lucide-react";
import { cn } from "@/lib/cn";

const PAGE_SIZE = 10;

function getTabFilter(tab: ComplaintTabId): { status?: string; priority?: string; assigned_to_me?: boolean } {
  switch (tab) {
    case "all": return {};
    case "open": return { status: "open,submitted,under_review,investigating" };
    case "assigned_to_me": return { assigned_to_me: true };
    case "high_risk": return { priority: "high,critical" };
    case "critical": return { priority: "critical" };
    case "overdue": return {};
    case "resolved": return { status: "resolved" };
    case "closed": return { status: "closed,archived" };
    case "repeat": return {};
    default: return {};
  }
}

const selectClass =
  "h-10 rounded-xl border border-[#E2E8F0] bg-white px-3 text-xs font-semibold text-[#334155] outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] transition-all cursor-pointer hover:border-slate-300";

function ComplaintsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const tabFromUrl = (searchParams.get("tab") as ComplaintTabId) ?? "all";
  const pageFromUrl = parseInt(searchParams.get("page") ?? "1", 10);
  const searchFromUrl = searchParams.get("search") ?? "";
  const channelFromUrl = searchParams.get("channel") ?? "";
  const themeFromUrl = searchParams.get("theme") ?? "";
  const severityFromUrl = searchParams.get("severity") ?? "";
  const slaFromUrl = searchParams.get("sla") ?? "";
  const dateFromUrl = searchParams.get("date_from") ?? "";
  const dateToUrl = searchParams.get("date_to") ?? "";

  const [activeTab, setActiveTab] = useState<ComplaintTabId>(tabFromUrl);
  const [search, setSearch] = useState(searchFromUrl);
  const [page, setPage] = useState(pageFromUrl);
  const [channel, setChannel] = useState(channelFromUrl);
  const [theme, setTheme] = useState(themeFromUrl);
  const [severity, setSeverity] = useState(severityFromUrl);
  const [slaStatus, setSlaStatus] = useState(slaFromUrl);
  const [dateFrom, setDateFrom] = useState(dateFromUrl);
  const [dateTo, setDateTo] = useState(dateToUrl);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const debouncedSearch = useDebounce(search, 300);

  useEffect(() => {
    setPage(1);
    setSelectedIds(new Set());
  }, [activeTab]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (activeTab !== "all") params.set("tab", activeTab);
    if (page > 1) params.set("page", String(page));
    if (search) params.set("search", search);
    if (channel) params.set("channel", channel);
    if (theme) params.set("theme", theme);
    if (severity) params.set("severity", severity);
    if (slaStatus) params.set("sla", slaStatus);
    if (dateFrom) params.set("date_from", dateFrom);
    if (dateTo) params.set("date_to", dateTo);
    const qs = params.toString();
    router.replace(`/complaints${qs ? `?${qs}` : ""}`, { scroll: false });
  }, [activeTab, page, search, channel, theme, severity, slaStatus, dateFrom, dateTo, router]);

  const tabFilter = getTabFilter(activeTab);

  const { data, isLoading } = useComplaintList({
    page,
    page_size: PAGE_SIZE,
    search: debouncedSearch || undefined,
    channel: channel || undefined,
    theme: theme || undefined,
    severity: severity || undefined,
    sla_status: slaStatus || undefined,
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
    ...tabFilter,
  });

  const { data: kpis } = useComplaintKPIs();
  const { data: tabCounts } = useComplaintTabCounts();

  const handleTabChange = useCallback((tab: ComplaintTabId) => {
    setActiveTab(tab);
  }, []);

  const handleClearFilters = useCallback(() => {
    setChannel("");
    setTheme("");
    setSeverity("");
    setSlaStatus("");
    setDateFrom("");
    setDateTo("");
    setSearch("");
    setPage(1);
  }, []);

  const handleExport = useCallback(() => {
    const items = data?.items ?? [];
    if (items.length === 0) return;

    const headers = ["Complaint ID", "Customer", "Channel", "Theme", "Severity", "Status", "Priority", "Assigned To", "Received Time"];
    const rows = items.map((item) => [
      item.complaint_number ?? item.id,
      item.customer_name ?? "Unknown",
      item.channel ?? "",
      item.theme ?? item.category ?? "",
      item.severity,
      item.status,
      item.priority,
      item.assigned_agent_name ?? item.assigned_queue ?? "",
      item.received_time ?? item.created_at ?? "",
    ]);

    const csv = [headers.join(","), ...rows.map((r) => r.map((v) => `"${v.replace(/"/g, '""')}`).join(","))].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `complaints-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, [data]);

  const handleCreateComplaint = useCallback(() => {
    router.push("/complaints/new");
  }, [router]);

  const items = (data?.items ?? []) as Complaint[];
  const tabCountsData = useMemo(() => tabCounts ?? {}, [tabCounts]);
  const hasFilters = channel || theme || severity || slaStatus || dateFrom || dateTo || search;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header Row */}
      <div className="flex items-start justify-between">
        <ComplaintHeader />
        <div className="flex items-center gap-2.5">
          <button
            onClick={handleExport}
            className="flex h-10 items-center gap-2 rounded-xl border border-[#E2E8F0] bg-white px-4 text-xs font-bold text-[#334155] shadow-sm hover:bg-[#F8FAFC] transition-all"
          >
            <Download className="h-3.5 w-3.5 text-[#64748B]" />
            Export
          </button>
          <button
            onClick={handleCreateComplaint}
            className="flex h-10 items-center gap-2 rounded-xl bg-[#0052FF] px-4 text-xs font-bold text-white shadow-md shadow-blue-500/10 hover:bg-blue-600 transition-all active:scale-[0.98]"
          >
            <Plus className="h-4 w-4" />
            New Complaint
          </button>
        </div>
      </div>

      {/* Tabs */}
      <ComplaintTabs
        activeTab={activeTab}
        onTabChange={handleTabChange}
        counts={tabCountsData as Record<string, number>}
      />

      {/* Always-visible filter bar matching mockup */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="relative min-w-[180px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#94A3B8]" />
          <input
            type="text"
            placeholder="Search complaints..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-10 w-full rounded-xl border border-[#E2E8F0] bg-white pl-9 pr-3 text-xs font-semibold text-[#334155] placeholder:text-[#94A3B8] outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB] transition-all"
          />
        </div>

        <select value={channel} onChange={(e) => setChannel(e.target.value)} className={selectClass}>
          <option value="">All Channels</option>
          <option value="voice">Voice</option>
          <option value="whatsapp">WhatsApp</option>
          <option value="email">Email</option>
          <option value="web_chat">Web Chat</option>
          <option value="smart_call">SMART CALL</option>
          <option value="crm">CRM</option>
          <option value="manual">Manual</option>
        </select>

        <select value={theme} onChange={(e) => setTheme(e.target.value)} className={selectClass}>
          <option value="">All Themes</option>
          <option value="claim_delays">Claim Delays</option>
          <option value="service_quality">Service Quality</option>
          <option value="policy_coverage">Policy & Coverage</option>
          <option value="payments_refunds">Payments & Refunds</option>
          <option value="provider_garage">Provider / Garage</option>
          <option value="renewal">Renewal</option>
        </select>

        <select value={severity} onChange={(e) => setSeverity(e.target.value)} className={selectClass}>
          <option value="">All Severity</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>

        <select value={slaStatus} onChange={(e) => setSlaStatus(e.target.value)} className={selectClass}>
          <option value="">All SLA Status</option>
          <option value="on_track">On Track</option>
          <option value="at_risk">At Risk</option>
          <option value="overdue">Overdue</option>
        </select>

        {/* Date range */}
        <div className="flex items-center gap-2 rounded-xl border border-[#E2E8F0] bg-white px-3 h-10">
          <Calendar className="h-4 w-4 text-[#94A3B8] shrink-0" />
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            className="text-xs font-semibold text-[#334155] outline-none bg-transparent w-[100px]"
          />
          <span className="text-[#94A3B8] text-xs">—</span>
          <input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            className="text-xs font-semibold text-[#334155] outline-none bg-transparent w-[100px]"
          />
        </div>

        {/* Clear & Apply */}
        {hasFilters && (
          <button
            onClick={handleClearFilters}
            className="flex h-10 items-center gap-1.5 rounded-xl border border-[#E2E8F0] bg-white px-4 text-xs font-bold text-[#64748B] shadow-sm hover:bg-[#F8FAFC] transition-all"
          >
            <X className="h-3.5 w-3.5" />
            Clear
          </button>
        )}
        <button
          onClick={() => setPage(1)}
          className="flex h-10 items-center gap-1.5 rounded-xl bg-[#0052FF] px-4 text-xs font-bold text-white shadow-md shadow-blue-500/10 hover:bg-blue-600 transition-all"
        >
          Apply
        </button>
      </div>

      {/* KPI Cards */}
      {kpis && (
        <ComplaintKPICards
          total={kpis.total_complaints}
          highRisk={kpis.high_risk}
          slaAtRisk={kpis.sla_at_risk}
          overdue={kpis.overdue}
          resolvedThisWeek={kpis.resolved_this_week}
        />
      )}

      <BulkToolbar
        selectedCount={selectedIds.size}
        onClear={() => setSelectedIds(new Set())}
      />

      <ComplaintTable
        data={items}
        isLoading={isLoading}
        total={data?.total}
        page={page}
        pageSize={PAGE_SIZE}
        onPageChange={setPage}
        selectedIds={selectedIds}
        onSelectionChange={setSelectedIds}
        onOpen={(item) => router.push(`/complaints/${item.id}`)}
        onAssign={() => {}}
        onTransfer={() => {}}
        onEscalate={() => {}}
        onCreateWorkflow={() => {}}
        onViewCustomer={() => {}}
        onArchive={() => {}}
        onDelete={() => {}}
      />
    </div>
  );
}

function LoadingFallback() {
  return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in">
        <div className="page-header"><h1>Complaints</h1><p>View, filter and manage customer complaints across all channels.</p></div>
        <div className="flex gap-1 border-b border-border">
          {Array.from({ length: 7 }).map((_, i) => <div key={i} className="h-9 w-28 rounded-t-lg bg-muted animate-pulse" />)}
        </div>
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => <div key={i} className="h-24 rounded-xl bg-muted animate-pulse" />)}
        </div>
        <div className="h-24 rounded-xl bg-muted animate-pulse" />
        <div className="h-64 rounded-xl bg-muted animate-pulse" />
      </div>
      <AICopilot />
    </DashboardShell>
  );
}

export default function ComplaintsPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <DashboardShell>
        <ComplaintsContent />
        <AICopilot />
      </DashboardShell>
    </Suspense>
  );
}
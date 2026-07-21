"use client";

import { useState } from "react";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { cn } from "@/lib/cn";
import { EnterpriseDistributionCharts } from "@/components/enterprise-analytics/enterprise-distribution-charts";
import { EnterpriseEmployeeTable } from "@/components/enterprise-analytics/enterprise-employee-table";
import { EnterpriseFilterBar } from "@/components/enterprise-analytics/enterprise-filter-bar";
import { EnterpriseKpiCards } from "@/components/enterprise-analytics/enterprise-kpi-cards";
import { EnterpriseSupervisorSection } from "@/components/enterprise-analytics/enterprise-supervisor-section";
import { EnterpriseTrendCharts } from "@/components/enterprise-analytics/enterprise-trend-charts";
import type { ExportReport, ReportingQueryFilters } from "@/features/reporting/types";

type Tab = "overview" | "employees" | "supervisor";

const TABS: { id: Tab; label: string; exportReport: ExportReport }[] = [
  { id: "overview", label: "Overview", exportReport: "summary" },
  { id: "employees", label: "Employee Analytics", exportReport: "employees" },
  { id: "supervisor", label: "Supervisor Dashboard", exportReport: "summary" },
];

function EnterpriseAnalyticsContent() {
  const [tab, setTab] = useState<Tab>("overview");
  const [filters, setFilters] = useState<ReportingQueryFilters>({});
  const [granularity, setGranularity] = useState<"day" | "week" | "month">("day");

  const activeTab = TABS.find((t) => t.id === tab)!;

  return (
    <div className="space-y-6">
      <div className="space-y-0.5">
        <h1 className="text-2xl font-extrabold tracking-tight text-foreground">
          Enterprise Analytics
        </h1>
        <p className="text-sm font-medium text-muted-foreground">
          Live conversation, AI-handling, and employee performance metrics — computed from the real
          database, updated as conversations happen.
        </p>
      </div>

      <div className="flex gap-1 border-b border-border">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={cn(
              "px-3 py-2 text-sm font-medium",
              tab === t.id
                ? "border-b-2 border-primary text-foreground"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab !== "supervisor" ? (
        <EnterpriseFilterBar
          filters={filters}
          onChange={setFilters}
          exportReport={activeTab.exportReport}
        />
      ) : null}

      {tab === "overview" ? (
        <div className="space-y-6">
          <EnterpriseKpiCards filters={filters} />

          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-muted-foreground">Trend granularity:</span>
            {(["day", "week", "month"] as const).map((g) => (
              <button
                key={g}
                type="button"
                onClick={() => setGranularity(g)}
                className={cn(
                  "rounded-md border px-2 py-1 text-xs",
                  granularity === g
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border text-muted-foreground hover:bg-accent",
                )}
              >
                {g}
              </button>
            ))}
          </div>
          <EnterpriseTrendCharts filters={filters} granularity={granularity} />
          <EnterpriseDistributionCharts filters={filters} />
        </div>
      ) : null}

      {tab === "employees" ? <EnterpriseEmployeeTable filters={filters} /> : null}

      {tab === "supervisor" ? <EnterpriseSupervisorSection /> : null}
    </div>
  );
}

export default function EnterpriseAnalyticsPage() {
  return (
    <DashboardShell>
      <EnterpriseAnalyticsContent />
      <AICopilot />
    </DashboardShell>
  );
}

"use client";

import { Download } from "lucide-react";

import { Button } from "@/components/ui/button";
import { reportingService } from "@/services/reporting.service";
import type { ExportReport, ReportingQueryFilters } from "@/features/reporting/types";

const CHANNELS = ["web_chat", "voice", "whatsapp", "email", "complaint"];
const PRIORITIES = ["low", "medium", "high", "critical"];

/** Date, employee, channel, priority — the filter dimensions that map to
 * real columns (see design decision 4: department/policy-type have no
 * backing field anywhere in this schema, so they're simply not offered
 * here rather than faked). Export buttons link straight to the backend
 * file-generation endpoint — no CSV/Excel library on the frontend at all. */
export function EnterpriseFilterBar({
  filters,
  onChange,
  exportReport,
}: {
  filters: ReportingQueryFilters;
  onChange: (filters: ReportingQueryFilters) => void;
  exportReport: ExportReport;
}) {
  function update(patch: Partial<ReportingQueryFilters>) {
    onChange({ ...filters, ...patch });
  }

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-xl border border-border bg-background p-3">
      <input
        type="date"
        value={filters.date_from?.slice(0, 10) ?? ""}
        onChange={(e) => update({ date_from: e.target.value ? `${e.target.value}T00:00:00Z` : undefined })}
        className="h-8 rounded-md border border-border bg-background px-2 text-xs"
        aria-label="From date"
      />
      <input
        type="date"
        value={filters.date_to?.slice(0, 10) ?? ""}
        onChange={(e) => update({ date_to: e.target.value ? `${e.target.value}T23:59:59Z` : undefined })}
        className="h-8 rounded-md border border-border bg-background px-2 text-xs"
        aria-label="To date"
      />
      <select
        value={filters.channel ?? ""}
        onChange={(e) => update({ channel: e.target.value || undefined })}
        className="h-8 rounded-md border border-border bg-background px-2 text-xs"
      >
        <option value="">All Channels</option>
        {CHANNELS.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>
      <select
        value={filters.priority ?? ""}
        onChange={(e) => update({ priority: e.target.value || undefined })}
        className="h-8 rounded-md border border-border bg-background px-2 text-xs"
      >
        <option value="">All Priorities</option>
        {PRIORITIES.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
      <input
        type="text"
        placeholder="Employee UUID"
        value={filters.assigned_employee_id ?? ""}
        onChange={(e) => update({ assigned_employee_id: e.target.value || undefined })}
        className="h-8 w-40 rounded-md border border-border bg-background px-2 text-xs"
      />

      {(filters.date_from || filters.date_to || filters.channel || filters.priority || filters.assigned_employee_id) ? (
        <Button size="sm" variant="ghost" className="h-8 text-xs" onClick={() => onChange({})}>
          Clear
        </Button>
      ) : null}

      <div className="ml-auto flex items-center gap-1.5">
        <a href={reportingService.exportUrl(exportReport, "csv", filters)} download>
          <Button size="sm" variant="outline" className="h-8 gap-1 text-xs">
            <Download className="h-3 w-3" /> CSV
          </Button>
        </a>
        <a href={reportingService.exportUrl(exportReport, "xlsx", filters)} download>
          <Button size="sm" variant="outline" className="h-8 gap-1 text-xs">
            <Download className="h-3 w-3" /> Excel
          </Button>
        </a>
        <Button
          size="sm"
          variant="outline"
          className="h-8 gap-1 text-xs opacity-60"
          onClick={() =>
            window.open(reportingService.exportUrl(exportReport, "pdf", filters), "_blank")
          }
          title="PDF export is not available yet"
        >
          <Download className="h-3 w-3" /> PDF
        </Button>
      </div>
    </div>
  );
}

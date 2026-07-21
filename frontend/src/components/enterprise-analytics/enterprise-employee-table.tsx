"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { useEmployeeAnalytics } from "@/features/reporting/hooks/use-reporting";
import type { EmployeeAnalyticsItem, ReportingQueryFilters } from "@/features/reporting/types";

function formatDuration(seconds: number | null): string {
  if (seconds == null) return "—";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  return `${Math.round(minutes / 60)}h`;
}

type EmployeeRow = EmployeeAnalyticsItem & { id: string };

const COLUMNS: Column<EmployeeRow>[] = [
  {
    key: "employee",
    header: "Employee",
    render: (e) => (
      <span className="font-medium">{e.employee_name ?? `${e.employee_id.slice(0, 8)}…`}</span>
    ),
  },
  { key: "assigned_conversations", header: "Assigned", render: (e) => String(e.assigned_conversations) },
  { key: "resolved", header: "Resolved", render: (e) => String(e.resolved) },
  { key: "escalated", header: "Escalated", render: (e) => String(e.escalated) },
  {
    key: "avg_resolution_seconds",
    header: "Avg. Resolution Time",
    render: (e) => formatDuration(e.avg_resolution_seconds),
  },
  { key: "ai_assistance_usage", header: "AI Assistance Usage", render: (e) => String(e.ai_assistance_usage) },
  { key: "transfer_count", header: "Transfers", render: (e) => String(e.transfer_count) },
];

/** Also serves as the "Agent Workload" visualization — the spec's Part B
 * chart list and Employee Analytics section describe the same underlying
 * data, so this one table backs both instead of duplicating the query. */
export function EnterpriseEmployeeTable({ filters }: { filters: ReportingQueryFilters }) {
  const { data = [], isLoading } = useEmployeeAnalytics(filters);
  const rows: EmployeeRow[] = data.map((e) => ({ ...e, id: e.employee_id }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Employee Analytics / Agent Workload</CardTitle>
      </CardHeader>
      <CardContent>
        <DataTable
          columns={COLUMNS}
          data={rows}
          isLoading={isLoading}
          emptyMessage="No employee-assigned conversations in this window."
        />
      </CardContent>
    </Card>
  );
}

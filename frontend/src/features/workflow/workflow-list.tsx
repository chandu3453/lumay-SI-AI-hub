"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { useWorkflows } from "@/features/dashboard/use-dashboard";
import { DataTable, type Column } from "@/components/ui/data-table";
import { formatRelative } from "@/lib/formatters";

const slaVariant: Record<string, "success" | "warning" | "destructive" | "neutral"> = {
  within_sla: "success", at_risk: "warning", breached: "destructive",
};

const statusVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  pending: "neutral", active: "default", completed: "success", cancelled: "neutral", archived: "neutral",
};

export function WorkflowList() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useWorkflows({ page, page_size: 10 });
  const router = useRouter();

  const columns: Column<any>[] = [
    {
      key: "workflow",
      header: "Workflow",
      render: (w: any) => (
        <div>
          <p className="font-medium">{w.workflow_number ?? "—"}</p>
          <p className="text-xs text-muted-foreground mt-0.5">
            <span className="capitalize">{w.workflow_stage}</span>
            <span className="mx-1">·</span>
            {w.created_at && formatRelative(w.created_at)}
          </p>
        </div>
      ),
    },
    { key: "team", header: "Team", render: (w: any) => <span className="text-muted-foreground">{w.assigned_team ?? "Unassigned"}</span> },
    { key: "sla", header: "SLA", render: (w: any) => <Badge variant={slaVariant[w.sla_status] ?? "neutral"} className="capitalize text-xs">{w.sla_status?.replace(/_/g, " ")}</Badge> },
    { key: "status", header: "Status", render: (w: any) => <Badge variant={statusVariant[w.workflow_status] ?? "neutral"} className="capitalize text-xs">{w.workflow_status}</Badge> },
  ];

  return (
    <DataTable columns={columns} data={data?.items?.map((w: any) => ({ ...w, id: w.id })) ?? []} isLoading={isLoading} emptyMessage="No workflows found" page={page} pageSize={10} total={data?.total} onPageChange={setPage} onRowClick={(item) => router.push(`/workflow/${item.id}`)} />
  );
}
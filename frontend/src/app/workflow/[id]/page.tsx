"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import {
  ArrowLeft, GitBranch, Users, Clock, AlertTriangle, CheckCircle2, Archive,
} from "lucide-react";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/cn";
import { formatDate, formatEnum } from "@/lib/formatters";
import { workflowService } from "@/services/workflow.service";
import { complaintsService } from "@/services/complaints.service";
import type { Complaint, Workflow } from "@/types/domain";

const slaVariant: Record<string, "success" | "warning" | "destructive" | "neutral"> = {
  within_sla: "success", at_risk: "warning", breached: "destructive",
};
const statusVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  pending: "neutral", active: "default", completed: "success", cancelled: "neutral", archived: "neutral", suspended: "warning",
};

function useWorkflowDetail(id: string) {
  return useQuery({
    queryKey: ["workflows", id],
    queryFn: async () => {
      const res = await workflowService.getById(id);
      return (res.data as { data: Workflow }).data;
    },
    enabled: !!id,
  });
}

function useLinkedComplaint(complaintId: string | undefined) {
  return useQuery({
    queryKey: ["complaints", complaintId],
    queryFn: async () => {
      if (!complaintId) return null;
      const res = await complaintsService.getById(complaintId);
      return (res.data as { data: Complaint }).data;
    },
    enabled: !!complaintId,
  });
}

export default function WorkflowDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const router = useRouter();
  const queryClient = useQueryClient();
  const { data: workflow, isLoading } = useWorkflowDetail(id);
  const { data: complaint } = useLinkedComplaint(workflow?.complaint_id ? String(workflow.complaint_id) : undefined);
  const [actionPending, setActionPending] = useState<string | null>(null);

  const isTerminal = workflow?.workflow_status === "completed" || workflow?.workflow_status === "archived" || workflow?.workflow_status === "cancelled";

  async function runAction(key: string, fn: () => Promise<unknown>) {
    setActionPending(key);
    try {
      await fn();
      await queryClient.invalidateQueries({ queryKey: ["workflows", id] });
    } finally {
      setActionPending(null);
    }
  }

  if (isLoading) {
    return (
      <DashboardShell>
        <div className="space-y-6 animate-fade-in">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
        <AICopilot />
      </DashboardShell>
    );
  }

  if (!workflow) {
    return (
      <DashboardShell>
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Workflow not found.</p>
        </div>
        <AICopilot />
      </DashboardShell>
    );
  }

  return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in text-left">
        <Link href="/workflow" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors">
          <ArrowLeft className="h-4 w-4" /> Back to Workflows
        </Link>

        <div className="bg-white dark:bg-card rounded-xl border border-border shadow-card p-5">
          <div className="flex items-start justify-between flex-wrap gap-3">
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <GitBranch className="h-5 w-5 text-primary" />
                <h1 className="text-lg font-bold text-foreground">{workflow.workflow_number ?? `Workflow ${String(workflow.id).slice(0, 8)}…`}</h1>
                <Badge variant={statusVariant[workflow.workflow_status] ?? "neutral"} className="capitalize">{formatEnum(workflow.workflow_status)}</Badge>
                <Badge variant={slaVariant[workflow.sla_status] ?? "neutral"} className="capitalize">{formatEnum(workflow.sla_status)}</Badge>
              </div>
              <p className="text-sm text-muted-foreground capitalize">Stage: {formatEnum(workflow.workflow_stage)}</p>
            </div>
            {complaint && (
              <button
                onClick={() => router.push(`/complaints/${complaint.id}`)}
                className="text-xs font-bold text-primary hover:underline"
              >
                View linked complaint: {complaint.complaint_number ?? complaint.id} →
              </button>
            )}
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Workflow Details</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-xs text-muted-foreground">Assigned Team</p>
                <p className="font-medium">{workflow.assigned_team ?? "Unassigned"}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Assigned Agent</p>
                <p className="font-medium">{workflow.assigned_agent_id ?? "Unassigned"}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Priority</p>
                <p className="font-medium capitalize">{workflow.priority ?? "—"}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Current Queue</p>
                <p className="font-medium">{(workflow as unknown as { current_queue?: string }).current_queue ?? "—"}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Started</p>
                <p className="font-medium">{workflow.started_at ? formatDate(workflow.started_at) : "—"}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Completed</p>
                <p className="font-medium">{workflow.completed_at ? formatDate(workflow.completed_at) : "—"}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {[
                { key: "escalate", icon: AlertTriangle, label: "Escalate", variant: "destructive", action: () => runAction("escalate", () => workflowService.escalate(id)) },
                { key: "complete", icon: CheckCircle2, label: "Mark Complete", variant: "success", action: () => runAction("complete", () => workflowService.complete(id)) },
                { key: "archive", icon: Archive, label: "Archive", variant: "outline", action: () => runAction("archive", () => workflowService.archive(id)) },
              ].map((action) => {
                const Icon = action.icon;
                const variantClasses: Record<string, string> = {
                  destructive: "bg-[#DC2626] text-white hover:bg-[#DC2626]/90",
                  outline: "border border-border bg-white hover:bg-accent text-foreground",
                  success: "bg-[#16A34A] text-white hover:bg-[#16A34A]/90",
                };
                return (
                  <button
                    key={action.key}
                    onClick={action.action}
                    disabled={isTerminal || actionPending !== null}
                    className={cn(
                      "w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed",
                      variantClasses[action.variant],
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {actionPending === action.key ? "Working…" : action.label}
                  </button>
                );
              })}
              <p className="text-[11px] text-muted-foreground pt-1">
                Assign / transfer / approve / reject require an agent picker not built this phase — use the Complaint Cases detail page for full lifecycle actions.
              </p>
            </CardContent>
          </Card>
        </div>

        {complaint && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2"><Users className="h-4 w-4" /> Linked Complaint</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-1">
              <p className="font-medium">{complaint.title}</p>
              <p className="text-muted-foreground flex items-center gap-2 text-xs">
                <Clock className="h-3.5 w-3.5" /> {complaint.created_at ? formatDate(complaint.created_at) : "—"}
              </p>
            </CardContent>
          </Card>
        )}
      </div>
      <AICopilot />
    </DashboardShell>
  );
}

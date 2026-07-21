"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  AlertCircle,
  ArrowLeft,
  Clock,
  MessageSquare,
  Sparkles,
  TrendingDown,
} from "lucide-react";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable, type Column } from "@/components/ui/data-table";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDate, formatEnum, formatRelative } from "@/lib/formatters";
import { useCustomer360, useCustomerActivity } from "@/features/reporting/hooks/use-reporting";
import {
  ChannelBadge,
  PriorityBadge,
  StatusBadge,
} from "@/components/interaction-center/shared/conversation-badges";
import { TimelineItemRow } from "@/components/interaction-center/timeline/timeline-item";
import type { ConversationSummary } from "@/features/conversations/types";

function formatDuration(seconds: number | null): string {
  if (seconds == null) return "—";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  return `${Math.round(minutes / 60)}h`;
}

const NOT_AVAILABLE_SECTIONS: { key: "policies" | "claims" | "payments" | "renewals" | "documents"; title: string }[] = [
  { key: "policies", title: "Policies" },
  { key: "claims", title: "Claims" },
  { key: "payments", title: "Payments" },
  { key: "renewals", title: "Renewals" },
  { key: "documents", title: "Documents" },
];

function CustomerDetailContent({ customerId }: { customerId: string }) {
  const { data, isLoading } = useCustomer360(customerId);
  const [timelinePage, setTimelinePage] = useState(1);
  const { data: activity, isLoading: activityLoading } = useCustomerActivity(customerId, timelinePage, 30);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <AlertCircle className="mb-4 h-12 w-12 text-destructive" />
        <p className="text-lg font-bold">Customer not found</p>
        <Link href="/customers" className="mt-6 text-sm font-bold text-primary hover:underline">
          &larr; Back to Customers
        </Link>
      </div>
    );
  }

  const conversationColumns: Column<ConversationSummary>[] = [
    {
      key: "channel",
      header: "Channel",
      render: (c) => <ChannelBadge channel={c.current_channel} />,
    },
    { key: "status", header: "Status", render: (c) => <StatusBadge status={c.current_status} /> },
    { key: "priority", header: "Priority", render: (c) => <PriorityBadge priority={c.priority} /> },
    {
      key: "updated_at",
      header: "Last Activity",
      sortable: true,
      render: (c) => <span className="text-xs text-muted-foreground">{formatRelative(c.updated_at)}</span>,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link
          href="/customers"
          className="flex h-8 w-8 items-center justify-center rounded-md border border-border hover:bg-accent"
        >
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight">{data.customer.full_name}</h1>
          <p className="text-sm text-muted-foreground">
            {data.customer.email ?? "No email on file"} · {formatEnum(data.customer.segment)} ·{" "}
            {formatEnum(data.customer.status)}
          </p>
        </div>
      </div>

      {/* Customer Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Customer Overview</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-3 md:grid-cols-4">
          <OverviewStat label="Open Complaints" value={String(data.overview.open_complaints)} />
          <OverviewStat label="Conversations" value={String(data.overview.conversation_count)} />
          <OverviewStat
            label="Avg. Resolution Time"
            value={formatDuration(data.overview.avg_resolution_seconds)}
          />
          <OverviewStat label="Escalations" value={String(data.overview.escalation_count)} />
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          {/* Current Conversation + Agent Assist Summary */}
          {data.current_conversation ? (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-sm">Current Conversation</CardTitle>
                <Link
                  href={`/interactions?conversation=${data.current_conversation.id}`}
                  className="text-xs font-medium text-primary hover:underline"
                >
                  Open in Interaction Center
                </Link>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex flex-wrap items-center gap-1.5">
                  <ChannelBadge channel={data.current_conversation.current_channel} />
                  <StatusBadge status={data.current_conversation.current_status} />
                  <PriorityBadge priority={data.current_conversation.priority} />
                </div>
                <p className="text-xs text-muted-foreground">
                  {data.assigned_employee
                    ? `Assigned to ${data.assigned_employee.full_name ?? data.assigned_employee.id.slice(0, 8)}`
                    : "Unassigned"}
                </p>
              </CardContent>
            </Card>
          ) : null}

          {data.agent_assist ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-1.5 text-sm">
                  <Sparkles className="h-3.5 w-3.5" /> Agent Assist Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-sm">{data.agent_assist.summary || "No summary available yet."}</p>
                <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                  {data.agent_assist.intent ? (
                    <Badge variant="default">{data.agent_assist.intent}</Badge>
                  ) : null}
                  {data.agent_assist.sentiment ? (
                    <Badge variant="outline">{formatEnum(data.agent_assist.sentiment)}</Badge>
                  ) : null}
                  {data.agent_assist.generated_at ? (
                    <span>Updated {formatRelative(data.agent_assist.generated_at)}</span>
                  ) : null}
                </div>
              </CardContent>
            </Card>
          ) : null}

          {/* Conversation History */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-1.5 text-sm">
                <MessageSquare className="h-3.5 w-3.5" /> Conversation History (
                {data.conversation_statistics.total_conversations})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <DataTable columns={conversationColumns} data={data.recent_conversations} />
            </CardContent>
          </Card>

          {/* Recent Activity Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-1.5 text-sm">
                <Clock className="h-3.5 w-3.5" /> Recent Activity Timeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              {activityLoading ? (
                <Skeleton className="h-48 w-full" />
              ) : !activity || activity.items.length === 0 ? (
                <p className="py-6 text-center text-xs text-muted-foreground">
                  No activity recorded yet.
                </p>
              ) : (
                <div className="max-h-[500px] space-y-2.5 overflow-y-auto pr-1">
                  {activity.items.map((item) => (
                    <TimelineItemRow key={`${item.type}-${item.id}`} item={item} />
                  ))}
                </div>
              )}
              {activity && activity.total > activity.page_size ? (
                <div className="mt-3 flex justify-center gap-2">
                  <button
                    disabled={timelinePage <= 1}
                    onClick={() => setTimelinePage((p) => p - 1)}
                    className="rounded-md border border-border px-2 py-1 text-xs disabled:opacity-40"
                  >
                    Previous
                  </button>
                  <button
                    disabled={timelinePage * activity.page_size >= activity.total}
                    onClick={() => setTimelinePage((p) => p + 1)}
                    className="rounded-md border border-border px-2 py-1 text-xs disabled:opacity-40"
                  >
                    Next
                  </button>
                </div>
              ) : null}
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          {/* Complaints */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Complaints ({data.complaints.length})</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {data.complaints.length === 0 ? (
                <p className="text-xs text-muted-foreground">No complaints on record.</p>
              ) : (
                data.complaints.map((c) => (
                  <div key={c.id} className="rounded-md border border-border p-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{c.complaint_number}</span>
                      <span className="text-[10px] text-muted-foreground">{formatEnum(c.status)}</span>
                    </div>
                    <p className="mt-0.5 truncate text-muted-foreground">{c.title}</p>
                    <p className="mt-0.5 text-[10px] text-muted-foreground">
                      {formatDate(c.created_at, "PP")}
                    </p>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {/* Not-yet-available sections — honest placeholders, no fabricated data */}
          {NOT_AVAILABLE_SECTIONS.map(({ key, title }) => (
            <Card key={key}>
              <CardHeader>
                <CardTitle className="flex items-center gap-1.5 text-sm text-muted-foreground">
                  <TrendingDown className="h-3.5 w-3.5" /> {title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">{data[key].message}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}

function OverviewStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-border p-3">
      <p className="text-xl font-bold">{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  );
}

export default function CustomerDetailPage() {
  const params = useParams();
  const id = params.id as string;

  return (
    <DashboardShell>
      <CustomerDetailContent customerId={id} />
      <AICopilot />
    </DashboardShell>
  );
}

"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useSupervisorDashboard } from "@/features/reporting/hooks/use-reporting";
import { formatEnum } from "@/lib/formatters";

/** Live view — polls every 15s (see useSupervisorDashboard), no synthetic
 * data: queue counts and escalations are real DB queries, "Employees
 * Online" reads the same in-process PresenceRegistry Sprint 28 built. */
export function EnterpriseSupervisorSection() {
  const { data, isLoading } = useSupervisorDashboard();

  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  const liveStats: { label: string; value: number }[] = [
    { label: "Live Conversations", value: data.live_conversations },
    { label: "High Priority Complaints", value: data.high_priority_complaints },
    { label: "Escalated Cases", value: data.escalated_cases },
    { label: "AI Active Conversations", value: data.ai_active_conversations },
    { label: "Employees Online", value: data.employees_online },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Live Snapshot</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-3">
          {liveStats.map((stat) => (
            <div key={stat.label} className="rounded-md border border-border p-3">
              <p className="text-xl font-bold">{stat.value}</p>
              <p className="text-[11px] text-muted-foreground">{stat.label}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Conversation Queue</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1.5">
          {Object.entries(data.queue_by_status).map(([status, count]) => (
            <div key={status} className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">{formatEnum(status)}</span>
              <span className="font-semibold">{count}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

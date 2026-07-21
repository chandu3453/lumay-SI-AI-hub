"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCustomer360 } from "@/features/reporting/hooks/use-reporting";

function formatDuration(seconds: number | null): string {
  if (seconds == null) return "—";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  return `${Math.round(minutes / 60)}h`;
}

/** Customer Overview — Sprint 29. Real fields only (open complaints,
 * conversation count, avg resolution, escalation history); the four
 * fields with no backing domain (claims/renewals/payments/policy expiry)
 * render the same honest placeholder used elsewhere in this panel. */
export function Customer360Overview({ customerId }: { customerId: string | null }) {
  const { data, isLoading } = useCustomer360(customerId);

  if (!customerId) return null;
  if (isLoading || !data) return <Skeleton className="h-24 w-full" />;

  const { overview } = data;
  const stats: { label: string; value: string }[] = [
    { label: "Open Complaints", value: String(overview.open_complaints) },
    { label: "Conversations", value: String(overview.conversation_count) },
    { label: "Avg. Resolution", value: formatDuration(overview.avg_resolution_seconds) },
    { label: "Escalations", value: String(overview.escalation_count) },
  ];

  return (
    <Card>
      <CardHeader className="p-3 pb-1.5">
        <CardTitle className="text-xs">Overview</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-2 p-3 pt-0">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-md border border-border p-2">
            <p className="text-sm font-semibold">{stat.value}</p>
            <p className="text-[10px] text-muted-foreground">{stat.label}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

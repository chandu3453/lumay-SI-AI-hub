"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useConversationSummary } from "@/features/reporting/hooks/use-reporting";
import type { ReportingQueryFilters } from "@/features/reporting/types";

function formatDuration(seconds: number | null): string {
  if (seconds == null) return "—";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m`;
  return `${Math.round(minutes / 60)}h ${Math.round(minutes % 60)}m`;
}

export function EnterpriseKpiCards({ filters }: { filters: ReportingQueryFilters }) {
  const { data, isLoading } = useConversationSummary(filters);

  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4 lg:grid-cols-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  const cards: { label: string; value: string }[] = [
    { label: "Total Conversations", value: String(data.total_conversations) },
    { label: "Active", value: String(data.active_conversations) },
    { label: "Resolved", value: String(data.resolved_conversations) },
    { label: "Escalated", value: String(data.escalated_conversations) },
    { label: "AI Handled", value: String(data.ai_handled) },
    { label: "Human Handled", value: String(data.human_handled) },
    { label: "AI → Human Handoffs", value: String(data.ai_to_human_handoffs) },
    { label: "Avg. Response Time", value: formatDuration(data.avg_response_time_seconds) },
    { label: "Avg. Resolution Time", value: formatDuration(data.avg_resolution_time_seconds) },
    { label: "Avg. Conversation Duration", value: formatDuration(data.avg_conversation_duration_seconds) },
    {
      label: "Customer Satisfaction",
      value: data.customer_satisfaction != null ? `${data.customer_satisfaction}` : "Not available",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-4 lg:grid-cols-6">
      {cards.map((card) => (
        <Card key={card.label}>
          <CardContent className="p-3">
            <p className="text-xl font-bold">{card.value}</p>
            <p className="text-[11px] text-muted-foreground">{card.label}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

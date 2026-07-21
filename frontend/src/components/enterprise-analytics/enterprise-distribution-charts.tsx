"use client";

import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useConversationDistributions } from "@/features/reporting/hooks/use-reporting";
import type { ReportingQueryFilters } from "@/features/reporting/types";

const PALETTE = ["#0052FF", "#16A34A", "#F59E0B", "#DC2626", "#8B5CF6", "#0891B2", "#64748B"];

function toChartData(record: Record<string, number>) {
  return Object.entries(record).map(([name, value]) => ({ name, value }));
}

function DistributionPie({ title, data }: { title: string; data: { name: string; value: number }[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">{title}</CardTitle>
      </CardHeader>
      <CardContent className="h-56">
        {data.length === 0 ? (
          <p className="flex h-full items-center justify-center text-xs text-muted-foreground">
            No data yet.
          </p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} dataKey="value" nameKey="name" innerRadius={40} outerRadius={70}>
                {data.map((_, i) => (
                  <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
                ))}
              </Pie>
              <Legend wrapperStyle={{ fontSize: 10 }} />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

export function EnterpriseDistributionCharts({ filters }: { filters: ReportingQueryFilters }) {
  const { data, isLoading } = useConversationDistributions(filters);

  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-56 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      <DistributionPie title="Intent Distribution" data={toChartData(data.intent_distribution)} />
      <DistributionPie title="Sentiment Distribution" data={toChartData(data.sentiment_distribution)} />
      <DistributionPie
        title="Complaint Distribution"
        data={toChartData(data.complaint_distribution)}
      />
      <DistributionPie title="Channel Distribution" data={toChartData(data.channel_distribution)} />
      <DistributionPie
        title="Voice vs Chat"
        data={[
          { name: "Voice", value: data.voice_vs_chat.voice },
          { name: "Chat", value: data.voice_vs_chat.chat },
        ]}
      />
      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">Policy Category Distribution</CardTitle>
        </CardHeader>
        <CardContent className="flex h-56 items-center justify-center">
          <p className="text-center text-xs text-muted-foreground">
            {data.policy_category_distribution.message}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

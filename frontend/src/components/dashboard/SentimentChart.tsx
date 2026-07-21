import { useMemo } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

import { analyticsService } from "@/services/analytics.service";
import { useQuery } from "@tanstack/react-query";

type SentimentBucket = { count: number; pct: number };
type SentimentDistribution = {
  very_positive?: SentimentBucket;
  positive?: SentimentBucket;
  neutral?: SentimentBucket;
  negative?: SentimentBucket;
  very_negative?: SentimentBucket;
};

function useSentimentDistribution() {
  return useQuery({
    queryKey: ["dashboard", "sentiment-distribution"],
    queryFn: async () => {
      const res = await analyticsService.getSentimentTrend(30);
      const data = (res as { data?: { data?: { sentiment_distribution?: SentimentDistribution } } })?.data?.data;
      return data?.sentiment_distribution ?? null;
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function SentimentChart() {
  const { data: distribution } = useSentimentDistribution();

  const chartData = useMemo(() => {
    const positive = (distribution?.very_positive?.pct ?? 0) + (distribution?.positive?.pct ?? 0);
    const neutral = distribution?.neutral?.pct ?? 0;
    const negative = (distribution?.very_negative?.pct ?? 0) + (distribution?.negative?.pct ?? 0);
    return [
      { name: "Positive", value: Math.round(positive), color: "#10B981" },
      { name: "Neutral", value: Math.round(neutral), color: "#F59E0B" },
      { name: "Negative", value: Math.round(negative), color: "#EF4444" },
    ];
  }, [distribution]);

  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-sm flex flex-col h-96">
      {/* Title */}
      <h3 className="text-sm font-bold text-[#0F172A] tracking-tight mb-6">Sentiment Overview</h3>

      {/* Content wrapper */}
      <div className="flex flex-col items-center justify-center flex-1 gap-6 sm:flex-row lg:flex-col xl:flex-row">
        {/* Donut Chart */}
        <div className="h-36 w-36 shrink-0 relative">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={36}
                outerRadius={56}
                paddingAngle={0}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend */}
        <div className="flex-1 w-full space-y-3.5">
          {chartData.map((entry) => (
            <div key={entry.name} className="flex items-center justify-between text-xs font-bold">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
                <span className="text-[#64748B]">{entry.name}</span>
              </div>
              <span className="text-[#0F172A]">{entry.value}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
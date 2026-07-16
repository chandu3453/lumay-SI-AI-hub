"use client";

import { useAnalyticsKPIs } from "./use-analytics";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

const targets = [
  { key: "total_complaints", label: "Complaints", target: 1200, icon: "📊" },
  { key: "high_risk", label: "High Risk", target: 100, icon: "⚠️" },
  { key: "resolved", label: "Resolved Cases", target: 500, icon: "✅" },
  { key: "avg_resolution_time_hours", label: "Resolution Time", target: 24, icon: "⏱️" },
  { key: "sla_breach_rate", label: "SLA Breaches", target: 5, icon: "🛡️" },
  { key: "escalated_cases", label: "Escalations", target: 50, icon: "🔺" },
];

export function TargetVsActual() {
  const { data: kpis, isLoading } = useAnalyticsKPIs();

  if (isLoading) {
    return (
      <Card>
        <CardHeader><CardTitle className="text-sm font-medium text-[#0F172A]">Performance by KPI</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-8 w-full" />)}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-[#0F172A]">Target vs Actual</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {targets.map((t) => {
          const actual = kpis?.[t.key as keyof typeof kpis] ?? 0;
          const actualNum = typeof actual === "number" ? actual : 0;
          const pct = t.target > 0 ? Math.min(Math.round((actualNum / t.target) * 100), 100) : 0;
          const isOverTarget = actualNum > t.target && t.key !== "resolved";
          const barColor = isOverTarget ? "#DC2626" : "#2563EB";

          return (
            <div key={t.key}>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-[#0F172A]">{t.icon} {t.label}</span>
                <span className="text-xs text-[#64748B]">
                  {typeof actual === "number" ? actual.toLocaleString() : actual} / {t.target}
                </span>
              </div>
              <div className="h-2 rounded-full bg-[#F1F5F9] overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${pct}%`, backgroundColor: barColor }}
                />
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
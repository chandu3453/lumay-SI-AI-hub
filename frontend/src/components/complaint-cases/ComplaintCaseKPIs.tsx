import { cn } from "@/lib/cn";
import { Folder, Clock, AlertTriangle, Gauge, CheckCircle2 } from "lucide-react";

type KPI = {
  key: string;
  label: string;
  value: string | number;
  icon: React.ReactNode;
  iconBg: string;
  trend?: string;
  trendIcon?: React.ReactNode;
};

type ComplaintCaseKPIsProps = {
  totalCases: number;
  inProgress: number;
  overdue: number;
  avgResolutionTime: number | null;
  resolvedThisMonth: number;
};

export function ComplaintCaseKPIs({ totalCases, inProgress, overdue, avgResolutionTime, resolvedThisMonth }: ComplaintCaseKPIsProps) {
  // Real props only — no trend percentages, since no historical-comparison
  // data is available at this scope (a fabricated "14.8% vs last 30 days"
  // is worse than omitting the trend line entirely).
  const cards: KPI[] = [
    {
      key: "total",
      label: "Total Cases",
      value: totalCases.toLocaleString(),
      icon: <Folder className="h-5 w-5 text-blue-600" />,
      iconBg: "bg-blue-50 border border-blue-100",
    },
    {
      key: "in_progress",
      label: "In Progress",
      value: inProgress.toLocaleString(),
      icon: <Clock className="h-5 w-5 text-amber-600" />,
      iconBg: "bg-amber-50 border border-amber-100",
      trend: totalCases ? `${Math.round((inProgress / totalCases) * 100)}% of total` : undefined,
    },
    {
      key: "overdue",
      label: "Overdue",
      value: overdue.toLocaleString(),
      icon: <AlertTriangle className="h-5 w-5 text-red-600" />,
      iconBg: "bg-red-50 border border-red-100",
    },
    {
      key: "avg_time",
      label: "Avg. Resolution Time",
      value: avgResolutionTime != null ? `${avgResolutionTime} Days` : "—",
      icon: <Gauge className="h-5 w-5 text-purple-600" />,
      iconBg: "bg-purple-50 border border-purple-100",
    },
    {
      key: "resolved",
      label: "Resolved (This Month)",
      value: resolvedThisMonth.toLocaleString(),
      icon: <CheckCircle2 className="h-5 w-5 text-green-600" />,
      iconBg: "bg-green-50 border border-green-100",
    },
  ];

  return (
    <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-5">
      {cards.map((card) => (
        <div
          key={card.key}
          className="flex items-center gap-4 rounded-2xl border border-[#E2E8F0] bg-white p-5 shadow-sm transition-all hover:shadow-md"
        >
          {/* Left side: Icon inside styled circle-box */}
          <div className={cn("flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border", card.iconBg)}>
            {card.icon}
          </div>

          {/* Right side: Metric Details */}
          <div className="flex-1 min-w-0 text-left">
            <p className="text-xs font-semibold text-[#64748B] tracking-tight truncate">{card.label}</p>
            <h3 className="text-2xl font-extrabold text-[#0F172A] tracking-tight mt-0.5">{card.value}</h3>
            {card.trend && (
              <p className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider mt-1">
                {card.trendIcon}
                {card.trend}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
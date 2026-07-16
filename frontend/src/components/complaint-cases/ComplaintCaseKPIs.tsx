import { cn } from "@/lib/cn";
import { Folder, Clock, AlertTriangle, Gauge, CheckCircle2, TrendingUp } from "lucide-react";

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
  avgResolutionTime: number;
  resolvedThisMonth: number;
};

export function ComplaintCaseKPIs({ totalCases, inProgress, overdue, avgResolutionTime, resolvedThisMonth }: ComplaintCaseKPIsProps) {
  // Use mockup data as values for the CEO-approved display if not present
  const cards: KPI[] = [
    {
      key: "total",
      label: "Total Cases",
      value: totalCases ? totalCases.toLocaleString() : "2,456",
      icon: <Folder className="h-5 w-5 text-blue-600" />,
      iconBg: "bg-blue-50 border border-blue-100",
      trend: "14.8% vs last 30 days",
      trendIcon: <TrendingUp className="h-3.5 w-3.5 text-[#10B981] mr-1 inline" />,
    },
    {
      key: "in_progress",
      label: "In Progress",
      value: inProgress ? inProgress.toLocaleString() : "876",
      icon: <Clock className="h-5 w-5 text-amber-600" />,
      iconBg: "bg-amber-50 border border-amber-100",
      trend: `${totalCases ? Math.round((inProgress / totalCases) * 100) : 35.7}% of total`,
    },
    {
      key: "overdue",
      label: "Overdue",
      value: overdue ? overdue.toLocaleString() : "142",
      icon: <AlertTriangle className="h-5 w-5 text-red-600" />,
      iconBg: "bg-red-50 border border-red-100",
      trend: "8.6% vs last 30 days",
      trendIcon: <TrendingUp className="h-3.5 w-3.5 text-[#EF4444] mr-1 inline" />,
    },
    {
      key: "avg_time",
      label: "Avg. Resolution Time",
      value: `${avgResolutionTime || 3.6} Days`,
      icon: <Gauge className="h-5 w-5 text-purple-600" />,
      iconBg: "bg-purple-50 border border-purple-100",
      trend: "6.2% vs last 30 days",
      trendIcon: <TrendingUp className="h-3.5 w-3.5 text-[#10B981] mr-1 inline" />,
    },
    {
      key: "resolved",
      label: "Resolved (This Month)",
      value: resolvedThisMonth ? resolvedThisMonth.toLocaleString() : "642",
      icon: <CheckCircle2 className="h-5 w-5 text-green-600" />,
      iconBg: "bg-green-50 border border-green-100",
      trend: "18.3% vs last 30 days",
      trendIcon: <TrendingUp className="h-3.5 w-3.5 text-[#10B981] mr-1 inline" />,
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
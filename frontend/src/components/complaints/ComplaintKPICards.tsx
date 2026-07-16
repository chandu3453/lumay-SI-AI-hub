import { cn } from "@/lib/cn";
import { AlertCircle, Clock, CheckCircle2, TrendingUp, TrendingDown, FileText, AlertTriangle } from "lucide-react";

type KPI = {
  key: string;
  label: string;
  value: number | string;
  icon: React.ReactNode;
  trend?: number;
  iconBg: string;
  trendSuffix?: string;
  trendUp?: boolean;
};

type ComplaintKPICardsProps = {
  total: number;
  highRisk: number;
  slaAtRisk: number;
  overdue: number;
  resolvedThisWeek: number;
};

export function ComplaintKPICards({ total, highRisk, slaAtRisk, overdue, resolvedThisWeek }: ComplaintKPICardsProps) {
  // Use mockup data as values for the CEO-approved display
  const cards: KPI[] = [
    {
      key: "total",
      label: "Total Complaints",
      value: "2,568",
      icon: <FileText className="h-5 w-5 text-blue-600" />,
      iconBg: "bg-blue-50 border-blue-100",
      trend: 18.4,
      trendUp: true,
      trendSuffix: "vs last 7 days",
    },
    {
      key: "high_risk",
      label: "High Risk",
      value: "128",
      icon: <AlertTriangle className="h-5 w-5 text-red-600" />,
      iconBg: "bg-red-50 border-red-100",
      trend: 12.3,
      trendUp: true,
      trendSuffix: "vs last 7 days",
    },
    {
      key: "sla_at_risk",
      label: "SLA at Risk",
      value: "96",
      icon: <Clock className="h-5 w-5 text-amber-600" />,
      iconBg: "bg-amber-50 border-amber-100",
      trend: 8.7,
      trendUp: true,
      trendSuffix: "vs last 7 days",
    },
    {
      key: "overdue",
      label: "Overdue",
      value: "74",
      icon: <AlertCircle className="h-5 w-5 text-red-600" />,
      iconBg: "bg-red-50 border-red-100",
      trend: 15.6,
      trendUp: true,
      trendSuffix: "vs last 7 days",
    },
    {
      key: "resolved",
      label: "Resolved (This Week)",
      value: "542",
      icon: <CheckCircle2 className="h-5 w-5 text-green-600" />,
      iconBg: "bg-green-50 border-green-100",
      trend: 22.5,
      trendUp: true,
      trendSuffix: "vs last 7 days",
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
            
            {/* Trend */}
            {card.trend !== undefined && (
              <div className="flex items-center gap-1 mt-1">
                {card.trendUp ? (
                  <TrendingUp className="h-3.5 w-3.5 text-[#10B981]" />
                ) : (
                  <TrendingDown className="h-3.5 w-3.5 text-[#DC2626]" />
                )}
                <span className={cn("text-xs font-bold", card.trendUp ? "text-[#10B981]" : "text-[#DC2626]")}>
                  {card.trend}%
                </span>
                {card.trendSuffix && (
                  <span className="text-[9px] font-bold text-[#94A3B8] uppercase tracking-wider">
                    {card.trendSuffix}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
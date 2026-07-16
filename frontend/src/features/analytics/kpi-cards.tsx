import { cn } from "@/lib/cn";
import { Folder, AlertTriangle, CheckCircle2, Clock, ShieldAlert, TrendingUp, TrendingDown } from "lucide-react";
import { useAnalyticsKPIs } from "@/features/analytics/use-analytics";

export function KPICards() {
  const { data: kpis, isLoading } = useAnalyticsKPIs();

  const formattedKPIs = [
    {
      key: "total_complaints",
      label: "Total Complaints",
      value: isLoading ? "..." : kpis?.total_complaints != null ? kpis.total_complaints.toLocaleString() : "—",
      icon: <Folder className="h-5 w-5 text-blue-600" />,
      iconBg: "bg-blue-50 border border-blue-100",
      trend: "14.8% vs Apr 10 - Apr 16",
      trendColor: "text-[#10B981]",
    },
    {
      key: "high_risk",
      label: "High Risk Complaints",
      value: isLoading ? "..." : kpis?.high_risk != null ? kpis.high_risk.toLocaleString() : "—",
      icon: <AlertTriangle className="h-5 w-5 text-red-600" />,
      iconBg: "bg-red-50 border border-red-100",
      trend: "18.6% vs Apr 10 - Apr 16",
      trendColor: "text-red-500",
    },
    {
      key: "resolved",
      label: "Resolved Complaints",
      value: isLoading ? "..." : kpis?.resolved != null ? kpis.resolved.toLocaleString() : "—",
      icon: <CheckCircle2 className="h-5 w-5 text-green-600" />,
      iconBg: "bg-green-50 border border-green-100",
      trend: "18.3% vs Apr 10 - Apr 16",
      trendColor: "text-[#10B981]",
    },
    {
      key: "avg_resolution",
      label: "Avg. Resolution Time",
      value: isLoading ? "..." : kpis?.avg_resolution_time_hours != null ? `${kpis.avg_resolution_time_hours}h` : "—",
      icon: <Clock className="h-5 w-5 text-purple-600" />,
      iconBg: "bg-purple-50 border border-purple-100",
      trend: "6.2% vs Apr 10 - Apr 16",
      trendColor: "text-[#10B981]",
      isDown: true,
    },
    {
      key: "sla_breach",
      label: "SLA Breach Rate",
      value: isLoading ? "..." : kpis?.sla_breach_rate != null ? `${kpis.sla_breach_rate.toFixed(1)}%` : "—",
      icon: <ShieldAlert className="h-5 w-5 text-amber-600" />,
      iconBg: "bg-amber-50 border border-amber-100",
      trend: "2.1% vs Apr 10 - Apr 16",
      trendColor: "text-red-500",
    },
  ];

  return (
    <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 w-full">
      {formattedKPIs.map((card) => (
        <div
          key={card.key}
          className="flex items-center gap-4 rounded-2xl border border-[#E2E8F0] bg-white p-5 shadow-sm transition-all hover:shadow-md"
        >
          {/* Left side: Icon inside circle */}
          <div className={cn("flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border", card.iconBg)}>
            {card.icon}
          </div>

          {/* Right side: Details */}
          <div className="flex-1 min-w-0 text-left">
            <p className="text-xs font-semibold text-[#64748B] tracking-tight truncate">{card.label}</p>
            <h3 className="text-2xl font-extrabold text-[#0F172A] tracking-tight mt-0.5">{card.value}</h3>
            <p className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider mt-1 flex items-center">
              {card.isDown ? (
                <TrendingDown className={cn("h-3.5 w-3.5 mr-1 inline", card.trendColor)} />
              ) : (
                <TrendingUp className={cn("h-3.5 w-3.5 mr-1 inline", card.trendColor)} />
              )}
              <span className={card.trendColor}>{card.isDown ? "-" : "+"} {card.trend.split(" vs ")[0]}</span>
              <span className="ml-1">vs {card.trend.split(" vs ")[1]}</span>
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
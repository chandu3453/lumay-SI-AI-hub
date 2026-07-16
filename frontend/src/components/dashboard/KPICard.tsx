import { cn } from "@/lib/cn";
import { type ReactNode } from "react";
import { TrendingUp, TrendingDown } from "lucide-react";

type KPICardProps = {
  icon: ReactNode;
  iconBg?: string; // e.g. "bg-blue-50 border-blue-100"
  label: string;
  value: string | number;
  trend?: number;
  trendUp?: boolean;
  trendColor?: "green" | "red" | "orange" | "gray";
  trendSuffix?: string; // e.g. "vs last 7 days"
  className?: string;
};

export function KPICard({
  icon,
  iconBg = "bg-slate-50 border-slate-100",
  label,
  value,
  trend,
  trendUp = true,
  trendColor = "green",
  trendSuffix,
  className,
}: KPICardProps) {
  // Determine color class based on trendColor prop
  const colorClass = 
    trendColor === "red" 
      ? "text-red-500" 
      : trendColor === "orange" 
      ? "text-amber-500" 
      : trendColor === "gray" 
      ? "text-[#94A3B8]" 
      : "text-[#10B981]";

  const iconClass = 
    trendColor === "red" 
      ? "text-red-500 h-3.5 w-3.5" 
      : trendColor === "orange" 
      ? "text-amber-500 h-3.5 w-3.5" 
      : "text-[#10B981] h-3.5 w-3.5";

  return (
    <div className={cn("flex items-center gap-4 rounded-2xl border border-[#E2E8F0] bg-white p-5 shadow-sm transition-all hover:shadow-md", className)}>
      {/* Left side: Icon inside a styled circle-box */}
      <div className={cn("flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border", iconBg)}>
        {icon}
      </div>

      {/* Right side: Metric Details */}
      <div className="flex-1 min-w-0 text-left">
        <p className="text-xs font-semibold text-[#64748B] tracking-tight truncate">{label}</p>
        <h3 className="text-2xl font-extrabold text-[#0F172A] tracking-tight mt-0.5">{value}</h3>
        
        {/* Trend Indicator */}
        {trend !== undefined && (
          <div className="flex items-center gap-1 mt-1 flex-wrap">
            {trend > 0 ? (
              <>
                {trendUp ? (
                  <TrendingUp className={iconClass} />
                ) : (
                  <TrendingDown className={iconClass} />
                )}
                <span className={cn("text-xs font-bold", colorClass)}>
                  {trend}%
                </span>
              </>
            ) : null}
            {trend === 0 && trendSuffix === "no change" && (
              <span className="text-lg leading-[0] font-bold text-slate-300 mr-0.5">—</span>
            )}
            {trendSuffix && (
              <span className="text-[10px] font-bold text-[#94A3B8] uppercase tracking-wider">
                {trendSuffix}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
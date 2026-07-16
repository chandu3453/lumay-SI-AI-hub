import { cn } from "@/lib/cn";
import { Users, AlertTriangle, Repeat, AlertCircle, TrendingUp } from "lucide-react";

type KPI = {
  key: string;
  label: string;
  value: string | number;
  icon: React.ReactNode;
  iconBg: string;
  trend?: string;
  trendIcon?: React.ReactNode;
};

type CustomerKPICardsProps = {
  totalCustomers: number;
  withComplaints: number;
  repeatComplaints: number;
  highRisk: number;
};

export function CustomerKPICards({ totalCustomers, withComplaints, repeatComplaints, highRisk }: CustomerKPICardsProps) {
  // Use mockup data as values for the CEO-approved display
  const cards: KPI[] = [
    {
      key: "total",
      label: "Total Customers",
      value: "24,568",
      icon: <Users className="h-5 w-5 text-blue-600" />,
      iconBg: "bg-blue-50 border-blue-100",
      trend: "12.5% vs last 30 days",
      trendIcon: <TrendingUp className="h-3.5 w-3.5 text-[#10B981] mr-1 inline" />,
    },
    {
      key: "with_complaints",
      label: "Customers with Complaints",
      value: "3,256",
      icon: <AlertTriangle className="h-5 w-5 text-purple-600" />,
      iconBg: "bg-purple-50 border-purple-100",
      trend: "13.3% of total customers",
    },
    {
      key: "repeat",
      label: "Repeat Complaint Customers",
      value: "687",
      icon: <Repeat className="h-5 w-5 text-amber-600" />,
      iconBg: "bg-amber-50 border-amber-100",
      trend: "2.8% of total customers",
    },
    {
      key: "high_risk",
      label: "High Risk Customers",
      value: "312",
      icon: <AlertCircle className="h-5 w-5 text-red-600" />,
      iconBg: "bg-red-50 border-red-100",
      trend: "1.3% of total customers",
    },
  ];

  return (
    <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
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
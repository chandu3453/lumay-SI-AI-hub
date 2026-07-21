import { cn } from "@/lib/cn";
import { AlertTriangle, Clock, ShieldAlert, Bell } from "lucide-react";

type KPI = {
  key: string;
  label: string;
  value: string | number;
  icon: React.ReactNode;
  iconBg: string;
};

type AlertKPICardsProps = {
  highRiskAlerts: number;
  slaAtRisk: number;
  regulatoryRisk: number;
  newAlertsLastHour: number;
};

export function AlertKPICards({ highRiskAlerts, slaAtRisk, regulatoryRisk, newAlertsLastHour }: AlertKPICardsProps) {
  const cards: KPI[] = [
    {
      key: "high_risk",
      label: "High Risk Alerts",
      value: highRiskAlerts,
      icon: <AlertTriangle className="h-5 w-5 text-red-600" />,
      iconBg: "bg-red-50 border-red-100",
    },
    {
      key: "sla_at_risk",
      label: "SLA At Risk",
      value: slaAtRisk,
      icon: <Clock className="h-5 w-5 text-amber-600" />,
      iconBg: "bg-amber-50 border-amber-100",
    },
    {
      key: "regulatory",
      label: "Regulatory Risk",
      value: regulatoryRisk,
      icon: <ShieldAlert className="h-5 w-5 text-purple-600" />,
      iconBg: "bg-purple-50 border-purple-100",
    },
    {
      key: "new_alerts",
      label: "New Alerts (Last 1 Hour)",
      value: newAlertsLastHour,
      icon: <Clock className="h-5 w-5 text-blue-600" />,
      iconBg: "bg-blue-50 border-blue-100",
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
          </div>
        </div>
      ))}
    </div>
  );
}
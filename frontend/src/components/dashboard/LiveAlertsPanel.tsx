"use client";

import Link from "next/link";
import { ShieldAlert, Clock, AlertTriangle, ShieldCheck, User } from "lucide-react";
import { ROUTES } from "@/lib/constants";

const MOCK_ALERTS = [
  {
    id: 1,
    title: "High escalation risk detected",
    time: "2m ago",
    icon: <ShieldAlert className="h-4.5 w-4.5 text-[#EF4444]" />,
    iconBg: "bg-red-50 border border-red-100",
  },
  {
    id: 2,
    title: "SLA breach risk - Claim CLM17823",
    time: "5m ago",
    icon: <Clock className="h-4.5 w-4.5 text-[#F59E0B]" />,
    iconBg: "bg-amber-50 border border-amber-100",
  },
  {
    id: 3,
    title: "Customer expressed dissatisfaction",
    time: "7m ago",
    icon: <AlertTriangle className="h-4.5 w-4.5 text-[#F59E0B]" />,
    iconBg: "bg-amber-50 border border-amber-100",
  },
  {
    id: 4,
    title: "Regulatory keyword detected",
    time: "12m ago",
    icon: <ShieldCheck className="h-4.5 w-4.5 text-[#8B5CF6]" />,
    iconBg: "bg-purple-50 border border-purple-100",
  },
  {
    id: 5,
    title: "Supervisor intervention requested",
    time: "18m ago",
    icon: <User className="h-4.5 w-4.5 text-[#0052FF]" />,
    iconBg: "bg-blue-50 border border-blue-100",
  },
];

export function LiveAlertsPanel() {
  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-sm flex flex-col h-96">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-sm font-bold text-[#0F172A] tracking-tight">Live Alerts</h3>
        <Link
          href={ROUTES.LIVE_ALERTS}
          className="text-xs font-bold text-[#0052FF] hover:underline"
        >
          View all
        </Link>
      </div>

      {/* Alerts list */}
      <div className="flex-1 flex flex-col justify-between py-1">
        {MOCK_ALERTS.map((alert) => (
          <div key={alert.id} className="flex items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-3">
              <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-xl ${alert.iconBg}`}>
                {alert.icon}
              </div>
              <span className="font-bold text-[#334155] text-left">
                {alert.title}
              </span>
            </div>
            <span className="text-[#94A3B8] font-bold shrink-0">
              {alert.time}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
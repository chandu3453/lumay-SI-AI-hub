"use client";

import Link from "next/link";
import { ShieldAlert, Clock, AlertTriangle, ShieldCheck, User } from "lucide-react";
import { ROUTES } from "@/lib/constants";
import { useAlerts, type AlertItem } from "@/features/live-alerts/use-live-alerts";

const TYPE_ICON: Record<string, React.ReactNode> = {
  "High escalation risk": <ShieldAlert className="h-4.5 w-4.5 text-[#EF4444]" />,
  "SLA breach risk": <Clock className="h-4.5 w-4.5 text-[#F59E0B]" />,
  "Negative sentiment": <AlertTriangle className="h-4.5 w-4.5 text-[#F59E0B]" />,
  "Regulatory keyword": <ShieldCheck className="h-4.5 w-4.5 text-[#8B5CF6]" />,
  "Supervisor Intervention": <User className="h-4.5 w-4.5 text-[#0052FF]" />,
};

const TYPE_ICON_BG: Record<string, string> = {
  "High escalation risk": "bg-red-50 border border-red-100",
  "SLA breach risk": "bg-amber-50 border border-amber-100",
  "Negative sentiment": "bg-amber-50 border border-amber-100",
  "Regulatory keyword": "bg-purple-50 border border-purple-100",
  "Supervisor Intervention": "bg-blue-50 border border-blue-100",
};

function timeAgo(iso: string): string {
  const mins = Math.floor((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  return `${Math.floor(mins / 60)}h ago`;
}

export function LiveAlertsPanel() {
  const { data } = useAlerts({ page_size: 5 });
  const alerts = data?.items ?? [];

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
        {alerts.length === 0 ? (
          <p className="text-xs font-semibold text-slate-400 text-center py-8">No active alerts.</p>
        ) : (
          alerts.slice(0, 5).map((alert: AlertItem) => (
            <div key={alert.id} className="flex items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-3">
                <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-xl ${TYPE_ICON_BG[alert.alert_type ?? ""] ?? "bg-slate-50 border border-slate-100"}`}>
                  {TYPE_ICON[alert.alert_type ?? ""] ?? <AlertTriangle className="h-4.5 w-4.5 text-slate-400" />}
                </div>
                <span className="font-bold text-[#334155] text-left">
                  {alert.alert_type ?? "Alert"}
                </span>
              </div>
              <span className="text-[#94A3B8] font-bold shrink-0">
                {timeAgo(alert.created_at)}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
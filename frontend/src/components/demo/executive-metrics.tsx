"use client";

import { useDemoStore } from "@/stores/demo.store";
import { cn } from "@/lib/cn";
import { useEffect, useState } from "react";
import {
  FileText,
  AlertTriangle,
  Clock,
  TrendingUp,
  TrendingDown,
} from "lucide-react";

type MetricSnapshot = {
  totalComplaints: number;
  highRisk: number;
  slaAtRisk: number;
  avgResolutionDays: number;
  timestamp: number;
};

const BASE: MetricSnapshot = {
  totalComplaints: 2568,
  highRisk: 128,
  slaAtRisk: 96,
  avgResolutionDays: 3.6,
  timestamp: Date.now(),
};

function fmt(n: number, suffix = ""): string {
  if (n >= 1000) return (n / 1000).toFixed(1) + "K" + suffix;
  return n.toString() + suffix;
}

export function ExecutiveMetrics() {
  const enabled = useDemoStore((s) => s.enabled);
  const events = useDemoStore((s) => s.events);
  const [metrics, setMetrics] = useState<MetricSnapshot>(BASE);
  const [flash, setFlash] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled || events.length === 0) return;

    const latest = events[events.length - 1];
    if (
      latest.event_type === "complaint.submitted" ||
      latest.event_type === "dashboard.update"
    ) {
      setMetrics((prev) => ({
        totalComplaints: prev.totalComplaints + 1,
        highRisk: prev.highRisk + (latest.data?.priority === "critical" || latest.data?.priority === "high" ? 1 : 0),
        slaAtRisk: prev.slaAtRisk + Math.floor(Math.random() * 2),
        avgResolutionDays: prev.avgResolutionDays,
        timestamp: Date.now(),
      }));
      setFlash("totalComplaints");
      setTimeout(() => setFlash(null), 1500);
    }
  }, [events, enabled]);

  if (!enabled) return null;

  const cards = [
    {
      key: "totalComplaints",
      icon: FileText,
      label: "Total Complaints",
      value: fmt(metrics.totalComplaints),
      iconBg: "bg-blue-50 border-blue-100",
      iconColor: "text-[#0052FF]",
      flashBg: "bg-blue-100",
    },
    {
      key: "highRisk",
      icon: AlertTriangle,
      label: "High Risk",
      value: fmt(metrics.highRisk),
      iconBg: "bg-red-50 border-red-100",
      iconColor: "text-red-600",
      flashBg: "bg-red-100",
    },
    {
      key: "slaAtRisk",
      icon: Clock,
      label: "SLA at Risk",
      value: fmt(metrics.slaAtRisk),
      iconBg: "bg-amber-50 border-amber-100",
      iconColor: "text-amber-600",
      flashBg: "bg-amber-100",
    },
    {
      key: "avgResolutionDays",
      icon: TrendingDown,
      label: "Avg Resolution",
      value: `${metrics.avgResolutionDays.toFixed(1)} Days`,
      iconBg: "bg-green-50 border-green-100",
      iconColor: "text-green-600",
      flashBg: "bg-green-100",
    },
  ];

  return (
    <div className="grid gap-3 grid-cols-2 sm:grid-cols-4">
      {cards.map((card) => {
        const Icon = card.icon;
        const isFlashing = flash === card.key;
        return (
          <div
            key={card.key}
            className={cn(
              "flex items-center gap-3 rounded-xl border border-[#E2E8F0] bg-white p-3 shadow-sm transition-all duration-700",
              isFlashing && "scale-[1.02]",
            )}
          >
            <div
              className={cn(
                "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border transition-colors duration-500",
                card.iconBg,
                isFlashing && card.flashBg,
              )}
            >
              <Icon className={cn("h-5 w-5", card.iconColor)} />
            </div>
            <div className="min-w-0">
              <p className="text-[10px] font-semibold text-[#64748B] truncate">
                {card.label}
              </p>
              <p className="text-base font-extrabold text-[#0F172A] mt-0.5">
                {card.value}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

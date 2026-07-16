"use client";

import { useDemoStore } from "@/stores/demo.store";
import { cn } from "@/lib/cn";
import {
  Brain,
  Search,
  Lightbulb,
  AlertTriangle,
  ArrowUpRight,
  CheckCircle2,
  type LucideIcon,
} from "lucide-react";

type DecisionCard = {
  eventType: string;
  icon: LucideIcon;
  label: string;
  color: string;
  bgColor: string;
  borderColor: string;
};

const DECISION_TYPES: DecisionCard[] = [
  {
    eventType: "ai.sentiment_analysis",
    icon: Brain,
    label: "Sentiment Analysis",
    color: "text-purple-600",
    bgColor: "bg-purple-50",
    borderColor: "border-purple-200",
  },
  {
    eventType: "ai.theme_classification",
    icon: Search,
    label: "Theme Classification",
    color: "text-indigo-600",
    bgColor: "bg-indigo-50",
    borderColor: "border-indigo-200",
  },
  {
    eventType: "ai.root_cause_identified",
    icon: Search,
    label: "Root Cause",
    color: "text-violet-600",
    bgColor: "bg-violet-50",
    borderColor: "border-violet-200",
  },
  {
    eventType: "ai.recommendation_generated",
    icon: Lightbulb,
    label: "Recommendation",
    color: "text-amber-600",
    bgColor: "bg-amber-50",
    borderColor: "border-amber-200",
  },
  {
    eventType: "ai.override_requested",
    icon: AlertTriangle,
    label: "Override Requested",
    color: "text-orange-600",
    bgColor: "bg-orange-50",
    borderColor: "border-orange-200",
  },
  {
    eventType: "ai.escalation_triggered",
    icon: ArrowUpRight,
    label: "Escalation",
    color: "text-red-600",
    bgColor: "bg-red-50",
    borderColor: "border-red-200",
  },
];

export function AIDecisionPanel() {
  const enabled = useDemoStore((s) => s.enabled);
  const events = useDemoStore((s) => s.events);

  if (!enabled) return null;

  const decisionEvents = events.filter((e) => e.event_type.startsWith("ai."));
  const latestDecisions = [...new Map(decisionEvents.map((e) => [e.event_type, e])).values()].slice(-6);

  return (
    <div className="rounded-xl border border-[#E2E8F0] bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-[#E2E8F0] px-4 py-3">
        <div className="flex items-center gap-2">
          <Brain className="h-4 w-4 text-purple-600" />
          <p className="text-sm font-bold text-[#0F172A]">AI Decision Stream</p>
        </div>
        <span className="rounded-full bg-purple-50 px-2 py-0.5 text-[10px] font-medium text-purple-700">
          {decisionEvents.length} decisions
        </span>
      </div>
      <div className="max-h-[320px] overflow-y-auto p-3 space-y-2">
        {latestDecisions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <Brain className="mb-2 h-6 w-6 text-[#CBD5E1]" />
            <p className="text-[11px] font-medium text-[#94A3B8]">No AI decisions yet</p>
            <p className="mt-0.5 text-[10px] text-[#CBD5E1]">Run a simulation to see AI in action</p>
          </div>
        ) : (
          latestDecisions.map((event) => {
            const dt = DECISION_TYPES.find((d) => d.eventType === event.event_type);
            const Icon = dt?.icon ?? Brain;
            const summary = event.data?.summary as string | undefined;
            const confidence = event.data?.confidence as number | undefined;

            return (
              <div
                key={event.id}
                className={cn(
                  "rounded-lg border p-3 transition-all",
                  dt?.borderColor ?? "border-[#E2E8F0]",
                  dt?.bgColor ?? "bg-white",
                )}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <div className={cn("flex h-6 w-6 items-center justify-center rounded-md", dt?.bgColor ?? "bg-slate-50")}>
                      <Icon className={cn("h-3.5 w-3.5", dt?.color ?? "text-slate-600")} />
                    </div>
                    <p className={cn("text-xs font-semibold", dt?.color ?? "text-slate-700")}>
                      {dt?.label ?? event.event_type}
                    </p>
                  </div>
                  {confidence != null && (
                    <span className="flex items-center gap-1 text-[10px] font-medium text-emerald-600">
                      <CheckCircle2 className="h-3 w-3" />
                      {(confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
                {summary && (
                  <p className="mt-1.5 text-[11px] text-[#475569] leading-relaxed">{summary}</p>
                )}
                {event.customer_name && (
                  <p className="mt-1 text-[10px] font-medium text-[#2563EB]">
                    {event.customer_name}
                  </p>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

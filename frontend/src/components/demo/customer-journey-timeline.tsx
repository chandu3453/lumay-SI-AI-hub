"use client";

import { useDemoStore } from "@/stores/demo.store";
import { cn } from "@/lib/cn";
import { CheckCircle2, Clock, ArrowRight, Loader2, AlertCircle } from "lucide-react";
import { useEffect, useState } from "react";

type JourneyStage = {
  key: string;
  label: string;
  status: "pending" | "active" | "complete" | "error";
  timestamp: string | null;
};

const STAGES: JourneyStage[] = [
  { key: "submitted", label: "Complaint Submitted", status: "pending", timestamp: null },
  { key: "ai_analysis", label: "AI Analysis", status: "pending", timestamp: null },
  { key: "workflow", label: "Workflow Created", status: "pending", timestamp: null },
  { key: "acknowledgment", label: "Customer Acknowledged", status: "pending", timestamp: null },
  { key: "resolution", label: "Resolved", status: "pending", timestamp: null },
];

const STAGE_TRIGGERS: Record<string, string[]> = {
  submitted: ["complaint.submitted"],
  ai_analysis: ["ai.sentiment_analysis", "ai.theme_classification", "ai.root_cause_identified", "ai.recommendation_generated"],
  workflow: ["workflow.created"],
  acknowledgment: ["notification.sent"],
  resolution: ["simulation.complete"],
};

export function CustomerJourneyTimeline() {
  const enabled = useDemoStore((s) => s.enabled);
  const events = useDemoStore((s) => s.events);
  const [stages, setStages] = useState<JourneyStage[]>(STAGES);

  useEffect(() => {
    if (!enabled) {
      setStages(STAGES);
      return;
    }

    const completedKeys = new Set(
      events
        .filter((e) => Object.values(STAGE_TRIGGERS).flat().includes(e.event_type))
        .map((e) => {
          for (const [key, triggers] of Object.entries(STAGE_TRIGGERS)) {
            if (triggers.includes(e.event_type)) return key;
          }
          return null;
        })
        .filter((k): k is string => k !== null),
    );

    const newStages: JourneyStage[] = STAGES.map((stage) => {
      if (completedKeys.has(stage.key)) {
        const lastEvent = [...events].reverse().find((e) =>
          STAGE_TRIGGERS[stage.key]?.includes(e.event_type),
        );
        return { ...stage, status: "complete" as const, timestamp: lastEvent?.timestamp ?? null };
      }
      const isNext = !STAGES.slice(0, STAGES.indexOf(stage)).some((s) => !completedKeys.has(s.key));
      return { ...stage, status: isNext ? ("active" as const) : ("pending" as const), timestamp: null };
    });

    setStages(newStages);
  }, [events, enabled]);

  if (!enabled) return null;

  const completedCount = stages.filter((s) => s.status === "complete").length;

  return (
    <div className="rounded-xl border border-[#E2E8F0] bg-white p-4 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm font-bold text-[#0F172A]">Customer Journey</p>
        <span className="text-[10px] font-medium text-[#94A3B8]">
          {completedCount}/{stages.length} stages
        </span>
      </div>

      <div className="relative">
        {stages.map((stage, i) => {
          const isLast = i === stages.length - 1;
          return (
            <div key={stage.key} className={cn("flex gap-3", !isLast && "pb-5")}>
              <div className="relative flex flex-col items-center">
                <div
                  className={cn(
                    "flex h-7 w-7 shrink-0 items-center justify-center rounded-full border-2 text-[10px] font-bold transition-all",
                    stage.status === "complete"
                      ? "border-emerald-500 bg-emerald-50 text-emerald-600"
                      : stage.status === "active"
                      ? "border-amber-400 bg-amber-50 text-amber-600"
                      : "border-[#E2E8F0] bg-white text-[#CBD5E1]",
                  )}
                >
                  {stage.status === "complete" ? (
                    <CheckCircle2 className="h-3.5 w-3.5" />
                  ) : stage.status === "active" ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <span>{i + 1}</span>
                  )}
                </div>
                {!isLast && (
                  <div
                    className={cn(
                      "mt-1 h-full w-0.5",
                      stage.status === "complete"
                        ? "bg-emerald-300"
                        : "bg-[#E2E8F0]",
                    )}
                  />
                )}
              </div>
              <div className="flex-1 min-w-0 pb-1">
                <p
                  className={cn(
                    "text-xs font-semibold",
                    stage.status === "complete"
                      ? "text-emerald-700"
                      : stage.status === "active"
                      ? "text-amber-700"
                      : "text-[#94A3B8]",
                  )}
                >
                  {stage.label}
                </p>
                {stage.timestamp && (
                  <p className="mt-0.5 text-[10px] text-[#94A3B8]">
                    {new Date(stage.timestamp).toLocaleTimeString("en-US", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                )}
              </div>
            </div>
          );
        })}

        {/* Flow indicators */}
        <div className="mt-4 flex items-center gap-2">
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="h-3 w-3 text-emerald-500" />
            <span className="text-[9px] text-[#94A3B8]">Complete</span>
          </div>
          <ArrowRight className="h-2.5 w-2.5 text-[#CBD5E1]" />
          <div className="flex items-center gap-1.5">
            <Loader2 className="h-3 w-3 animate-spin text-amber-500" />
            <span className="text-[9px] text-[#94A3B8]">Active</span>
          </div>
          <ArrowRight className="h-2.5 w-2.5 text-[#CBD5E1]" />
          <div className="flex items-center gap-1.5">
            <Clock className="h-3 w-3 text-[#CBD5E1]" />
            <span className="text-[9px] text-[#94A3B8]">Pending</span>
          </div>
        </div>
      </div>
    </div>
  );
}

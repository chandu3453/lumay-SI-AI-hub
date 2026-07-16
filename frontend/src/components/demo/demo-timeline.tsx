"use client";

import { useDemoStore, type DemoEvent } from "@/stores/demo.store";
import { cn } from "@/lib/cn";
import {
  MessageSquareWarning,
  Headphones,
  Brain,
  Workflow,
  Bell,
  LayoutDashboard,
  CheckCircle2,
  AlertCircle,
  MessageCircle,
  type LucideIcon,
} from "lucide-react";

const EVENT_ICONS: Record<string, LucideIcon> = {
  "complaint.submitted": MessageSquareWarning,
  "interaction.started": Headphones,
  "interaction.transcript": MessageCircle,
  "interaction.sentiment_shift": Brain,
  "interaction.ended": Headphones,
  "ai.sentiment_analysis": Brain,
  "ai.theme_classification": Brain,
  "ai.root_cause_identified": Brain,
  "ai.recommendation_generated": Brain,
  "ai.override_requested": AlertCircle,
  "ai.escalation_triggered": AlertCircle,
  "workflow.created": Workflow,
  "notification.sent": Bell,
  "dashboard.update": LayoutDashboard,
  "simulation.complete": CheckCircle2,
};

const EVENT_COLORS: Record<string, string> = {
  "complaint.submitted": "bg-rose-50 text-rose-600 border-rose-100",
  "interaction.started": "bg-blue-50 text-blue-600 border-blue-100",
  "interaction.transcript": "bg-sky-50 text-sky-600 border-sky-100",
  "interaction.sentiment_shift": "bg-violet-50 text-violet-600 border-violet-100",
  "interaction.ended": "bg-slate-50 text-slate-600 border-slate-100",
  "ai.sentiment_analysis": "bg-purple-50 text-purple-600 border-purple-100",
  "ai.theme_classification": "bg-purple-50 text-purple-600 border-purple-100",
  "ai.root_cause_identified": "bg-indigo-50 text-indigo-600 border-indigo-100",
  "ai.recommendation_generated": "bg-indigo-50 text-indigo-600 border-indigo-100",
  "ai.override_requested": "bg-amber-50 text-amber-600 border-amber-100",
  "ai.escalation_triggered": "bg-red-50 text-red-600 border-red-100",
  "workflow.created": "bg-cyan-50 text-cyan-600 border-cyan-100",
  "notification.sent": "bg-emerald-50 text-emerald-600 border-emerald-100",
  "dashboard.update": "bg-slate-50 text-slate-600 border-slate-100",
  "simulation.complete": "bg-emerald-50 text-emerald-600 border-emerald-100",
};

function formatEventType(type: string): string {
  return type
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function EventCard({ event }: { event: DemoEvent }) {
  const Icon = EVENT_ICONS[event.event_type] ?? Brain;
  const colorClass = EVENT_COLORS[event.event_type] ?? "bg-slate-50 text-slate-600 border-slate-100";
  const summary = event.data?.summary as string | undefined;

  return (
    <div className="flex gap-3 group">
      <div className="relative flex flex-col items-center">
        <div className={cn("flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border", colorClass)}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
      <div className="flex-1 min-w-0 pb-5">
        <div className="flex items-center justify-between">
          <p className="text-xs font-semibold text-[#0F172A]">
            {formatEventType(event.event_type)}
          </p>
          <span className="text-[10px] text-[#94A3B8] shrink-0 ml-2">
            {new Date(event.timestamp).toLocaleTimeString("en-US", {
              hour: "2-digit",
              minute: "2-digit",
              second: "2-digit",
            })}
          </span>
        </div>
        {summary && (
          <p className="mt-0.5 text-[11px] text-[#64748B] leading-relaxed line-clamp-2">
            {summary}
          </p>
        )}
        {event.customer_name && (
          <p className="mt-0.5 text-[10px] font-medium text-[#2563EB]">
            {event.customer_name}
          </p>
        )}
      </div>
    </div>
  );
}

export function DemoTimeline() {
  const enabled = useDemoStore((s) => s.enabled);
  const events = useDemoStore((s) => s.events);

  if (!enabled) return null;

  const reversed = [...events].reverse();

  return (
    <div className="rounded-xl border border-[#E2E8F0] bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-[#E2E8F0] px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-emerald-500 shadow-sm shadow-emerald-400" />
          <p className="text-sm font-bold text-[#0F172A]">Live Demo Timeline</p>
        </div>
        <span className="text-[10px] font-medium text-[#94A3B8]">
          {events.length} events
        </span>
      </div>
      <div className="max-h-[400px] overflow-y-auto p-4">
        {reversed.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <Brain className="mb-2 h-8 w-8 text-[#CBD5E1]" />
            <p className="text-xs font-medium text-[#94A3B8]">
              No demo events yet
            </p>
            <p className="mt-1 text-[10px] text-[#CBD5E1]">
              Run a simulation scenario to see live events
            </p>
          </div>
        ) : (
          <div className="space-y-0">
            {reversed.slice(0, 50).map((event) => (
              <div key={event.id} className="relative">
                {event !== reversed[0] && (
                  <div className="absolute left-[15px] top-0 h-full w-px bg-[#E2E8F0]" />
                )}
                <EventCard event={event} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

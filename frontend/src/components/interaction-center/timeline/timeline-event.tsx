"use client";

import {
  Bell,
  CheckCircle2,
  FileWarning,
  Info,
  PhoneCall,
  PhoneOff,
  Settings2,
  ShieldAlert,
  UserCheck,
  Workflow,
  type LucideIcon,
} from "lucide-react";

import { formatDate } from "@/lib/formatters";
import { formatEnum } from "@/lib/formatters";
import type { TimelineItem } from "@/features/conversations/types";

const PREFIX_CONFIG: { prefix: string; icon: LucideIcon; tone: string }[] = [
  { prefix: "complaint.escalated", icon: ShieldAlert, tone: "text-destructive" },
  { prefix: "complaint.resolved", icon: CheckCircle2, tone: "text-success" },
  { prefix: "complaint.closed", icon: CheckCircle2, tone: "text-success" },
  { prefix: "complaint.assigned", icon: UserCheck, tone: "text-primary" },
  { prefix: "complaint.intelligence_result", icon: Info, tone: "text-primary" },
  { prefix: "complaint", icon: FileWarning, tone: "text-warning" },
  { prefix: "workflow", icon: Workflow, tone: "text-primary" },
  { prefix: "notification", icon: Bell, tone: "text-muted-foreground" },
  { prefix: "voice.session_started", icon: PhoneCall, tone: "text-success" },
  { prefix: "voice.session_ended", icon: PhoneOff, tone: "text-muted-foreground" },
];

function iconFor(eventType: string): { icon: LucideIcon; tone: string } {
  const match = PREFIX_CONFIG.find((c) => eventType.startsWith(c.prefix));
  return match ?? { icon: Settings2, tone: "text-muted-foreground" };
}

function summarize(item: TimelineItem): string | null {
  const payload = item.payload as Record<string, unknown> | null;
  if (!payload) return null;
  if (item.event_type === "voice.session_ended" && typeof payload.duration_seconds === "number") {
    const mins = Math.floor(payload.duration_seconds / 60);
    const secs = Math.round(payload.duration_seconds % 60);
    return `Call duration: ${mins}m ${secs}s`;
  }
  if (typeof payload.complaint_number === "string") return `Complaint ${payload.complaint_number}`;
  if (typeof payload.reason === "string" && payload.reason) return payload.reason;
  if (typeof payload.queue === "string") return `Queue: ${payload.queue}`;
  return null;
}

/** Complaint / workflow / notification / voice-session / system events all
 * render through this one compact row (Zendesk/Genesys-style), interleaved
 * chronologically with messages — never a separate "events" panel. */
export function TimelineEvent({ item }: { item: TimelineItem }) {
  if (!item.event_type) return null;
  const { icon: Icon, tone } = iconFor(item.event_type);
  const detail = summarize(item);

  return (
    <div className="flex items-center gap-2 py-1 pl-9 text-xs text-muted-foreground">
      <Icon className={`h-3.5 w-3.5 shrink-0 ${tone}`} />
      <span className="font-medium text-foreground">{formatEnum(item.event_type)}</span>
      {detail ? <span>· {detail}</span> : null}
      <span className="ml-auto shrink-0">{formatDate(item.timestamp, "p")}</span>
    </div>
  );
}

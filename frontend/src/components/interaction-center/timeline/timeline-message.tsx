"use client";

import { Bot, Eye, Lock, Phone, User } from "lucide-react";

import { cn } from "@/lib/cn";
import { formatDate } from "@/lib/formatters";
import { channelLabel } from "@/components/interaction-center/shared/conversation-badges";
import type { TimelineItem } from "@/features/conversations/types";

const SENDER_ICON = {
  customer: User,
  ai: Bot,
  employee: User,
  supervisor: Eye,
  system: Bot,
} as const;

const SENDER_LABEL: Record<string, string> = {
  customer: "Customer",
  ai: "AI Assistant",
  employee: "Agent",
  supervisor: "Supervisor",
  system: "System",
};

/** Every message — web chat, WhatsApp, email, or a voice transcript segment
 * — renders through this ONE component. Voice is distinguished only by a
 * small "Voice" badge, never a separate panel (per "never separate voice
 * from chat, one unified timeline"). */
export function TimelineMessage({ item }: { item: TimelineItem }) {
  if (!item.sender_type) return null;
  const isCustomer = item.sender_type === "customer";
  const meta = item.payload as { internal?: boolean; deleted?: boolean } | null;
  const isInternalNote = Boolean(meta?.internal);
  const isDeleted = Boolean(meta?.deleted);
  const Icon = SENDER_ICON[item.sender_type] ?? User;

  return (
    <div className={cn("flex gap-2.5", isCustomer ? "flex-row" : "flex-row-reverse")}>
      <div
        className={cn(
          "flex h-7 w-7 shrink-0 items-center justify-center rounded-full",
          isCustomer ? "bg-muted text-muted-foreground" : "bg-primary/10 text-primary",
        )}
      >
        <Icon className="h-3.5 w-3.5" />
      </div>
      <div className={cn("max-w-[70%]", isCustomer ? "items-start" : "items-end", "flex flex-col")}>
        <div className="mb-0.5 flex items-center gap-1.5 text-[11px] text-muted-foreground">
          <span className="font-medium">{SENDER_LABEL[item.sender_type] ?? item.sender_type}</span>
          {item.channel === "voice" ? (
            <span className="inline-flex items-center gap-0.5 rounded bg-muted px-1 py-0.5">
              <Phone className="h-2.5 w-2.5" /> Voice
            </span>
          ) : item.channel ? (
            <span className="rounded bg-muted px-1 py-0.5">{channelLabel(item.channel)}</span>
          ) : null}
          {isInternalNote ? (
            <span className="inline-flex items-center gap-0.5 rounded bg-warning/10 px-1 py-0.5 text-warning">
              <Lock className="h-2.5 w-2.5" /> Internal note
            </span>
          ) : null}
          <span>{formatDate(item.timestamp, "p")}</span>
        </div>
        <div
          className={cn(
            "rounded-lg px-3 py-2 text-sm",
            isDeleted
              ? "border border-dashed border-border bg-muted/40 italic text-muted-foreground"
              : isInternalNote
                ? "border border-warning/30 bg-warning/10"
                : isCustomer
                  ? "bg-muted"
                  : "bg-primary text-primary-foreground",
          )}
        >
          {isDeleted ? "This internal note was deleted." : item.content}
        </div>
      </div>
    </div>
  );
}

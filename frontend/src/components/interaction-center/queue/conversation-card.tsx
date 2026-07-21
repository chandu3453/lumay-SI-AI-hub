"use client";

import { AlertOctagon } from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { cn } from "@/lib/cn";
import { formatRelative } from "@/lib/formatters";
import {
  ChannelBadge,
  HandlingIndicator,
  LiveIndicator,
  PriorityBadge,
  StatusBadge,
} from "@/components/interaction-center/shared/conversation-badges";
import type { ConversationSummary } from "@/features/conversations/types";

function initials(name: string | null, id: string): string {
  if (name) {
    const parts = name.trim().split(/\s+/);
    return parts
      .slice(0, 2)
      .map((p) => p[0])
      .join("")
      .toUpperCase();
  }
  return id.slice(0, 2).toUpperCase();
}

export function ConversationCard({
  conversation,
  isSelected,
  onSelect,
}: {
  conversation: ConversationSummary;
  isSelected: boolean;
  onSelect: () => void;
}) {
  const displayName =
    conversation.customer_name ??
    (conversation.customer_id ? `Customer ${conversation.customer_id.slice(0, 8)}` : "Anonymous customer");

  return (
    <button
      type="button"
      onClick={onSelect}
      aria-pressed={isSelected}
      className={cn(
        "w-full border-b border-border p-3 text-left transition-colors hover:bg-accent/50",
        isSelected && "bg-accent",
      )}
    >
      <div className="flex items-start gap-2.5">
        <Avatar className="h-9 w-9 shrink-0">
          <AvatarFallback className="text-xs font-medium">
            {initials(conversation.customer_name, conversation.id)}
          </AvatarFallback>
        </Avatar>
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-2">
            <span className="truncate text-sm font-medium">{displayName}</span>
            <LiveIndicator status={conversation.current_status} />
          </div>
          <div className="mt-0.5 flex items-center gap-1.5 text-[11px] text-muted-foreground">
            <span className="font-mono">{conversation.id.slice(0, 8)}</span>
            {conversation.complaint_id ? (
              <span className="inline-flex items-center gap-0.5 text-destructive">
                <AlertOctagon className="h-3 w-3" /> Complaint
              </span>
            ) : null}
          </div>
          {conversation.last_message_preview ? (
            <p className="mt-1 truncate text-xs text-muted-foreground">
              {conversation.last_message_preview}
            </p>
          ) : null}
          <div className="mt-2 flex flex-wrap items-center gap-1.5">
            <ChannelBadge channel={conversation.current_channel} />
            <StatusBadge status={conversation.current_status} />
            <PriorityBadge priority={conversation.priority} />
            <HandlingIndicator status={conversation.current_status} />
          </div>
          <div className="mt-1.5 flex items-center justify-between text-[11px] text-muted-foreground">
            <span>
              {conversation.assigned_employee_id
                ? `Assigned: ${conversation.assigned_employee_id.slice(0, 8)}`
                : "Unassigned"}
            </span>
            <span>{formatRelative(conversation.updated_at)}</span>
          </div>
        </div>
      </div>
    </button>
  );
}

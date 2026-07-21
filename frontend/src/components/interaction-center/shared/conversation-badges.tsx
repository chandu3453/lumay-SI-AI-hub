"use client";

import { Mail, MessageCircle, MessageSquare, Phone, ShieldAlert } from "lucide-react";
import type { LucideIcon } from "lucide-react";

import { Badge, type BadgeProps } from "@/components/ui/badge";
import type {
  ConversationChannel,
  ConversationPriority,
  ConversationStatus,
} from "@/features/conversations/types";

const CHANNEL_ICONS: Record<ConversationChannel, LucideIcon> = {
  web_chat: MessageSquare,
  voice: Phone,
  whatsapp: MessageCircle,
  email: Mail,
  complaint: ShieldAlert,
};

const CHANNEL_LABELS: Record<ConversationChannel, string> = {
  web_chat: "Web Chat",
  voice: "Voice",
  whatsapp: "WhatsApp",
  email: "Email",
  complaint: "Complaint",
};

export function ChannelIcon({ channel, className }: { channel: ConversationChannel; className?: string }) {
  const Icon = CHANNEL_ICONS[channel] ?? MessageSquare;
  return <Icon className={className} />;
}

export function channelLabel(channel: ConversationChannel): string {
  return CHANNEL_LABELS[channel] ?? channel;
}

export function ChannelBadge({ channel }: { channel: ConversationChannel }) {
  return (
    <Badge variant="outline" className="gap-1">
      <ChannelIcon channel={channel} className="h-3 w-3" />
      {channelLabel(channel)}
    </Badge>
  );
}

const STATUS_VARIANT: Record<ConversationStatus, BadgeProps["variant"]> = {
  new: "neutral",
  active: "default",
  waiting_for_customer: "secondary",
  waiting_for_agent: "warning",
  ai_handling: "default",
  human_handling: "success",
  escalated: "destructive",
  resolved: "success",
  closed: "neutral",
};

export const STATUS_LABELS: Record<ConversationStatus, string> = {
  new: "New",
  active: "Active",
  waiting_for_customer: "Waiting for Customer",
  waiting_for_agent: "Waiting for Agent",
  ai_handling: "AI Handling",
  human_handling: "Human Handling",
  escalated: "Escalated",
  resolved: "Resolved",
  closed: "Closed",
};

export function StatusBadge({ status }: { status: ConversationStatus }) {
  return <Badge variant={STATUS_VARIANT[status] ?? "neutral"}>{STATUS_LABELS[status] ?? status}</Badge>;
}

const PRIORITY_VARIANT: Record<ConversationPriority, BadgeProps["variant"]> = {
  low: "outline",
  medium: "secondary",
  high: "warning",
  critical: "destructive",
};

export function PriorityBadge({ priority }: { priority: ConversationPriority }) {
  return (
    <Badge variant={PRIORITY_VARIANT[priority] ?? "outline"} className="uppercase tracking-wide">
      {priority}
    </Badge>
  );
}

/** AI/Human handling indicator — derived from status alone, no extra fetch. */
export function HandlingIndicator({ status }: { status: ConversationStatus }) {
  if (status === "ai_handling") {
    return <Badge variant="default">AI</Badge>;
  }
  if (status === "human_handling") {
    return <Badge variant="success">Human</Badge>;
  }
  return null;
}

/** Live indicator — a plain solid dot, no animation (per the "no unnecessary
 * animations" design requirement). */
export function LiveIndicator({ status }: { status: ConversationStatus }) {
  const isLive =
    status === "active" ||
    status === "ai_handling" ||
    status === "human_handling" ||
    status === "waiting_for_agent";
  if (!isLive) return null;
  return <span className="inline-block h-2 w-2 shrink-0 rounded-full bg-success" title="Live" />;
}

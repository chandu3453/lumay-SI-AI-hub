"use client";

import {
  Phone, MessageCircle, Globe, Mail, Radio,
  ClipboardList, BookUser, Star, FileCheck2,
} from "lucide-react";
import { cn } from "@/lib/cn";
import type { ChannelId, WorkspaceInteraction } from "@/features/interactions/types";

export const CHANNEL_DEFS = [
  { id: "all" as ChannelId, label: "All", icon: null, color: "#64748B" },
  { id: "web_chat" as ChannelId, label: "Web Chat", icon: Globe, color: "#8B5CF6" },
  { id: "voice" as ChannelId, label: "Voice Calls", icon: Phone, color: "#0052FF" },
  { id: "whatsapp" as ChannelId, label: "WhatsApp", icon: MessageCircle, color: "#25D366" },
  { id: "email" as ChannelId, label: "Email", icon: Mail, color: "#3B82F6" },
];

export function getChannelIcon(
  channelId: string,
  className = "h-4 w-4",
): React.ReactNode {
  const def = CHANNEL_DEFS.find(c => c.id === channelId);
  if (!def || !def.icon) return null;
  const Icon = def.icon;
  return <Icon className={className} style={{ color: def.color }} />;
}

export function getChannelColor(channelId: string): string {
  return CHANNEL_DEFS.find(c => c.id === channelId)?.color ?? "#64748B";
}

interface ChannelTabsProps {
  activeChannel: ChannelId;
  onChange: (channel: ChannelId) => void;
  interactions: WorkspaceInteraction[];
}

export function ChannelTabs({ activeChannel, onChange, interactions }: ChannelTabsProps) {
  // Count per channel
  const counts: Record<string, number> = { all: 0 };
  for (const item of interactions) {
    let ch: string = item.channel;
    if (ch === "smart_call") ch = "voice";
    if (ch === "web_form") ch = "web_chat";
    
    if (["voice", "web_chat", "whatsapp", "email"].includes(ch)) {
      counts[ch] = (counts[ch] ?? 0) + 1;
      counts["all"] = (counts["all"] ?? 0) + 1;
    }
  }

  // Count high risk
  const highRiskCount = interactions.filter(i => i.status === "high_risk").length;
  const unreadTotal = interactions.reduce((sum, i) => sum + i.unreadCount, 0);

  return (
    <div className="flex shrink-0 flex-col bg-white border-b border-[#E2E8F0]">
      {/* Alert bar */}
      {(highRiskCount > 0 || unreadTotal > 0) && (
        <div className="flex items-center gap-3 px-5 py-1.5 bg-[#FFFBEB] border-b border-[#FDE68A] text-xs">
          {highRiskCount > 0 && (
            <span className="flex items-center gap-1 font-bold text-[#B45309]">
              <span className="h-1.5 w-1.5 rounded-full bg-[#EF4444] animate-pulse inline-block" />
              {highRiskCount} High Risk
            </span>
          )}
          {unreadTotal > 0 && (
            <span className="font-medium text-[#92400E]">{unreadTotal} unread messages</span>
          )}
          <span className="ml-auto text-[#92400E] font-medium">
            {interactions.length} total interactions
          </span>
        </div>
      )}

      {/* Channel tab strip */}
      <div className="flex items-end gap-0 overflow-x-auto px-4 scrollbar-none">
        {CHANNEL_DEFS.map(ch => {
          const count = counts[ch.id] ?? 0;
          const isActive = activeChannel === ch.id;
          const Icon = ch.icon;
          return (
            <button
              key={ch.id}
              onClick={() => onChange(ch.id)}
              className={cn(
                "flex items-center gap-1.5 px-4 py-3 text-[11px] font-bold whitespace-nowrap transition-all border-b-2 relative shrink-0",
                isActive
                  ? "border-[#0052FF] text-[#0052FF]"
                  : "border-transparent text-slate-500 hover:text-[#0F172A] hover:bg-slate-50/50"
              )}
              style={isActive ? { borderColor: ch.color, color: ch.color } : {}}
            >
              {Icon && (
                <Icon
                  className="h-3.5 w-3.5 shrink-0"
                  style={{ color: isActive ? ch.color : undefined }}
                />
              )}
              <span>{ch.label}</span>
              {count > 0 && (
                <span
                  className={cn(
                    "text-[9px] px-1.5 py-0.5 rounded-full font-bold",
                    isActive
                      ? "text-white"
                      : "bg-slate-100 text-slate-500"
                  )}
                  style={isActive ? { backgroundColor: ch.color } : {}}
                >
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

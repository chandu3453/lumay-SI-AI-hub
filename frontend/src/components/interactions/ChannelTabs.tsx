"use client";

import { Phone, Bot, MessageSquare, MessageCircle, Mail, Database, FileText } from "lucide-react";
import { cn } from "@/lib/cn";

export type ChannelTabId = "all" | "voice" | "smart_call" | "whatsapp" | "web_chat" | "email" | "crm" | "manual";

type ChannelTab = {
  id: ChannelTabId;
  name: string;
  icon: React.ReactNode;
  activeColor: string;
};

const CHANNELS: ChannelTab[] = [
  { id: "voice", name: "Voice Calls", icon: <Phone className="h-4 w-4" />, activeColor: "text-[#10B981]" },
  { id: "smart_call", name: "SMART CALL", icon: <Bot className="h-4 w-4" />, activeColor: "text-[#0052FF]" },
  { id: "whatsapp", name: "WhatsApp", icon: <MessageSquare className="h-4 w-4" />, activeColor: "text-[#10B981]" },
  { id: "web_chat", name: "Web Chat", icon: <MessageCircle className="h-4 w-4" />, activeColor: "text-[#8B5CF6]" },
  { id: "email", name: "Email", icon: <Mail className="h-4 w-4" />, activeColor: "text-[#2563EB]" },
  { id: "crm", name: "CRM Records", icon: <Database className="h-4 w-4" />, activeColor: "text-[#6366F1]" },
  { id: "manual", name: "Manual", icon: <FileText className="h-4 w-4" />, activeColor: "text-[#64748B]" },
];

type ChannelTabsProps = {
  activeTab: ChannelTabId;
  onTabChange: (tab: ChannelTabId) => void;
  counts: Record<string, number>;
};

export function ChannelTabs({ activeTab, onTabChange, counts }: ChannelTabsProps) {
  // Use mockup counts if dynamic counts are not loaded
  const getCount = (id: string) => {
    if (counts[id] !== undefined) return counts[id];
    switch (id) {
      case "voice": return 24;
      case "smart_call": return 18;
      case "whatsapp": return 36;
      case "web_chat": return 22;
      case "email": return 16;
      case "crm": return 8;
      case "manual": return 4;
      default: return 0;
    }
  };

  return (
    <div className="flex items-center gap-1 bg-white border border-[#E2E8F0] rounded-2xl p-1.5 overflow-x-auto w-full">
      {CHANNELS.map((channel) => {
        const isActive = activeTab === channel.id;
        return (
          <button
            key={channel.id}
            onClick={() => onTabChange(channel.id)}
            className={cn(
              "flex items-center gap-2.5 px-4 py-3 rounded-xl text-xs font-bold transition-all relative whitespace-nowrap",
              isActive
                ? "bg-[#EFF6FF] text-[#0052FF]"
                : "text-[#64748B] hover:text-[#0F172A] hover:bg-[#F8FAFC]"
            )}
          >
            <span className={cn("shrink-0", isActive ? channel.activeColor : "text-[#94A3B8]")}>
              {channel.icon}
            </span>
            <span>{channel.name}</span>
            <span
              className={cn(
                "rounded-md px-1.5 py-0.5 text-[10px] font-bold shrink-0",
                isActive ? "bg-white text-[#0052FF]" : "bg-slate-100 text-slate-500"
              )}
            >
              {getCount(channel.id)}
            </span>
          </button>
        );
      })}
    </div>
  );
}

export { CHANNELS };
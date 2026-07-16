"use client";

import { useState, useMemo } from "react";
import { Search, SlidersHorizontal } from "lucide-react";
import { cn } from "@/lib/cn";
import type { WorkspaceInteraction, ChannelId } from "@/features/interactions/types";
import { getChannelIcon } from "./channel-tabs";

const STATUS_CONFIG = {
  high_risk: { label: "High Risk", cls: "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20" },
  new: { label: "New", cls: "bg-[#0052FF]/10 text-[#0052FF] border-[#0052FF]/20" },
  in_progress: { label: "In Progress", cls: "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20" },
  processed: { label: "Processed", cls: "bg-[#10B981]/10 text-[#10B981] border-[#10B981]/20" },
  closed: { label: "Closed", cls: "bg-slate-100 text-slate-500 border-slate-200" },
  active: { label: "Active", cls: "bg-[#0052FF]/10 text-[#0052FF] border-[#0052FF]/20" },
  pending: { label: "Pending", cls: "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20" },
} as const;

const SENTIMENT_DOT: Record<string, string> = {
  very_positive: "bg-[#10B981]",
  positive: "bg-[#34D399]",
  neutral: "bg-slate-300",
  negative: "bg-[#F59E0B]",
  very_negative: "bg-[#EF4444]",
  extremely_negative: "bg-[#7F1D1D]",
};

interface ConversationListProps {
  interactions: WorkspaceInteraction[];
  activeChannel: ChannelId;
  selectedId: string;
  onSelect: (id: string) => void;
}

export function ConversationList({
  interactions,
  activeChannel,
  selectedId,
  onSelect,
}: ConversationListProps) {
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<"time" | "priority">("time");

  const filtered = useMemo(() => {
    let list = interactions;
    // Channel filter
    if (activeChannel !== "all") {
      list = list.filter(i => {
        let ch: string = i.channel;
        if (ch === "smart_call") ch = "voice";
        if (ch === "web_form") ch = "web_chat";
        return ch === activeChannel;
      });
    }
    // Search
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        i =>
          i.customer.name.toLowerCase().includes(q) ||
          i.subject.toLowerCase().includes(q) ||
          i.customer.policyNumber.toLowerCase().includes(q) ||
          i.customer.phone.toLowerCase().includes(q)
      );
    }
    // Sort
    if (sortBy === "priority") {
      const pOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      list = [...list].sort((a, b) => (pOrder[a.priority] ?? 3) - (pOrder[b.priority] ?? 3));
    } else {
      list = [...list].sort((a, b) => b.timestamp - a.timestamp);
    }
    return list;
  }, [interactions, activeChannel, search, sortBy]);

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="p-3 border-b border-[#E2E8F0] space-y-2.5 shrink-0">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-bold text-[#64748B]">
            {filtered.length} conversation{filtered.length !== 1 ? "s" : ""}
          </span>
          <div className="flex items-center gap-1">
            <span className="text-[10px] text-slate-400">Sort:</span>
            <select
              value={sortBy}
              onChange={e => setSortBy(e.target.value as "time" | "priority")}
              className="text-[10px] font-bold text-[#0F172A] bg-transparent focus:outline-none cursor-pointer"
            >
              <option value="time">Latest</option>
              <option value="priority">Priority</option>
            </select>
            <SlidersHorizontal className="h-3 w-3 text-slate-400 ml-1" />
          </div>
        </div>
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search by name, policy, phone..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-8 pr-3 py-2 text-[11px] focus:outline-none focus:ring-2 focus:ring-[#0052FF]/20 focus:bg-white transition-all"
          />
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto divide-y divide-slate-50">
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <div className="h-10 w-10 rounded-full bg-slate-100 flex items-center justify-center mb-3">
              <Search className="h-5 w-5 text-slate-300" />
            </div>
            <p className="text-xs font-semibold text-slate-400">No conversations found</p>
            <p className="text-[10px] text-slate-300 mt-1">Try adjusting your search or filter</p>
          </div>
        ) : (
          filtered.map(item => {
            const isSelected = item.id === selectedId;
            const statusConf = STATUS_CONFIG[item.status] ?? STATUS_CONFIG.new;
            const sentimentDot = SENTIMENT_DOT[item.ai.sentiment] ?? "bg-slate-300";
            const isHighRisk = item.status === "high_risk";
            const hasUnread = item.unreadCount > 0;

            return (
              <button
                key={item.id}
                onClick={() => onSelect(item.id)}
                className={cn(
                  "w-full text-left p-3.5 transition-all hover:bg-slate-50/80 flex gap-2.5 relative group",
                  isSelected ? "bg-[#EFF6FF] border-l-[3px] border-l-[#0052FF]" : "border-l-[3px] border-l-transparent",
                  isHighRisk && !isSelected && "bg-[#FEF2F2]/30"
                )}
              >
                {/* Avatar */}
                <div className="relative shrink-0">
                  <div
                    className={cn(
                      "h-9 w-9 rounded-full flex items-center justify-center text-xs font-extrabold ring-2 ring-offset-1",
                      isHighRisk ? "ring-[#EF4444]/30" : isSelected ? "ring-[#0052FF]/20" : "ring-slate-100"
                    )}
                    style={{
                      background: isHighRisk
                        ? "linear-gradient(135deg, #FEE2E2, #FECACA)"
                        : isSelected
                        ? "linear-gradient(135deg, #EFF6FF, #DBEAFE)"
                        : "linear-gradient(135deg, #F1F5F9, #E2E8F0)",
                      color: isHighRisk ? "#EF4444" : isSelected ? "#0052FF" : "#64748B",
                    }}
                  >
                    {item.customer.name.charAt(0)}
                  </div>
                  {/* Channel icon badge */}
                  <div className="absolute -bottom-0.5 -right-0.5 h-4 w-4 rounded-full bg-white border border-slate-200 flex items-center justify-center">
                    {getChannelIcon(item.channel, "h-2.5 w-2.5")}
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0 space-y-1">
                  <div className="flex items-start justify-between gap-1">
                    <div className="flex items-center gap-1.5 min-w-0">
                      <span className={cn(
                        "text-xs font-bold truncate",
                        hasUnread ? "text-[#0F172A]" : "text-[#334155]"
                      )}>
                        {item.customer.name}
                      </span>
                      {/* Sentiment dot */}
                      <span className={cn("h-1.5 w-1.5 rounded-full shrink-0", sentimentDot)} />
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      <span className="text-[9px] text-slate-400 font-medium">{item.time}</span>
                      {hasUnread && (
                        <span className="h-4 min-w-4 px-1 rounded-full bg-[#0052FF] text-white text-[8px] font-extrabold flex items-center justify-center">
                          {item.unreadCount}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Policy + product */}
                  <div className="text-[9px] text-slate-400 font-mono truncate">
                    {item.customer.policyNumber} · {item.customer.product}
                  </div>

                  {/* Last message */}
                  <p className="text-[10px] text-slate-500 truncate leading-normal">
                    {item.lastMessage}
                  </p>

                  {/* Badges row */}
                  <div className="flex items-center gap-1 flex-wrap">
                    <span className={cn(
                      "text-[8px] px-1.5 py-0.5 rounded border font-bold shrink-0",
                      statusConf.cls
                    )}>
                      {statusConf.label}
                    </span>
                    {item.ai.complaintDetected && (
                      <span className="text-[8px] px-1.5 py-0.5 rounded border font-bold bg-[#7C3AED]/10 text-[#7C3AED] border-[#7C3AED]/20 shrink-0">
                        ⚠ Complaint
                      </span>
                    )}
                    {item.ai.repeatComplaint && (
                      <span className="text-[8px] px-1.5 py-0.5 rounded border font-bold bg-orange-50 text-orange-600 border-orange-200 shrink-0">
                        ↺ Repeat
                      </span>
                    )}
                    {item.priority === "critical" && (
                      <span className="text-[8px] px-1.5 py-0.5 rounded border font-bold bg-red-50 text-red-600 border-red-200 animate-pulse shrink-0">
                        🔴 Critical
                      </span>
                    )}
                  </div>
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}

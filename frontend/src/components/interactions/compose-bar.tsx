"use client";

import { useState } from "react";
import {
  Send, Paperclip, Smile, Phone, AlertTriangle,
  Plus, UserCog, Mic, RefreshCw,
} from "lucide-react";
import { cn } from "@/lib/cn";

interface ComposeBarProps {
  channel: string;
  onSend: (text: string, type?: "reply" | "note") => void;
  onEscalate?: () => void;
  onCreateComplaint?: () => void;
  onTransfer?: () => void;
  isCreatingComplaint?: boolean;
  disabled?: boolean;
}

const COMPOSE_TABS = [
  { id: "reply", label: "Reply" },
  { id: "note", label: "Internal Note" },
];

export function ComposeBar({
  channel,
  onSend,
  onEscalate,
  onCreateComplaint,
  onTransfer,
  isCreatingComplaint,
  disabled,
}: ComposeBarProps) {
  const [activeTab, setActiveTab] = useState<"reply" | "note">("reply");
  const [value, setValue] = useState("");

  function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!value.trim()) return;
    onSend(value, activeTab);
    setValue("");
  }

  const placeholder =
    activeTab === "note"
      ? "Add an internal note (not visible to customer)..."
      : channel === "whatsapp"
      ? "Type a WhatsApp message..."
      : channel === "email"
      ? "Type your email reply..."
      : "Type your reply...";

  const isNote = activeTab === "note";

  return (
    <div className="border-t border-[#E2E8F0] bg-white shrink-0">
      {/* Compose tabs */}
      <div className="flex items-center gap-1 px-4 pt-3 pb-2 border-b border-slate-50">
        {COMPOSE_TABS.map(tab => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id as "reply" | "note")}
            className={cn(
              "px-3 py-1.5 rounded-lg text-xs font-bold transition-all",
              activeTab === tab.id
                ? tab.id === "note"
                  ? "bg-amber-50 text-amber-700 border border-amber-200"
                  : "bg-[#EFF6FF] text-[#0052FF] border border-[#BFDBFE]/50"
                : "text-slate-400 hover:text-slate-700 hover:bg-slate-50"
            )}
          >
            {tab.label}
          </button>
        ))}

        {/* Channel action buttons on right */}
        <div className="ml-auto flex items-center gap-1.5">
          {onCreateComplaint && (
            <button
              type="button"
              onClick={onCreateComplaint}
              disabled={isCreatingComplaint}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-[#EF4444]/10 hover:bg-[#EF4444]/20 text-[#EF4444] rounded-lg text-[10px] font-bold transition-all disabled:opacity-50"
            >
              {isCreatingComplaint
                ? <><RefreshCw className="h-3 w-3 animate-spin" />Creating...</>
                : <><Plus className="h-3 w-3" />Complaint</>
              }
            </button>
          )}
          {onEscalate && (
            <button
              type="button"
              onClick={onEscalate}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-[#F59E0B]/10 hover:bg-[#F59E0B]/20 text-[#F59E0B] rounded-lg text-[10px] font-bold transition-all"
            >
              <AlertTriangle className="h-3 w-3" />Escalate
            </button>
          )}
          {onTransfer && (
            <button
              type="button"
              onClick={onTransfer}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg text-[10px] font-bold transition-all"
            >
              <UserCog className="h-3 w-3" />Transfer
            </button>
          )}
        </div>
      </div>

      {/* Input row */}
      <form onSubmit={handleSend} className="p-3">
        {isNote && (
          <div className="mb-2 text-[10px] font-medium text-amber-600 bg-amber-50 px-3 py-1.5 rounded-lg border border-amber-100">
            Internal note — not visible to customer
          </div>
        )}
        <div className="flex items-center gap-2">
          <button type="button" className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-400 transition-colors shrink-0">
            <Paperclip className="h-4 w-4" />
          </button>
          <button type="button" className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-400 transition-colors shrink-0">
            <Mic className="h-4 w-4" />
          </button>
          <textarea
            rows={1}
            placeholder={placeholder}
            value={value}
            onChange={e => setValue(e.target.value)}
            onKeyDown={e => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend(e as unknown as React.FormEvent);
              }
            }}
            disabled={disabled}
            className={cn(
              "flex-1 resize-none bg-slate-50 border rounded-xl px-4 py-2.5 text-xs focus:outline-none focus:ring-2 focus:bg-white transition-all leading-relaxed min-h-[38px] max-h-[120px]",
              isNote
                ? "border-amber-200 focus:ring-amber-200/40 focus:border-amber-300 bg-amber-50/30"
                : "border-slate-200 focus:ring-[#0052FF]/20 focus:border-[#0052FF]/40"
            )}
          />
          <button type="button" className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-400 transition-colors shrink-0">
            <Smile className="h-4 w-4" />
          </button>
          {channel === "voice" && (
            <button type="button" className="p-2 bg-[#10B981]/10 hover:bg-[#10B981]/20 rounded-lg text-[#10B981] transition-colors shrink-0">
              <Phone className="h-4 w-4" />
            </button>
          )}
          <button
            type="submit"
            disabled={!value.trim() || disabled}
            className={cn(
              "p-2.5 rounded-xl shrink-0 transition-all shadow-sm",
              isNote
                ? "bg-amber-500 hover:bg-amber-600 text-white disabled:opacity-50"
                : "bg-[#0052FF] hover:bg-[#0040CC] text-white disabled:opacity-50"
            )}
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
        <p className="text-[9px] text-slate-300 mt-1.5 pl-1">Press Enter to send · Shift+Enter for new line</p>
      </form>
    </div>
  );
}

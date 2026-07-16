"use client";

import { Mail, Paperclip, CornerUpLeft, Forward, Bot } from "lucide-react";
import { cn } from "@/lib/cn";
import type { WorkspaceInteraction } from "@/features/interactions/types";

interface EmailWorkspaceProps {
  interaction: WorkspaceInteraction;
  onSend: (text: string) => void;
  inputValue: string;
  onInputChange: (val: string) => void;
}

export function EmailWorkspace({ interaction, onSend, inputValue, onInputChange }: EmailWorkspaceProps) {
  const emailMessages = interaction.messages.filter(m => m.type === "email" || m.sender === "agent");
  const attachments = interaction.emailAttachments ?? [];

  function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!inputValue.trim()) return;
    onSend(inputValue);
  }

  return (
    <div className="flex flex-col h-full">
      {/* Email thread header */}
      <div className="px-5 py-4 border-b border-[#E2E8F0] bg-white shrink-0">
        <div className="flex items-start gap-3">
          <div className="h-9 w-9 rounded-xl bg-[#3B82F6]/10 flex items-center justify-center shrink-0">
            <Mail className="h-4.5 w-4.5 text-[#3B82F6]" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-extrabold text-[#0F172A] truncate">
              {interaction.emailSubject ?? interaction.subject}
            </h4>
            <div className="mt-1 space-y-0.5 text-[10px] text-slate-500">
              <p><span className="text-slate-400 font-medium">From:</span> {interaction.emailFrom ?? interaction.customer.email}</p>
              <p><span className="text-slate-400 font-medium">To:</span> {(interaction.emailRecipients ?? ["complaints@lumay.om"]).join(", ")}</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 shrink-0">
            <button className="flex items-center gap-1.5 px-3 py-1.5 border border-slate-200 rounded-xl text-[10px] font-bold text-slate-600 hover:bg-slate-50 transition-all">
              <CornerUpLeft className="h-3 w-3" />Reply
            </button>
            <button className="flex items-center gap-1.5 px-3 py-1.5 border border-slate-200 rounded-xl text-[10px] font-bold text-slate-600 hover:bg-slate-50 transition-all">
              <Forward className="h-3 w-3" />Forward
            </button>
          </div>
        </div>

        {/* Attachments */}
        {attachments.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {attachments.map((a, i) => (
              <div key={i} className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl cursor-pointer hover:bg-[#EFF6FF] hover:border-[#BFDBFE] transition-all">
                <Paperclip className="h-3 w-3 text-[#3B82F6]" />
                <span className="text-[10px] font-medium text-[#0F172A]">{a.name}</span>
                <span className="text-[9px] text-slate-400">{a.size}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* AI Summary strip */}
      {interaction.ai.aiSummary && (
        <div className="px-5 py-2.5 bg-violet-50 border-b border-violet-100 flex items-start gap-2 shrink-0">
          <Bot className="h-3.5 w-3.5 text-violet-600 shrink-0 mt-0.5" />
          <p className="text-[10px] text-violet-800 leading-relaxed">
            <span className="font-bold">AI: </span>{interaction.ai.aiSummary}
          </p>
        </div>
      )}

      {/* Email thread */}
      <div className="flex-1 overflow-y-auto p-5 space-y-5 bg-[#F8FAFC]">
        {interaction.messages.map((m, i) => {
          if (m.type === "system_event" || m.type === "ai_note") {
            return (
              <div key={m.id} className="flex justify-center">
                <span className={cn(
                  "text-[10px] px-3 py-1 rounded-full border font-medium",
                  m.type === "ai_note"
                    ? "bg-violet-50 border-violet-100 text-violet-700"
                    : "bg-slate-50 border-slate-200 text-slate-400"
                )}>
                  {m.text}
                </span>
              </div>
            );
          }

          const isCustomer = m.sender === "customer";
          return (
            <div key={m.id} className="bg-white rounded-2xl border border-[#E2E8F0] overflow-hidden shadow-sm">
              {/* Email card header */}
              <div className="px-4 py-3 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={cn(
                    "h-7 w-7 rounded-lg flex items-center justify-center text-[10px] font-extrabold",
                    isCustomer ? "bg-slate-200 text-slate-600" : "bg-[#0052FF]/10 text-[#0052FF]"
                  )}>
                    {isCustomer ? interaction.customer.name.charAt(0) : "LM"}
                  </div>
                  <div>
                    <p className="text-[10px] font-bold text-[#0F172A]">
                      {isCustomer ? interaction.customer.name : (m.agentName ?? "LuMay Insurance")}
                    </p>
                    <p className="text-[9px] text-slate-400">
                      {isCustomer ? interaction.customer.email : "noreply@lumay.om"}
                    </p>
                  </div>
                </div>
                <span className="text-[9px] text-slate-400 font-mono">{m.time}</span>
              </div>
              {/* Email body */}
              <div className="px-4 py-4 text-[11px] text-[#334155] leading-relaxed whitespace-pre-line">
                {m.text}
              </div>
            </div>
          );
        })}
      </div>

      {/* Reply compose */}
      <form onSubmit={handleSend} className="border-t border-[#E2E8F0] bg-white p-4 shrink-0">
        <div className="border border-slate-200 rounded-xl overflow-hidden focus-within:ring-2 focus-within:ring-[#0052FF]/20 focus-within:border-[#0052FF]/40 transition-all">
          <div className="px-4 py-2 border-b border-slate-100 flex items-center gap-2 text-[10px] text-slate-500 bg-slate-50">
            <span className="font-medium">To:</span>
            <span className="font-bold text-[#0F172A]">{interaction.customer.email}</span>
          </div>
          <textarea
            rows={3}
            placeholder="Write your reply..."
            value={inputValue}
            onChange={e => onInputChange(e.target.value)}
            className="w-full px-4 py-3 text-xs focus:outline-none resize-none"
          />
          <div className="flex items-center gap-2 px-4 py-2.5 border-t border-slate-100 bg-slate-50">
            <button type="button" className="text-slate-400 hover:text-slate-600">
              <Paperclip className="h-4 w-4" />
            </button>
            <div className="ml-auto flex items-center gap-2">
              <button type="button" className="px-3 py-1.5 text-[10px] font-bold text-slate-600 border border-slate-200 rounded-xl hover:bg-slate-100 transition-colors">
                Save Draft
              </button>
              <button
                type="submit"
                disabled={!inputValue.trim()}
                className="px-4 py-1.5 text-[10px] font-bold text-white bg-[#0052FF] hover:bg-[#0040CC] rounded-xl disabled:opacity-50 transition-colors"
              >
                Send Reply
              </button>
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}

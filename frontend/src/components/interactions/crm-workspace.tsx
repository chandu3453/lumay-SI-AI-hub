"use client";

import { useState } from "react";
import { BookUser, User, Clock, Plus, ChevronRight } from "lucide-react";
import { cn } from "@/lib/cn";
import type { WorkspaceInteraction } from "@/features/interactions/types";

interface CrmWorkspaceProps {
  interaction: WorkspaceInteraction;
  onSend: (text: string) => void;
}

const PAST_INTERACTIONS = [
  { date: "Jun 15, 2024", channel: "Email", subject: "Premium payment query", agent: "Noor Al Amri", resolved: true },
  { date: "Apr 02, 2024", channel: "Web Chat", subject: "Policy document request", agent: "Sara Al Rashdi", resolved: true },
  { date: "Feb 18, 2024", channel: "Voice", subject: "Claim status inquiry", agent: "Khalid Al Farsi", resolved: true },
];

export function CrmWorkspace({ interaction, onSend }: CrmWorkspaceProps) {
  const [note, setNote] = useState("");

  return (
    <div className="flex flex-col h-full">
      {/* CRM header */}
      <div className="px-5 py-3 bg-gradient-to-r from-[#0891B2]/5 to-white border-b border-[#0891B2]/10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-xl bg-[#0891B2]/10 flex items-center justify-center">
            <BookUser className="h-4 w-4 text-[#0891B2]" />
          </div>
          <div>
            <p className="text-xs font-extrabold text-[#0F172A]">CRM Records — {interaction.customer.name}</p>
            <p className="text-[10px] text-slate-400">Customer since {interaction.customer.customerSince} · {interaction.customer.segment}</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {/* Current Interaction Notes */}
        <div className="p-4 space-y-3">
          <p className="text-[10px] font-extrabold text-slate-400 uppercase">Current Interaction Notes</p>
          <div className="space-y-2">
            {interaction.messages.filter(m => m.sender !== "system" && m.type !== "ai_note").map(m => (
              <div key={m.id} className="flex gap-3 items-start">
                <div className="relative shrink-0">
                  <div className={cn(
                    "h-7 w-7 rounded-full flex items-center justify-center text-[9px] font-extrabold",
                    m.sender === "customer" ? "bg-slate-200 text-slate-600" : "bg-[#0052FF]/10 text-[#0052FF]"
                  )}>
                    {m.sender === "customer" ? interaction.customer.name.charAt(0) : (m.agentName?.[0] ?? "A")}
                  </div>
                  <div className="absolute top-7 bottom-0 left-1/2 -translate-x-1/2 w-px bg-slate-100" />
                </div>
                <div className="pb-3 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold text-[#0F172A]">
                      {m.sender === "customer" ? interaction.customer.name : (m.agentName ?? "Agent")}
                    </span>
                    <span className="text-[9px] text-slate-400 font-mono">{m.time}</span>
                  </div>
                  <p className="text-[11px] text-[#334155] mt-0.5 leading-relaxed">{m.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="h-px bg-slate-100 mx-4" />

        {/* Interaction History */}
        <div className="p-4 space-y-3">
          <p className="text-[10px] font-extrabold text-slate-400 uppercase">Interaction History</p>
          <div className="space-y-2">
            {PAST_INTERACTIONS.map((pi, i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-white border border-[#E2E8F0] rounded-xl hover:bg-slate-50 cursor-pointer group transition-all">
                <div className="h-8 w-8 rounded-lg bg-slate-100 flex items-center justify-center">
                  <User className="h-4 w-4 text-slate-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold text-[#0F172A] truncate">{pi.subject}</span>
                    {pi.resolved && (
                      <span className="text-[8px] px-1.5 py-0.5 bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/20 rounded font-bold shrink-0">
                        Resolved
                      </span>
                    )}
                  </div>
                  <p className="text-[9px] text-slate-400">{pi.date} · {pi.channel} · {pi.agent}</p>
                </div>
                <ChevronRight className="h-3.5 w-3.5 text-slate-300 group-hover:text-slate-500 transition-colors" />
              </div>
            ))}
          </div>
        </div>

        {/* Add Manual Note */}
        <div className="p-4 space-y-3">
          <p className="text-[10px] font-extrabold text-slate-400 uppercase">Add CRM Note</p>
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <textarea
              rows={3}
              placeholder="Add a manual note about this customer interaction..."
              value={note}
              onChange={e => setNote(e.target.value)}
              className="w-full px-4 py-3 text-xs focus:outline-none resize-none"
            />
            <div className="flex justify-end px-4 py-2.5 border-t border-slate-100 bg-slate-50">
              <button
                onClick={() => { onSend(note); setNote(""); }}
                disabled={!note.trim()}
                className="flex items-center gap-1.5 px-4 py-1.5 bg-[#0052FF] hover:bg-[#0040CC] disabled:opacity-50 text-white rounded-xl text-[10px] font-bold transition-all"
              >
                <Plus className="h-3 w-3" />Save Note
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

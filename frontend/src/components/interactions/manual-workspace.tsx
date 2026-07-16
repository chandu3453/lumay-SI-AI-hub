"use client";

import { useState } from "react";
import { ClipboardList, User, Building2, Phone, Save, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/cn";
import type { WorkspaceInteraction } from "@/features/interactions/types";

interface ManualWorkspaceProps {
  interaction: WorkspaceInteraction;
  onSend: (text: string) => void;
}

const INTERACTION_TYPES = [
  { id: "walk_in", label: "Walk-in Complaint", icon: "🚶" },
  { id: "phone_summary", label: "Phone Call Summary", icon: "📞" },
  { id: "branch_visit", label: "Branch Visit", icon: "🏢" },
  { id: "external", label: "External Complaint", icon: "📋" },
] as const;

export function ManualWorkspace({ interaction, onSend }: ManualWorkspaceProps) {
  const [type, setType] = useState<string>("walk_in");
  const [summary, setSummary] = useState("");
  const [saved, setSaved] = useState(false);

  function handleSave() {
    if (!summary.trim()) return;
    onSend(`[${INTERACTION_TYPES.find(t => t.id === type)?.label}] ${summary}`);
    setSaved(true);
    setSummary("");
    setTimeout(() => setSaved(false), 3000);
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-5 py-3 bg-gradient-to-r from-[#78716C]/5 to-white border-b border-[#78716C]/10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-xl bg-[#78716C]/10 flex items-center justify-center">
            <ClipboardList className="h-4 w-4 text-[#78716C]" />
          </div>
          <div>
            <p className="text-xs font-extrabold text-[#0F172A]">Manual Interaction Record</p>
            <p className="text-[10px] text-slate-400">Agent manually records interaction details</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {/* Existing interaction notes */}
        {interaction.messages.filter(m => m.sender !== "system").length > 0 && (
          <div className="space-y-3">
            <p className="text-[10px] font-extrabold text-slate-400 uppercase">Recorded Entries</p>
            {interaction.messages.filter(m => m.type !== "system_event").map(m => (
              <div key={m.id} className={cn(
                "p-4 rounded-xl border",
                m.type === "ai_note"
                  ? "bg-violet-50 border-violet-100"
                  : "bg-white border-slate-200 shadow-sm"
              )}>
                <div className="flex items-center gap-2 mb-2">
                  <div className="h-6 w-6 rounded-lg bg-slate-100 flex items-center justify-center">
                    <User className="h-3 w-3 text-slate-500" />
                  </div>
                  <span className="text-[10px] font-bold text-[#0F172A]">{m.agentName ?? "Agent"}</span>
                  <span className="text-[9px] text-slate-400 font-mono ml-auto">{m.time}</span>
                </div>
                <p className="text-[11px] text-[#334155] leading-relaxed">{m.text}</p>
              </div>
            ))}
          </div>
        )}

        {/* New entry form */}
        <div className="space-y-4">
          <p className="text-[10px] font-extrabold text-slate-400 uppercase">New Entry</p>

          {/* Interaction type */}
          <div className="grid grid-cols-2 gap-2">
            {INTERACTION_TYPES.map(t => (
              <button
                key={t.id}
                onClick={() => setType(t.id)}
                className={cn(
                  "flex items-center gap-2 px-3 py-2.5 rounded-xl border text-[10px] font-bold transition-all text-left",
                  type === t.id
                    ? "bg-[#EFF6FF] border-[#BFDBFE] text-[#0052FF]"
                    : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"
                )}
              >
                <span>{t.icon}</span>
                {t.label}
              </button>
            ))}
          </div>

          {/* Customer ref */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[9px] font-bold text-slate-400 uppercase mb-1">Customer</label>
              <div className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-[11px] font-semibold text-[#0F172A]">
                {interaction.customer.name}
              </div>
            </div>
            <div>
              <label className="block text-[9px] font-bold text-slate-400 uppercase mb-1">Policy</label>
              <div className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-[11px] font-mono text-[#0F172A]">
                {interaction.customer.policyNumber}
              </div>
            </div>
          </div>

          {/* Summary */}
          <div>
            <label className="block text-[9px] font-bold text-slate-400 uppercase mb-1.5">Interaction Summary</label>
            <textarea
              rows={5}
              placeholder="Describe the customer interaction in detail — complaint raised, resolution provided, follow-up required..."
              value={summary}
              onChange={e => setSummary(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-xs focus:outline-none focus:ring-2 focus:ring-[#0052FF]/20 focus:border-[#0052FF]/40 resize-none leading-relaxed transition-all"
            />
          </div>

          {/* Save button */}
          {saved ? (
            <div className="flex items-center gap-2 p-3 bg-[#10B981]/10 border border-[#10B981]/20 rounded-xl">
              <CheckCircle2 className="h-4 w-4 text-[#10B981]" />
              <span className="text-xs font-bold text-[#10B981]">Interaction saved successfully</span>
            </div>
          ) : (
            <button
              onClick={handleSave}
              disabled={!summary.trim()}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-[#0052FF] hover:bg-[#0040CC] disabled:opacity-50 text-white rounded-xl text-xs font-extrabold transition-all shadow-sm"
            >
              <Save className="h-4 w-4" />
              Save Interaction Record
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

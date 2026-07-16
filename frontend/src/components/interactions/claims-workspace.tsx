"use client";

import { useState } from "react";
import { FileCheck2, User, Plus, Save, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/cn";
import type { WorkspaceInteraction } from "@/features/interactions/types";

interface ClaimsWorkspaceProps {
  interaction: WorkspaceInteraction;
  onSend: (text: string) => void;
}

const NOTE_TYPES = [
  { id: "adjuster", label: "Adjuster Note", color: "#0052FF" },
  { id: "surveyor", label: "Surveyor Note", color: "#10B981" },
  { id: "medical", label: "Medical Reviewer", color: "#EC4899" },
  { id: "legal", label: "Legal Note", color: "#F59E0B" },
];

export function ClaimsWorkspace({ interaction, onSend }: ClaimsWorkspaceProps) {
  const [noteType, setNoteType] = useState("adjuster");
  const [note, setNote] = useState("");
  const [saved, setSaved] = useState(false);

  function handleSave() {
    if (!note.trim()) return;
    const type = NOTE_TYPES.find(t => t.id === noteType);
    onSend(`[${type?.label ?? "Note"}] ${note}`);
    setSaved(true);
    setNote("");
    setTimeout(() => setSaved(false), 3000);
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-5 py-3 bg-gradient-to-r from-[#10B981]/5 to-white border-b border-[#10B981]/10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-xl bg-[#10B981]/10 flex items-center justify-center">
            <FileCheck2 className="h-4 w-4 text-[#10B981]" />
          </div>
          <div>
            <p className="text-xs font-extrabold text-[#0F172A]">Claims Notes — {interaction.claimNumber ?? "Internal"}</p>
            <p className="text-[10px] text-slate-400">
              {interaction.adjusterName ? `Lead Adjuster: ${interaction.adjusterName}` : "Internal claims documentation"}
            </p>
          </div>
          {interaction.claimNumber && (
            <span className="ml-auto text-[9px] font-bold px-2.5 py-1 bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/20 rounded-full">
              {interaction.claimNumber}
            </span>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {/* Existing notes */}
        <div className="space-y-3">
          <p className="text-[10px] font-extrabold text-slate-400 uppercase">Internal Notes</p>
          {interaction.messages.filter(m => m.type !== "system_event").map(m => {
            const isAI = m.type === "ai_note";
            return (
              <div
                key={m.id}
                className={cn(
                  "p-4 rounded-xl border shadow-sm",
                  isAI ? "bg-violet-50 border-violet-100" : "bg-white border-[#E2E8F0]"
                )}
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <div className={cn(
                      "h-6 w-6 rounded-lg flex items-center justify-center text-[9px] font-extrabold",
                      isAI ? "bg-violet-100 text-violet-600" : "bg-[#10B981]/10 text-[#10B981]"
                    )}>
                      {isAI ? "AI" : (m.agentName?.[0] ?? "A")}
                    </div>
                    <div>
                      <span className="text-[10px] font-bold text-[#0F172A]">
                        {isAI ? "AI Intelligence" : (m.agentName ?? "Agent")}
                      </span>
                    </div>
                  </div>
                  <span className="text-[9px] text-slate-400 font-mono shrink-0">{m.time}</span>
                </div>
                <p className="text-[11px] text-[#334155] leading-relaxed">{m.text}</p>
              </div>
            );
          })}
        </div>

        {/* New note form */}
        <div className="space-y-3">
          <p className="text-[10px] font-extrabold text-slate-400 uppercase">Add New Note</p>

          {/* Note type selector */}
          <div className="flex flex-wrap gap-2">
            {NOTE_TYPES.map(t => (
              <button
                key={t.id}
                onClick={() => setNoteType(t.id)}
                className={cn(
                  "px-3 py-1.5 rounded-xl border text-[10px] font-bold transition-all",
                  noteType === t.id ? "text-white border-transparent shadow-sm" : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50"
                )}
                style={noteType === t.id ? { backgroundColor: t.color } : {}}
              >
                {t.label}
              </button>
            ))}
          </div>

          <textarea
            rows={4}
            placeholder={`Add a ${NOTE_TYPES.find(t => t.id === noteType)?.label ?? "note"} — findings, assessment, recommendations...`}
            value={note}
            onChange={e => setNote(e.target.value)}
            className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-xs focus:outline-none focus:ring-2 focus:ring-[#0052FF]/20 focus:border-[#0052FF]/40 resize-none leading-relaxed transition-all"
          />

          {saved ? (
            <div className="flex items-center gap-2 p-3 bg-[#10B981]/10 border border-[#10B981]/20 rounded-xl">
              <CheckCircle2 className="h-4 w-4 text-[#10B981]" />
              <span className="text-xs font-bold text-[#10B981]">Note saved to claims file</span>
            </div>
          ) : (
            <button
              onClick={handleSave}
              disabled={!note.trim()}
              className="w-full flex items-center justify-center gap-2 py-2.5 bg-[#10B981] hover:bg-[#059669] disabled:opacity-50 text-white rounded-xl text-xs font-extrabold transition-all shadow-sm"
            >
              <Save className="h-4 w-4" />
              Save to Claims File
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

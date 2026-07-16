"use client";

import { Radio, Bot, BookOpen, AlertTriangle, TrendingUp, Zap } from "lucide-react";
import { cn } from "@/lib/cn";
import type { WorkspaceInteraction } from "@/features/interactions/types";
import { MessageBubble } from "./message-bubble";

interface SmartCallWorkspaceProps {
  interaction: WorkspaceInteraction;
}

const AI_SUGGESTIONS = [
  { text: "Verify claim number and policy status before addressing delay concerns", priority: "high" },
  { text: "Offer to escalate to Claims Manager if customer requests it", priority: "medium" },
  { text: "Reference SLA policy — 15 business day claim resolution commitment", priority: "medium" },
  { text: "Ask if customer wants WhatsApp status updates enabled", priority: "low" },
];

export function SmartCallWorkspace({ interaction }: SmartCallWorkspaceProps) {
  const escRisk = interaction.ai.escalationRisk;

  return (
    <div className="flex flex-col h-full">
      {/* SMART CALL header */}
      <div className="px-5 py-3 bg-gradient-to-r from-[#EC4899]/5 to-white border-b border-[#EC4899]/10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-xl bg-[#EC4899]/10 flex items-center justify-center">
            <Radio className="h-4 w-4 text-[#EC4899]" />
          </div>
          <div>
            <p className="text-xs font-extrabold text-[#0F172A]">SMART CALL — AI Voice Agent</p>
            <p className="text-[10px] text-slate-400">AI-handled interaction · {interaction.callDuration}</p>
          </div>
          <div className="ml-auto flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-slate-400" />
            <span className="text-[10px] text-slate-500">Completed</span>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        {/* Transcript */}
        <div className="p-4 space-y-3">
          <p className="text-[10px] font-bold text-slate-400 uppercase">AI Transcript</p>
          {interaction.messages.map(m => (
            <MessageBubble key={m.id} msg={m} />
          ))}
        </div>

        {/* Divider */}
        <div className="h-px bg-slate-100 mx-4" />

        {/* Real-time AI Suggestions */}
        <div className="p-4 space-y-3">
          <div className="flex items-center gap-2">
            <Zap className="h-3.5 w-3.5 text-[#EC4899]" />
            <p className="text-[10px] font-extrabold text-slate-400 uppercase">AI Suggestions</p>
          </div>
          <div className="space-y-2">
            {AI_SUGGESTIONS.map((s, i) => (
              <div
                key={i}
                className={cn(
                  "flex items-start gap-2 p-2.5 rounded-xl border text-[11px]",
                  s.priority === "high"
                    ? "bg-[#EF4444]/5 border-[#EF4444]/20"
                    : s.priority === "medium"
                    ? "bg-[#F59E0B]/5 border-[#F59E0B]/20"
                    : "bg-slate-50 border-slate-100"
                )}
              >
                <div className={cn(
                  "h-1.5 w-1.5 rounded-full mt-1.5 shrink-0",
                  s.priority === "high" ? "bg-[#EF4444]" :
                  s.priority === "medium" ? "bg-[#F59E0B]" : "bg-slate-400"
                )} />
                <span className="text-[#334155] leading-snug">{s.text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Escalation risk meter */}
        <div className="mx-4 mb-4 p-4 bg-white border border-[#E2E8F0] rounded-xl space-y-2 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-3.5 w-3.5 text-[#EF4444]" />
              <span className="text-[10px] font-extrabold text-[#0F172A]">Escalation Risk</span>
            </div>
            <span className={cn(
              "text-[10px] font-extrabold px-2 py-0.5 rounded-full",
              escRisk >= 75 ? "bg-[#EF4444]/10 text-[#EF4444]" :
              escRisk >= 50 ? "bg-[#F59E0B]/10 text-[#F59E0B]" : "bg-[#10B981]/10 text-[#10B981]"
            )}>
              {escRisk}%
            </span>
          </div>
          <div className="h-2.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              className={cn(
                "h-full rounded-full transition-all duration-700",
                escRisk >= 75 ? "bg-[#EF4444]" :
                escRisk >= 50 ? "bg-[#F59E0B]" : "bg-[#10B981]"
              )}
              style={{ width: `${escRisk}%` }}
            />
          </div>
        </div>

        {/* Knowledge articles */}
        <div className="px-4 pb-4 space-y-2">
          <div className="flex items-center gap-2">
            <BookOpen className="h-3.5 w-3.5 text-[#0052FF]" />
            <p className="text-[10px] font-extrabold text-slate-400 uppercase">Knowledge Articles</p>
          </div>
          {interaction.ai.knowledgeArticles.map((a, i) => (
            <div key={i} className="flex items-center justify-between p-2.5 bg-[#EFF6FF]/50 border border-[#BFDBFE]/30 rounded-xl cursor-pointer hover:bg-[#EFF6FF] transition-colors">
              <div className="flex items-center gap-2">
                <BookOpen className="h-3 w-3 text-[#0052FF]" />
                <span className="text-[10px] font-medium text-[#0F172A]">{a.title}</span>
              </div>
              <span className="text-[9px] font-bold text-[#0052FF]">{a.relevance}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

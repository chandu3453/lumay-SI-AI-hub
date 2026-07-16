"use client";

import { Star, Bot, TrendingDown } from "lucide-react";
import { cn } from "@/lib/cn";
import type { WorkspaceInteraction } from "@/features/interactions/types";

interface SurveyWorkspaceProps {
  interaction: WorkspaceInteraction;
}

function StarRating({ rating, max = 5 }: { rating: number; max?: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {Array.from({ length: max }).map((_, i) => (
        <Star
          key={i}
          className={cn(
            "h-3.5 w-3.5",
            i < rating ? "text-[#F59E0B] fill-[#F59E0B]" : "text-slate-200 fill-slate-200"
          )}
        />
      ))}
    </div>
  );
}

function ScoreGauge({ score, max = 10 }: { score: number; max?: number }) {
  const pct = (score / max) * 100;
  const color = score >= 7 ? "#10B981" : score >= 4 ? "#F59E0B" : "#EF4444";
  return (
    <div className="flex flex-col items-center gap-1">
      <div
        className="h-16 w-16 rounded-full flex items-center justify-center text-xl font-extrabold text-white shadow-sm"
        style={{ background: `conic-gradient(${color} ${pct}%, #E2E8F0 0)` }}
      >
        <div className="h-12 w-12 rounded-full bg-white flex items-center justify-center">
          <span className="text-lg font-extrabold" style={{ color }}>{score}</span>
        </div>
      </div>
      <span className="text-[9px] font-bold text-slate-400">out of {max}</span>
    </div>
  );
}

export function SurveyWorkspace({ interaction }: SurveyWorkspaceProps) {
  const score = interaction.surveyScore ?? 0;
  const responses = interaction.surveyResponses ?? [];
  const churnRisk = score <= 4 ? "High" : score <= 6 ? "Medium" : "Low";
  const churnColor = score <= 4 ? "text-[#EF4444]" : score <= 6 ? "text-[#F59E0B]" : "text-[#10B981]";

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-5 py-3 bg-gradient-to-r from-[#F59E0B]/5 to-white border-b border-[#F59E0B]/10 shrink-0">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-xl bg-[#F59E0B]/10 flex items-center justify-center">
            <Star className="h-4 w-4 text-[#F59E0B]" />
          </div>
          <div>
            <p className="text-xs font-extrabold text-[#0F172A]">Customer Survey Response</p>
            <p className="text-[10px] text-slate-400">{interaction.subject}</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {/* Score overview */}
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm flex items-center gap-6">
          <ScoreGauge score={score} />
          <div className="flex-1 space-y-2">
            <div>
              <p className="text-[9px] font-bold text-slate-400 uppercase">Overall Score</p>
              <p className={cn(
                "text-lg font-extrabold",
                score >= 7 ? "text-[#10B981]" : score >= 4 ? "text-[#F59E0B]" : "text-[#EF4444]"
              )}>
                {score <= 4 ? "Very Dissatisfied" : score <= 6 ? "Neutral" : "Satisfied"}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <TrendingDown className={cn("h-4 w-4", churnColor)} />
              <span className="text-[10px] text-slate-500">Churn Risk:</span>
              <span className={cn("text-[10px] font-extrabold", churnColor)}>{churnRisk}</span>
            </div>
            <div className="flex items-center gap-2">
              <Bot className="h-4 w-4 text-violet-500" />
              <span className="text-[10px] text-slate-500">Complaint Probability:</span>
              <span className="text-[10px] font-extrabold text-violet-600">
                {interaction.ai.detectionConfidence}%
              </span>
            </div>
          </div>
        </div>

        {/* Survey questions */}
        <div className="space-y-3">
          <p className="text-[10px] font-extrabold text-slate-400 uppercase">Survey Responses</p>
          {responses.map((r, i) => (
            <div key={i} className="bg-white border border-[#E2E8F0] rounded-xl p-4 shadow-sm space-y-2">
              <div className="flex items-start justify-between gap-2">
                <p className="text-[10px] font-bold text-[#0F172A] leading-snug flex-1">{r.question}</p>
                {r.rating != null && <StarRating rating={r.rating} />}
              </div>
              <p className={cn(
                "text-[11px] leading-relaxed px-3 py-2 rounded-lg",
                r.rating != null && r.rating <= 2
                  ? "text-[#EF4444] bg-[#EF4444]/5"
                  : r.rating != null && r.rating <= 3
                  ? "text-[#F59E0B] bg-[#F59E0B]/5"
                  : "text-[#334155] bg-slate-50"
              )}>
                {r.answer}
              </p>
            </div>
          ))}
        </div>

        {/* AI recommendation */}
        <div className="bg-violet-50 border border-violet-100 rounded-2xl p-4 space-y-2">
          <div className="flex items-center gap-2">
            <Bot className="h-4 w-4 text-violet-600" />
            <span className="text-[10px] font-extrabold text-violet-700 uppercase">AI Recommendation</span>
          </div>
          <p className="text-[11px] text-violet-800 leading-relaxed">{interaction.ai.suggestedResolution}</p>
          <div className="flex items-center gap-2 pt-1">
            <span className="text-[9px] font-bold text-violet-500 uppercase">Recommended Action:</span>
            <span className="text-[9px] font-bold text-[#0052FF]">{interaction.ai.recommendedDepartment}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

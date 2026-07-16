"use client";

import { useState } from "react";
import {
  Bot, User, Shield, AlertTriangle, TrendingUp,
  Clock, ChevronDown, ChevronUp, BookOpen, RefreshCw,
  Plus, UserCog, FileText, Zap, ExternalLink,
} from "lucide-react";
import { cn } from "@/lib/cn";
import type { WorkspaceInteraction, RiskLevel } from "@/features/interactions/types";

const SENTIMENT_CONFIG: Record<string, { label: string; emoji: string; cls: string }> = {
  very_positive: { label: "Very Positive", emoji: "😊", cls: "text-[#10B981] bg-[#10B981]/10" },
  positive: { label: "Positive", emoji: "🙂", cls: "text-[#34D399] bg-[#34D399]/10" },
  neutral: { label: "Neutral", emoji: "😐", cls: "text-slate-500 bg-slate-100" },
  negative: { label: "Negative", emoji: "😟", cls: "text-[#F59E0B] bg-[#F59E0B]/10" },
  very_negative: { label: "Very Negative", emoji: "😠", cls: "text-[#EF4444] bg-[#EF4444]/10" },
  extremely_negative: { label: "Extremely Negative", emoji: "🤬", cls: "text-[#7F1D1D] bg-[#EF4444]/15" },
};

const SEVERITY_BAR: Record<string, { pct: number; cls: string }> = {
  low: { pct: 25, cls: "bg-[#10B981]" },
  medium: { pct: 55, cls: "bg-[#F59E0B]" },
  high: { pct: 80, cls: "bg-[#EF4444]" },
  critical: { pct: 100, cls: "bg-[#7F1D1D] animate-pulse" },
};

const RISK_CONFIG: Record<RiskLevel, { label: string; cls: string }> = {
  low: { label: "Low", cls: "text-[#10B981] bg-[#10B981]/10 border-[#10B981]/20" },
  medium: { label: "Medium", cls: "text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/20" },
  high: { label: "High", cls: "text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/20" },
  critical: { label: "Critical", cls: "text-white bg-[#EF4444] border-[#EF4444] animate-pulse" },
};

const SLA_CONFIG = {
  resolved: { label: "Resolved", cls: "text-[#10B981] bg-[#10B981]/10" },
  on_track: { label: "On Track", cls: "text-[#10B981] bg-[#10B981]/10" },
  at_risk: { label: "At Risk", cls: "text-[#F59E0B] bg-[#F59E0B]/10" },
  breached: { label: "SLA Breached", cls: "text-[#EF4444] bg-[#EF4444]/10" },
};

function Section({ title, children, defaultOpen = true }: { title: string; children: React.ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-[#E2E8F0] rounded-xl overflow-hidden shadow-sm">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3 bg-white hover:bg-slate-50/50 transition-colors"
      >
        <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">{title}</span>
        {open ? <ChevronUp className="h-3.5 w-3.5 text-slate-400" /> : <ChevronDown className="h-3.5 w-3.5 text-slate-400" />}
      </button>
      {open && <div className="px-4 pb-4 pt-1 bg-white space-y-3">{children}</div>}
    </div>
  );
}

function DataRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between py-0.5">
      <span className="text-[10px] text-slate-400 shrink-0">{label}</span>
      <div className="text-[10px] font-semibold text-[#0F172A] text-right">{children}</div>
    </div>
  );
}

interface AIIntelligencePanelProps {
  interaction: WorkspaceInteraction;
  onCreateComplaint: () => void;
  onEscalate: () => void;
  onAssignAgent: () => void;
  onGenerateSummary: () => void;
  isCreatingComplaint?: boolean;
  isGeneratingSummary?: boolean;
}

export function AIIntelligencePanel({
  interaction,
  onCreateComplaint,
  onEscalate,
  onAssignAgent,
  onGenerateSummary,
  isCreatingComplaint,
  isGeneratingSummary,
}: AIIntelligencePanelProps) {
  const { customer, ai } = interaction;
  const [showFullResponse, setShowFullResponse] = useState(false);

  const sentConf = SENTIMENT_CONFIG[ai.sentiment] ?? SENTIMENT_CONFIG.neutral;
  const sevBar = SEVERITY_BAR[ai.severity] ?? SEVERITY_BAR.low;
  const riskConf = RISK_CONFIG[ai.escalationRiskLevel] ?? RISK_CONFIG.low;
  const slaConf = SLA_CONFIG[ai.slaRisk] ?? SLA_CONFIG.on_track;

  return (
    <div className="flex flex-col gap-3 h-full overflow-y-auto pr-0.5">
      {/* Customer Profile */}
      <Section title="Customer Profile">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
          <div className="h-10 w-10 rounded-full bg-gradient-to-br from-[#EFF6FF] to-[#DBEAFE] flex items-center justify-center text-sm font-extrabold text-[#0052FF] shrink-0">
            {customer.name.charAt(0)}
          </div>
          <div className="min-w-0">
            <h5 className="text-xs font-extrabold text-[#0F172A] truncate">{customer.name}</h5>
            <p className="text-[9px] text-slate-400 truncate">{customer.phone}</p>
            <p className="text-[9px] text-slate-400 truncate">{customer.email}</p>
          </div>
        </div>
        <div className="space-y-1.5">
          <DataRow label="Policy">{customer.policyNumber}</DataRow>
          <DataRow label="Product">{customer.product}</DataRow>
          <DataRow label="Segment">
            <span className={cn(
              "px-1.5 py-0.5 rounded text-[9px] font-bold border",
              customer.segment === "VIP"
                ? "bg-amber-50 text-amber-700 border-amber-200"
                : customer.segment === "Premium"
                ? "bg-[#EFF6FF] text-[#0052FF] border-[#BFDBFE]"
                : "bg-slate-50 text-slate-600 border-slate-200"
            )}>
              {customer.segment}
            </span>
          </DataRow>
          <DataRow label="Customer Since">{customer.customerSince}</DataRow>
          <DataRow label="Location">{customer.city}</DataRow>
          {customer.claimStatus && (
            <DataRow label="Claim Status">
              <span className="text-[9px] font-bold text-[#F59E0B]">{customer.claimStatus}</span>
            </DataRow>
          )}
          <DataRow label="Lifetime Value">OMR {customer.lifetimeValue.toLocaleString()}</DataRow>
        </div>

        {/* Complaint history */}
        <div className="pt-2 border-t border-slate-100 space-y-1.5">
          <DataRow label="Total Complaints">{customer.totalComplaints}</DataRow>
          <DataRow label="Open Complaints">
            <span className={customer.openComplaints > 0 ? "text-[#EF4444] font-bold" : ""}>
              {customer.openComplaints}
            </span>
          </DataRow>
          <DataRow label="Repeat Customer">
            <span className={customer.isRepeatCustomer ? "text-[#EF4444] font-bold" : "text-slate-500"}>
              {customer.isRepeatCustomer ? "Yes ⚠" : "No"}
            </span>
          </DataRow>
          {customer.lastComplaint && (
            <DataRow label="Last Complaint">{customer.lastComplaint}</DataRow>
          )}
        </div>
        <div className="pt-1">
          <span className={cn(
            "inline-flex items-center gap-1 text-[9px] font-bold px-2 py-1 rounded-lg border",
            RISK_CONFIG[customer.riskLevel].cls
          )}>
            <Shield className="h-2.5 w-2.5" />
            {RISK_CONFIG[customer.riskLevel].label} Risk Customer
          </span>
        </div>
      </Section>

      {/* AI Complaint Intelligence */}
      <Section title="AI Complaint Intelligence">
        <div className="space-y-2.5">
          {/* Complaint detection */}
          <div className={cn(
            "flex items-center justify-between p-2.5 rounded-lg border",
            ai.complaintDetected
              ? "bg-[#EF4444]/5 border-[#EF4444]/20"
              : "bg-[#10B981]/5 border-[#10B981]/20"
          )}>
            <div className="flex items-center gap-2">
              <AlertTriangle className={cn("h-4 w-4", ai.complaintDetected ? "text-[#EF4444]" : "text-[#10B981]")} />
              <span className="text-xs font-bold text-[#0F172A]">
                {ai.complaintDetected ? "Complaint Detected" : "No Complaint"}
              </span>
            </div>
            <span className={cn(
              "text-[10px] font-extrabold px-2 py-0.5 rounded-full",
              ai.complaintDetected ? "bg-[#EF4444]/10 text-[#EF4444]" : "bg-[#10B981]/10 text-[#10B981]"
            )}>
              {ai.detectionConfidence}%
            </span>
          </div>

          {/* Sentiment */}
          <DataRow label="Sentiment">
            <span className={cn("inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-bold", sentConf.cls)}>
              <span>{sentConf.emoji}</span>
              {sentConf.label}
            </span>
          </DataRow>

          <DataRow label="Emotion">{ai.emotion}</DataRow>
          <DataRow label="Category">{ai.theme}</DataRow>

          {/* Severity bar */}
          <div>
            <DataRow label="Severity">
              <span className={cn(
                "text-[10px] font-bold capitalize",
                ai.severity === "high" || ai.severity === "critical" ? "text-[#EF4444]" :
                ai.severity === "medium" ? "text-[#F59E0B]" : "text-[#10B981]"
              )}>
                {ai.severity}
              </span>
            </DataRow>
            <div className="mt-1.5 h-1.5 bg-slate-100 rounded-full overflow-hidden">
              <div className={cn("h-full rounded-full transition-all duration-700", sevBar.cls)} style={{ width: `${sevBar.pct}%` }} />
            </div>
          </div>

          {/* Escalation risk */}
          <div>
            <DataRow label="Escalation Risk">
              <span className={cn("text-[10px] font-extrabold px-2 py-0.5 rounded-full border text-[10px]", riskConf.cls)}>
                {riskConf.label} ({ai.escalationRisk}%)
              </span>
            </DataRow>
            <div className="mt-1.5 h-2 bg-slate-100 rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full rounded-full transition-all duration-700",
                  ai.escalationRisk >= 75 ? "bg-[#EF4444]" :
                  ai.escalationRisk >= 50 ? "bg-[#F59E0B]" :
                  "bg-[#10B981]"
                )}
                style={{ width: `${ai.escalationRisk}%` }}
              />
            </div>
          </div>

          <DataRow label="SLA Risk">
            <span className={cn("px-2 py-0.5 rounded-lg text-[10px] font-bold", slaConf.cls)}>
              {slaConf.label}
            </span>
          </DataRow>

          <DataRow label="Repeat Complaint">
            <span className={cn("font-bold", ai.repeatComplaint ? "text-[#EF4444]" : "text-slate-400")}>
              {ai.repeatComplaint ? `Yes (${ai.priorComplaintCount} prior)` : "No"}
            </span>
          </DataRow>

          {ai.regulatoryRisk && (
            <div className="flex items-center gap-2 p-2 bg-red-50 border border-red-100 rounded-lg">
              <Shield className="h-3.5 w-3.5 text-[#EF4444] shrink-0" />
              <span className="text-[10px] font-bold text-[#EF4444]">Regulatory Risk Flagged</span>
            </div>
          )}
        </div>
      </Section>

      {/* AI Summary */}
      <Section title="AI Summary & Recommendations">
        <div className="space-y-3">
          <div>
            <p className="text-[9px] font-bold text-slate-400 uppercase mb-1.5">AI Summary</p>
            <p className="text-[11px] text-[#334155] leading-relaxed">{ai.aiSummary}</p>
          </div>

          <div>
            <p className="text-[9px] font-bold text-slate-400 uppercase mb-1.5">Root Cause</p>
            <p className="text-[11px] text-[#334155] leading-relaxed">{ai.rootCause}</p>
          </div>

          <div>
            <p className="text-[9px] font-bold text-slate-400 uppercase mb-1.5">Suggested Resolution</p>
            <p className="text-[11px] text-[#334155] leading-relaxed">{ai.suggestedResolution}</p>
          </div>

          {ai.recommendedDepartment && (
            <div className="flex items-center gap-2 p-2 bg-[#EFF6FF] border border-[#BFDBFE]/50 rounded-lg">
              <UserCog className="h-3.5 w-3.5 text-[#0052FF] shrink-0" />
              <span className="text-[10px] font-bold text-[#0052FF]">{ai.recommendedDepartment}</span>
            </div>
          )}

          {ai.suggestedResponse && (
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <p className="text-[9px] font-bold text-slate-400 uppercase">Suggested Response</p>
                <button
                  onClick={() => setShowFullResponse(s => !s)}
                  className="text-[9px] font-bold text-[#0052FF] hover:underline"
                >
                  {showFullResponse ? "Collapse" : "Expand"}
                </button>
              </div>
              <div className={cn(
                "bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-[11px] text-[#334155] leading-relaxed overflow-hidden transition-all",
                showFullResponse ? "max-h-[400px]" : "max-h-[60px]"
              )}>
                {ai.suggestedResponse}
              </div>
            </div>
          )}
        </div>
      </Section>

      {/* Knowledge Articles */}
      {ai.knowledgeArticles.length > 0 && (
        <Section title="Knowledge Articles" defaultOpen={false}>
          <div className="space-y-1.5">
            {ai.knowledgeArticles.map((a, i) => (
              <div key={i} className="flex items-start gap-2 p-2 bg-slate-50 rounded-lg border border-slate-100 hover:bg-[#EFF6FF]/50 hover:border-[#BFDBFE]/50 transition-colors cursor-pointer group">
                <BookOpen className="h-3.5 w-3.5 text-[#0052FF] mt-0.5 shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-[10px] font-semibold text-[#0F172A] leading-tight">{a.title}</p>
                  <div className="flex items-center gap-1 mt-0.5">
                    <div className="h-1 flex-1 bg-slate-200 rounded-full">
                      <div className="h-1 bg-[#0052FF] rounded-full" style={{ width: `${a.relevance}%` }} />
                    </div>
                    <span className="text-[9px] text-slate-400 shrink-0">{a.relevance}%</span>
                  </div>
                </div>
                <ExternalLink className="h-3 w-3 text-slate-300 group-hover:text-[#0052FF] shrink-0 transition-colors" />
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Quick Actions */}
      <Section title="Quick Actions">
        <div className="space-y-2">
          {ai.complaintDetected && (
            <button
              onClick={onCreateComplaint}
              disabled={isCreatingComplaint}
              className="w-full py-2.5 bg-[#EF4444] hover:bg-[#DC2626] disabled:opacity-60 text-white rounded-xl text-xs font-extrabold shadow-sm transition-all flex items-center justify-center gap-1.5"
            >
              {isCreatingComplaint
                ? <><RefreshCw className="h-3.5 w-3.5 animate-spin" />Creating...</>
                : <><Plus className="h-3.5 w-3.5" />Create Complaint</>
              }
            </button>
          )}
          <button
            onClick={onCreateComplaint}
            className="w-full py-2 bg-[#0052FF] hover:bg-[#0040CC] text-white rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5"
          >
            <FileText className="h-3.5 w-3.5" />
            Create Complaint Case
          </button>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={onAssignAgent}
              className="py-2 px-2 border border-slate-200 hover:bg-slate-50 text-slate-600 rounded-xl text-[10px] font-bold transition-all flex items-center justify-center gap-1"
            >
              <UserCog className="h-3 w-3" />Assign Agent
            </button>
            <button
              onClick={onEscalate}
              className="py-2 px-2 border border-[#F59E0B]/30 bg-[#FFFBEB] hover:bg-[#FEF3C7] text-[#B45309] rounded-xl text-[10px] font-bold transition-all flex items-center justify-center gap-1"
            >
              <AlertTriangle className="h-3 w-3" />Escalate
            </button>
            <button
              onClick={onGenerateSummary}
              disabled={isGeneratingSummary}
              className="col-span-2 py-2 px-2 border border-violet-200 bg-violet-50 hover:bg-violet-100 text-violet-700 rounded-xl text-[10px] font-bold transition-all flex items-center justify-center gap-1 disabled:opacity-50"
            >
              {isGeneratingSummary
                ? <><RefreshCw className="h-3 w-3 animate-spin" />Generating...</>
                : <><Zap className="h-3 w-3" />Generate AI Summary</>
              }
            </button>
          </div>
        </div>
      </Section>
    </div>
  );
}

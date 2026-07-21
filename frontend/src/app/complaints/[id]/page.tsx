"use client";

import { useParams, useRouter } from "next/navigation";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useComplaintDetail } from "@/features/complaints/hooks/use-complaint-detail";
import { InsuranceBadge } from "@/components/insurance/InsuranceBadge";
import { cn } from "@/lib/cn";
import {
  ArrowLeft, Phone, Mail, MessageCircle, Globe, Radio, ClipboardList,
  AlertTriangle, Clock, Shield, CheckCircle2, Search, Brain,
  FileText, Headphones, Paperclip, MessageSquare, User, Users,
  ChevronRight, Send, Plus, Download, Copy, GitBranch, Bell,
  AlertCircle, RefreshCw, Link2, Calendar, Flag,
} from "lucide-react";
import Link from "next/link";
import { AIIntelligencePanel } from "@/components/complaints/AIIntelligencePanel";
import { AIOverridePanel } from "@/components/complaints/AIOverridePanel";
import { DemoModeToggle } from "@/components/demo/demo-mode-toggle";
import { DemoScenarios } from "@/components/demo/demo-scenarios";
import { DemoTimeline } from "@/components/demo/demo-timeline";
import { LiveInteractionBadge } from "@/components/demo/live-interaction-badge";
import { AIDecisionPanel } from "@/components/demo/ai-decision-panel";
import { CustomerJourneyTimeline } from "@/components/demo/customer-journey-timeline";
import { useDemoSSE } from "@/hooks/use-demo-sse";
import { useDemoStore } from "@/stores/demo.store";
import { useState, useEffect, useCallback } from "react";
import { complaintsService } from "@/services/complaints.service";
import { useAuthStore } from "@/stores/auth.store";
import type { AIOverrideRequest, RelatedComplaintSummary, SLAStatusResult } from "@/types/domain";

const severityColors: Record<string, string> = {
  critical: "bg-[#DC2626]/10 text-[#DC2626]", high: "bg-[#F59E0B]/10 text-[#F59E0B]",
  medium: "bg-[#2563EB]/10 text-[#2563EB]", low: "bg-[#64748B]/10 text-[#64748B]",
};
const priorityColors: Record<string, string> = {
  critical: "bg-[#DC2626]/10 text-[#DC2626]", high: "bg-[#F59E0B]/10 text-[#F59E0B]",
  medium: "bg-[#2563EB]/10 text-[#2563EB]", low: "bg-[#64748B]/10 text-[#64748B]",
};
const statusColors: Record<string, string> = {
  submitted: "bg-[#64748B]/10 text-[#64748B]", open: "bg-[#2563EB]/10 text-[#2563EB]",
  under_review: "bg-[#8B5CF6]/10 text-[#8B5CF6]", investigating: "bg-[#F59E0B]/10 text-[#F59E0B]",
  resolved: "bg-[#16A34A]/10 text-[#16A34A]", closed: "bg-[#64748B]/10 text-[#64748B]",
};
const slaColors: Record<string, string> = {
  on_track: "text-[#16A34A]", at_risk: "text-[#F59E0B]", breached: "text-[#DC2626]", overdue: "text-[#DC2626]",
  within_sla: "text-[#16A34A]",
};
const channelIcons: Record<string, React.ReactNode> = {
  voice: <Phone className="h-4 w-4" />, whatsapp: <MessageCircle className="h-4 w-4" />,
  email: <Mail className="h-4 w-4" />, web_chat: <Globe className="h-4 w-4" />,
  smart_call: <Radio className="h-4 w-4" />, crm: <ClipboardList className="h-4 w-4" />,
  survey: <ClipboardList className="h-4 w-4" />, manual: <ClipboardList className="h-4 w-4" />,
  agent_entered: <ClipboardList className="h-4 w-4" />,
};

function SLACountdown({ deadline, status }: { deadline: string | null | undefined; status: string | null | undefined }) {
  if (!deadline) return <span className="text-[#64748B] text-xs">—</span>;
  try {
    const dl = new Date(deadline);
    const now = new Date();
    const diffMs = dl.getTime() - now.getTime();
    const diffH = Math.floor(Math.abs(diffMs) / 3600000);
    const diffM = Math.floor((Math.abs(diffMs) % 3600000) / 60000);
    const breached = diffMs < 0;
    const pct = status === "within_sla" ? 30 : status === "at_risk" ? 65 : 92;
    const color = breached || status === "breached" ? "text-[#DC2626]" : status === "at_risk" ? "text-[#F59E0B]" : "text-[#16A34A]";
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className={cn("text-lg font-bold", color)}>
            {breached ? "-" : ""}{diffH}h {diffM}m {breached ? "overdue" : "remaining"}
          </span>
          <span className="text-xs text-[#64748B]">{dl.toLocaleDateString("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}</span>
        </div>
        <div className="h-1.5 rounded-full bg-[#F1F5F9]">
          <div className={cn("h-full rounded-full transition-all", breached || status === "breached" ? "bg-[#DC2626]" : status === "at_risk" ? "bg-[#F59E0B]" : "bg-[#16A34A]")} style={{ width: `${Math.min(pct, 100)}%` }} />
        </div>
      </div>
    );
  } catch { return <span className="text-xs text-[#64748B]">—</span>; }
}

export default function ComplaintInvestigationPage() {
  const params = useParams();
  const id = params.id as string;
  const router = useRouter();
  const { data: c, isLoading, refetch } = useComplaintDetail(id);
  const [showOverride, setShowOverride] = useState(false);
  const [related, setRelated] = useState<RelatedComplaintSummary[]>([]);
  const [acknowledging, setAcknowledging] = useState(false);
  const [actionPending, setActionPending] = useState<string | null>(null);
  const demoEnabled = useDemoStore((s) => s.enabled);
  const currentUser = useAuthStore((s) => s.user);

  useDemoSSE();

  useEffect(() => {
    if (!id) return;
    complaintsService.getRelatedComplaints(id, 5)
      .then((res: any) => setRelated(res?.data?.data ?? res?.data ?? []))
      .catch(() => {});
  }, [id]);

  async function handleAcknowledge() {
    if (!c?.id) return;
    setAcknowledging(true);
    try {
      await complaintsService.acknowledge(String(c.id));
      refetch();
    } finally {
      setAcknowledging(false);
    }
  }

  async function handleOverrideSubmit(override: AIOverrideRequest) {
    if (c?.id) {
      await complaintsService.applyAIOverride(String(c.id), override);
      setShowOverride(false);
      refetch();
    }
  }

  async function handleAssign() {
    if (!c?.id || !currentUser?.id) return;
    setActionPending("assign");
    try {
      await complaintsService.assign(String(c.id), currentUser.id);
      refetch();
    } finally {
      setActionPending(null);
    }
  }

  async function handleEscalate() {
    if (!c?.id) return;
    setActionPending("escalate");
    try {
      await complaintsService.escalate(String(c.id));
      refetch();
    } finally {
      setActionPending(null);
    }
  }

  async function handleResolve() {
    if (!c?.id) return;
    setActionPending("resolve");
    try {
      await complaintsService.resolve(String(c.id));
      refetch();
    } finally {
      setActionPending(null);
    }
  }

  async function handleClose() {
    if (!c?.id) return;
    setActionPending("close");
    try {
      await complaintsService.close(String(c.id));
      refetch();
    } finally {
      setActionPending(null);
    }
  }

  if (isLoading) return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in">
        <Skeleton className="h-16 w-full rounded-xl" />
        <div className="grid grid-cols-[1fr_380px] gap-6">
          <div className="space-y-6"><Skeleton className="h-40 w-full" /><Skeleton className="h-48 w-full" /><Skeleton className="h-64 w-full" /></div>
          <div className="space-y-6"><Skeleton className="h-60 w-full" /><Skeleton className="h-48 w-full" /><Skeleton className="h-40 w-full" /></div>
        </div>
      </div>
      <AICopilot />
    </DashboardShell>
  );

  if (!c) return (
    <DashboardShell>
      <div className="flex items-center justify-center h-64"><p className="text-muted-foreground">Complaint not found.</p></div>
      <AICopilot />
    </DashboardShell>
  );

  return (
    <DashboardShell>
      <LiveInteractionBadge />
      <div className="space-y-6 animate-fade-in">
        {/* Back link + Demo Mode toggle */}
        <div className="flex items-center justify-between">
          <Link href="/complaints" className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-[#0F172A] transition-colors">
            <ArrowLeft className="h-4 w-4" /> Back to Complaints
          </Link>
          <DemoModeToggle />
        </div>

        {/* Header */}
        <div className="bg-white rounded-xl border border-border shadow-card p-5">
          <div className="flex items-start justify-between">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <h1 className="text-lg font-bold text-[#0F172A]">{c.complaint_number}</h1>
                <Badge variant="outline" className={cn("text-xs font-medium", priorityColors[c.priority])}>{c.priority}</Badge>
                <Badge variant="outline" className={cn("text-xs font-medium", severityColors[c.severity])}>{c.severity}</Badge>
                <span className={cn("inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium capitalize", statusColors[c.status])}>{c.status.replace(/_/g, " ")}</span>
                {c.regulatory_flag && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-[#DC2626]/10 text-[#DC2626] border border-[#DC2626]/20">
                    <Shield className="h-3 w-3" /> Regulatory
                  </span>
                )}
                {c.is_repeat && (
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-[#F59E0B]/10 text-[#F59E0B]">
                    <AlertCircle className="h-3 w-3" /> Repeat
                  </span>
                )}
              </div>
              <p className="text-sm text-[#0F172A] font-medium">{c.title}</p>
              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <InsuranceBadge line={c.insurance_line} />
                <span className="font-mono">{c.policy_number}</span>
                <span className="text-[#0F172A]">{c.product_name}</span>
                <span>Received {c.received_time ? new Date(c.received_time).toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "—"}</span>
              </div>
              </div>
              <div className="flex items-center gap-2">
                {!c.acknowledged_time && c.status !== "resolved" && c.status !== "closed" && (
                  <button
                    onClick={handleAcknowledge}
                    disabled={acknowledging}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-[#16A34A] text-white rounded-lg text-xs font-medium hover:bg-[#15803D] disabled:opacity-60 transition-colors"
                  >
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    {acknowledging ? "Acknowledging..." : "Acknowledge"}
                  </button>
                )}
                {c.acknowledged_time && (
                  <span className="flex items-center gap-1 text-xs text-[#16A34A] bg-[#F0FDF4] px-2.5 py-1 rounded-md">
                    <CheckCircle2 className="h-3 w-3" />
                    Acknowledged
                  </span>
                )}
              </div>
            </div>
          </div>

        {/* Main grid */}
        <div className="grid grid-cols-[1fr_380px] gap-6">
          {/* Left column */}
          <div className="space-y-6">
            {/* FR-010 Structured AI Summary */}
            <Card className="border-l-4 border-l-[#8B5CF6]">
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <Brain className="h-4 w-4 text-[#8B5CF6]" />
                  <CardTitle className="text-sm font-semibold text-[#0F172A]">AI Structured Summary</CardTitle>
                  <Badge variant="outline" className="text-[10px] px-1.5 py-0 h-4 bg-[#F5F3FF] text-[#8B5CF6] border-[#8B5CF6]/20">FR-010</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {c.ai_summary && <p className="text-sm text-[#475569] leading-relaxed border-l-2 border-[#8B5CF6]/30 pl-3">{c.ai_summary}</p>}

                {/* Key fact grid */}
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { label: "Channel", value: (c.channel ?? c.source ?? "—").replace(/_/g, " ") },
                    { label: "Product", value: (c.product ?? "—").replace(/_/g, " ") },
                    { label: "Policy", value: c.policy_number ?? "—" },
                    { label: "Claim", value: c.claim_number ?? "—" },
                    { label: "Language", value: c.detected_language?.toUpperCase() ?? "EN" },
                    { label: "Theme", value: (c.theme ?? "—").replace(/_/g, " ") },
                  ].map(item => (
                    <div key={item.label} className="bg-[#F8FAFC] rounded-lg p-2.5">
                      <p className="text-[10px] text-muted-foreground">{item.label}</p>
                      <p className="text-xs font-medium text-[#0F172A] mt-0.5 capitalize">{item.value}</p>
                    </div>
                  ))}
                </div>

                {/* Customer requested outcome */}
                {c.customer_requested_outcome && (
                  <div className="bg-[#FFF7ED] border border-[#F59E0B]/30 rounded-lg p-3">
                    <p className="text-[10px] font-semibold text-[#F59E0B] uppercase tracking-wider mb-1">Customer Requested Outcome</p>
                    <p className="text-sm text-[#92400E]">{c.customer_requested_outcome}</p>
                  </div>
                )}

                {/* Recommendation */}
                {c.recommendation && (
                  <div className="bg-[#EFF6FF] border border-[#2563EB]/20 rounded-lg p-3">
                    <p className="text-[10px] font-semibold text-[#2563EB] uppercase tracking-wider mb-1">Recommended Next Action</p>
                    <p className="text-sm text-[#1e3a5f]">{c.recommendation}</p>
                  </div>
                )}

                {/* Sentiment arc */}
                {(c.sentiment_start || c.sentiment || c.sentiment_end) && (
                  <div className="flex items-center gap-3">
                    <span className="text-[10px] text-muted-foreground">Sentiment Arc</span>
                    <div className="flex items-center gap-1.5">
                      {c.sentiment_start && <span className="text-xs px-2 py-0.5 rounded bg-[#FEF2F2] text-[#DC2626]">{c.sentiment_start.replace(/_/g, " ")}</span>}
                      <span className="text-[#94A3B8] text-xs">→</span>
                      {c.sentiment && <span className="text-xs px-2 py-0.5 rounded bg-[#F8FAFC] text-[#475569]">{c.sentiment.replace(/_/g, " ")}</span>}
                      {c.sentiment_end && (<>
                        <span className="text-[#94A3B8] text-xs">→</span>
                        <span className="text-xs px-2 py-0.5 rounded bg-[#F0FDF4] text-[#16A34A]">{c.sentiment_end.replace(/_/g, " ")}</span>
                      </>)}
                    </div>
                  </div>
                )}

                {/* Root cause */}
                {c.root_cause && (
                  <div className="space-y-1">
                    <p className="text-[10px] font-semibold text-[#64748B] uppercase tracking-wider">Root Cause</p>
                    <p className="text-xs text-[#475569]">{c.root_cause}</p>
                    {c.contributing_factors && c.contributing_factors.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {c.contributing_factors.slice(0, 4).map((f: string) => (
                          <span key={f} className="text-[10px] px-2 py-0.5 rounded-full bg-[#F1F5F9] text-[#475569]">{f}</span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>


            {/* Complaint Timeline */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-[#0F172A]">Complaint Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  {c.timeline.map((stage, i) => (
                    <div key={stage.stage} className="flex flex-col items-center">
                      <div className={cn(
                        "h-8 w-8 rounded-full flex items-center justify-center text-xs font-medium border-2",
                        stage.completed ? "bg-[#16A34A] border-[#16A34A] text-white" : "bg-white border-[#E2E8F0] text-muted-foreground",
                      )}>{stage.completed ? "✓" : i + 1}</div>
                      <p className={cn("text-[10px] mt-1.5 text-center", stage.completed ? "text-[#0F172A] font-medium" : "text-muted-foreground")}>{stage.stage}</p>
                      {stage.date && <p className="text-[9px] text-muted-foreground mt-0.5">{stage.date}</p>}
                      {i < c.timeline.length - 1 && <div className={cn("h-0.5 w-8 mt-[-20px] ml-8", stage.completed ? "bg-[#16A34A]" : "bg-[#E2E8F0]")} />}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Interaction Timeline */}
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-semibold text-[#0F172A]">Interaction Timeline</CardTitle>
                  <span className="text-xs text-muted-foreground">{c.interactions.length} interactions</span>
                </div>
              </CardHeader>
              <CardContent className="space-y-0">
                {c.interactions.map((int, i) => (
                  <div key={int.id} className={cn("flex gap-4 pb-5", i < c.interactions.length - 1 ? "border-l-2 border-[#E2E8F0] ml-[17px] pl-7" : "ml-[19px] pl-7")}>
                    <div className={cn(
                      "absolute left-0 h-9 w-9 rounded-full flex items-center justify-center -ml-[18px]",
                      int.direction === "inbound" ? "bg-[#EFF6FF] text-[#2563EB]" : "bg-[#F0FDF4] text-[#16A34A]",
                    )}>
                      {channelIcons[int.channel] ?? <MessageSquare className="h-4 w-4" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-[#0F172A]">{int.subject}</p>
                        <span className="text-[11px] text-muted-foreground shrink-0">{int.timestamp}</span>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">{int.summary}</p>
                      <p className="text-[11px] text-muted-foreground mt-1">
                        <span className={cn("capitalize", int.direction === "inbound" ? "text-[#2563EB]" : "text-[#16A34A]")}>{int.direction}</span>
                        <span className="mx-1">·</span>
                        <span className="capitalize">{int.channel.replace(/_/g, " ")}</span>
                        <span className="mx-1">·</span>
                        {int.agent}
                      </p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Attachments */}
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Paperclip className="h-4 w-4 text-muted-foreground" />
                    <CardTitle className="text-sm font-semibold text-[#0F172A]">Attachments</CardTitle>
                  </div>
                  <span className="text-xs text-muted-foreground">{c.attachments.length} files</span>
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                {c.attachments.map((att) => (
                  <div key={att.id} className="flex items-center justify-between p-2.5 rounded-lg hover:bg-[#F8FAFC] transition-colors cursor-pointer">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        "h-8 w-8 rounded-lg flex items-center justify-center",
                        att.type === "pdf" ? "bg-[#FEF2F2] text-[#DC2626]" : "bg-[#EFF6FF] text-[#2563EB]",
                      )}>
                        {att.type === "pdf" ? <FileText className="h-4 w-4" /> : <Headphones className="h-4 w-4" />}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-[#0F172A]">{att.name}</p>
                        <p className="text-[11px] text-muted-foreground">{att.size} · {att.date}</p>
                      </div>
                    </div>
                    <Download className="h-4 w-4 text-muted-foreground hover:text-[#0F172A]" />
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Internal Notes */}
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-semibold text-[#0F172A]">Internal Notes</CardTitle>
                  <button className="flex items-center gap-1 text-xs text-primary hover:underline">
                    <Plus className="h-3 w-3" /> Add Note
                  </button>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {c.notes.map((note) => (
                  <div key={note.id} className="border border-border rounded-lg p-3">
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className={cn(
                          "text-[10px] px-1.5 py-0 h-4",
                          note.type === "Agent" ? "bg-[#EFF6FF] text-[#2563EB] border-[#2563EB]/20" :
                          note.type === "Supervisor" ? "bg-[#F0FDF4] text-[#16A34A] border-[#16A34A]/20" :
                          "bg-[#F5F3FF] text-[#8B5CF6] border-[#8B5CF6]/20",
                        )}>{note.type}</Badge>
                        <span className="text-xs font-medium text-[#0F172A]">{note.author}</span>
                      </div>
                      <span className="text-[11px] text-muted-foreground">{note.date}</span>
                    </div>
                    <p className="text-xs text-[#475569] leading-relaxed">{note.content}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Right column */}
          <div className="space-y-6">
            {/* Customer Panel */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-[#0F172A]">Customer Profile</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-[#EFF6FF] flex items-center justify-center text-sm font-bold text-[#2563EB]">
                    {c.customer_name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[#0F172A]">{c.customer_name}</p>
                    <p className="text-xs text-muted-foreground">{c.customer.email}</p>
                    <p className="text-xs text-muted-foreground">{c.customer.phone}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { label: "Segment", value: c.customer.segment },
                    { label: "City", value: c.customer.city },
                    { label: "Risk Level", value: c.customer.risk_level, color: c.customer.risk_level === "high" ? "text-[#DC2626]" : "text-[#16A34A]" },
                    { label: "Churn Risk", value: c.customer.churn_risk, color: c.customer.churn_risk === "high" ? "text-[#DC2626]" : "text-[#16A34A]" },
                  ].map((item) => (
                    <div key={item.label} className="bg-[#F8FAFC] rounded-lg p-2.5">
                      <p className="text-[10px] text-muted-foreground">{item.label}</p>
                      <p className={cn("text-xs font-medium mt-0.5 capitalize", (item as any).color ?? "text-[#0F172A]")}>{item.value}</p>
                    </div>
                  ))}
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { label: "Complaints", value: c.customer.total_complaints },
                    { label: "Interactions", value: c.customer.total_interactions },
                    { label: "LTV", value: `$${(c.customer.lifetime_value / 1000).toFixed(1)}K` },
                  ].map((item) => (
                    <div key={item.label} className="text-center bg-[#F8FAFC] rounded-lg p-2.5">
                      <p className="text-lg font-bold text-[#0F172A]">{item.value}</p>
                      <p className="text-[10px] text-muted-foreground">{item.label}</p>
                    </div>
                  ))}
                </div>

                {/* Policies */}
                <div>
                  <p className="text-xs font-semibold text-[#0F172A] mb-2">Active Policies</p>
                  <div className="space-y-2">
                    {c.customer.policies.map((p, i) => (
                      <div key={i} className="flex items-center justify-between border border-border rounded-lg p-2.5">
                        <div>
                          <p className="text-xs font-medium text-[#0F172A]">{p.product}</p>
                          <p className="text-[10px] font-mono text-muted-foreground">{p.policy_number}</p>
                        </div>
                        <span className={cn("text-[10px] font-medium", p.status === "Active" ? "text-[#16A34A]" : "text-[#F59E0B]")}>{p.status}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

              {/* SLA Panel — live countdown */}
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <CardTitle className="text-sm font-semibold text-[#0F172A]">SLA Monitor</CardTitle>
                    </div>
                    <span className={cn("text-xs font-medium capitalize", slaColors[c.sla_risk ?? "within_sla"] ?? "text-[#16A34A]")}>
                      {(c.sla_risk ?? "within_sla").replace(/_/g, " ")}
                    </span>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <SLACountdown deadline={c.resolution_deadline} status={c.sla_risk} />
                  <div className="space-y-2">
                    {[
                      { label: "Received", value: c.received_time ? new Date(c.received_time).toLocaleDateString("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }) : "—" },
                      { label: "Acknowledged", value: c.acknowledged_time ? new Date(c.acknowledged_time).toLocaleDateString("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }) : "Pending" },
                      { label: "Breach Probability", value: c.sla_breach_probability != null ? `${c.sla_breach_probability}%` : "—", color: (c.sla_breach_probability ?? 0) >= 75 ? "text-[#DC2626]" : "text-[#0F172A]" },
                    ].map(item => (
                      <div key={item.label} className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">{item.label}</span>
                        <span className={cn("text-xs font-medium", (item as any).color ?? "text-[#0F172A]")}>{item.value}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>


              {/* FR-008 — Related Complaints */}
              {related.length > 0 && (
                <Card className="border-l-4 border-l-[#F59E0B]">
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-[#F59E0B]" />
                      <CardTitle className="text-sm font-semibold text-[#0F172A]">Related Complaints</CardTitle>
                      <Badge variant="outline" className="text-[10px] px-1.5 py-0 h-4 bg-[#FEF3C7] text-[#B45309] border-[#F59E0B]/30">{related.length} prior</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {related.map(r => (
                      <Link
                        key={r.id}
                        href={`/complaints/${r.id}`}
                        className="flex items-start justify-between p-2.5 rounded-lg border border-border hover:bg-[#F8FAFC] transition-colors group"
                      >
                        <div className="space-y-0.5 min-w-0">
                          <p className="text-xs font-medium text-[#0F172A] truncate group-hover:text-[#0052FF]">{r.title}</p>
                          <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                            <span className="font-mono">{r.complaint_number ?? r.id.toString().slice(0, 8)}</span>
                            {r.theme && <span className="capitalize">{r.theme.replace(/_/g, " ")}</span>}
                          </div>
                        </div>
                        <div className="text-right shrink-0 ml-2">
                          <p className={cn("text-[10px] font-medium", severityColors[r.severity] ?? "text-muted-foreground")}>{r.severity}</p>
                          {r.days_ago != null && <p className="text-[10px] text-muted-foreground">{r.days_ago}d ago</p>}
                        </div>
                      </Link>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Phase 2 AI Panel */}
            {showOverride ? (
              <AIOverridePanel
                complaint={c as any}
                onSubmit={handleOverrideSubmit}
                onCancel={() => setShowOverride(false)}
              />
            ) : (
              <AIIntelligencePanel
                complaint={c as any}
                onOverrideClick={() => setShowOverride(true)}
              />
            )}

            {/* Demo sidebar (shown when Demo Mode is on) */}
            {demoEnabled && (
              <div className="space-y-6">
                <DemoScenarios />
                <CustomerJourneyTimeline />
                <AIDecisionPanel />
                <DemoTimeline />
              </div>
            )}

            {/* Recommended Actions */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-[#0F172A]">Recommended Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {[
                  { key: "assign", icon: User, label: "Assign to Officer", variant: "default", action: handleAssign },
                  { key: "escalate", icon: AlertTriangle, label: "Escalate", variant: "destructive", action: handleEscalate },
                  { key: "merge", icon: Copy, label: "Merge Duplicate", variant: "outline" },
                  { key: "email", icon: Send, label: "Send Email", variant: "outline" },
                  { key: "workflow", icon: GitBranch, label: "Create Workflow", variant: "outline", action: () => router.push("/workflow") },
                  { key: "notify", icon: Bell, label: "Notify Supervisor", variant: "outline" },
                  { key: "resolve", icon: CheckCircle2, label: "Resolve", variant: "success", action: handleResolve },
                  { key: "close", icon: Shield, label: "Close Complaint", variant: "outline", action: handleClose },
                ].map((action) => {
                  const Icon = action.icon;
                  const variantClasses: Record<string, string> = {
                    default: "bg-primary text-primary-foreground hover:bg-primary/90",
                    destructive: "bg-[#DC2626] text-white hover:bg-[#DC2626]/90",
                    outline: "border border-border bg-white hover:bg-accent text-[#0F172A]",
                    success: "bg-[#16A34A] text-white hover:bg-[#16A34A]/90",
                  };
                  const disabled = !action.action || (c.status === "closed" || c.status === "archived") || actionPending !== null;
                  return (
                    <button
                      key={action.key}
                      onClick={action.action}
                      disabled={disabled}
                      className={cn(
                        "w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed",
                        variantClasses[action.variant],
                      )}
                    >
                      <span className="flex items-center gap-2">
                        <Icon className="h-4 w-4" />
                        {actionPending === action.key ? "Working…" : action.label}
                      </span>
                      <ChevronRight className="h-4 w-4 opacity-50" />
                    </button>
                  );
                })}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
      <AICopilot />
    </DashboardShell>
  );
}
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
  FileText, User, ChevronRight, GitBranch, Bell,
  AlertCircle, Calendar, Flag, MessageSquare,
} from "lucide-react";
import Link from "next/link";

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
  new: "bg-[#2563EB]/10 text-[#2563EB]", in_progress: "bg-[#F59E0B]/10 text-[#F59E0B]",
  pending_review: "bg-[#8B5CF6]/10 text-[#8B5CF6]", escalated: "bg-[#DC2626]/10 text-[#DC2626]",
  acknowledged: "bg-[#2563EB]/10 text-[#2563EB]", archived: "bg-[#64748B]/10 text-[#64748B]",
};
const slaColors: Record<string, string> = {
  within_sla: "text-[#16A34A]", at_risk: "text-[#F59E0B]", breached: "text-[#DC2626]",
};
const channelIcons: Record<string, React.ReactNode> = {
  voice: <Phone className="h-4 w-4" />, whatsapp: <MessageCircle className="h-4 w-4" />,
  email: <Mail className="h-4 w-4" />, web_chat: <Globe className="h-4 w-4" />,
  smart_call: <Radio className="h-4 w-4" />, web_form: <ClipboardList className="h-4 w-4" />,
};

export default function ComplaintCaseDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const router = useRouter();
  const { data: c, isLoading } = useComplaintDetail(id);

  if (isLoading) return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in">
        <Skeleton className="h-12 w-48 rounded-xl" />
        <Skeleton className="h-64 w-full rounded-xl" />
        <Skeleton className="h-48 w-full rounded-xl" />
      </div>
      <AICopilot />
    </DashboardShell>
  );

  if (!c) return (
    <DashboardShell>
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <AlertCircle className="h-12 w-12 text-red-400 mb-4" />
        <p className="text-lg font-bold text-[#0F172A]">Case Not Found</p>
        <p className="text-sm text-[#64748B] mt-1">The requested complaint case could not be found.</p>
        <button onClick={() => router.push("/complaint-cases")} className="mt-6 text-sm font-bold text-[#0052FF] hover:underline">&larr; Back to Complaint Cases</button>
      </div>
      <AICopilot />
    </DashboardShell>
  );

  const customerName = (c as any).customer_name || (c as any).customer?.name || "Unknown";
  const caseId = c.complaint_number || `CASE-${id.slice(0, 8)}`;
  const workflow = { status: c.status, assigned_team: c.assigned_queue, sla_status: (c as any).sla_status };

  return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-sm text-[#64748B]">
          <button onClick={() => router.push("/complaint-cases")} className="hover:text-[#0F172A] transition-colors">Complaint Cases</button>
          <ChevronRight className="h-3.5 w-3.5" />
          <span className="text-[#0F172A] font-medium">{caseId}</span>
        </div>

        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-extrabold text-[#0F172A]">{caseId}</h1>
              <Badge className={cn("capitalize", statusColors[c.status] || "bg-[#64748B]/10 text-[#64748B]")}>{c.status?.replace(/_/g, " ")}</Badge>
            </div>
            <p className="text-sm text-[#64748B] mt-1">{c.title}</p>
          </div>
          <div className="flex items-center gap-2">
            {c.insurance_line && <InsuranceBadge line={c.insurance_line} />}
          </div>
        </div>

        {/* Main grid */}
        <div className="grid grid-cols-[1fr_360px] gap-6">
          {/* Left column */}
          <div className="space-y-6">
            {/* Description */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-[#0F172A]">Case Description</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-[#475569] leading-relaxed">{c.description || "No description provided."}</p>
              </CardContent>
            </Card>

            {/* AI Analysis */}
            {c.ai_summary && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-semibold text-[#0F172A] flex items-center gap-2">
                    <Brain className="h-4 w-4 text-[#0052FF]" /> AI Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="bg-blue-50/50 rounded-xl p-4 text-sm text-[#475569] leading-relaxed">{c.ai_summary}</div>
                  {(c as any).ai_decision && (
                    <div className="mt-3 flex items-center gap-2">
                      <Shield className="h-4 w-4 text-[#0052FF]" />
                      <span className="text-xs font-bold text-[#0F172A]">AI Decision:</span>
                      <span className="text-xs text-[#475569]">{(c as any).ai_decision}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Timeline */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-[#0F172A] flex items-center gap-2">
                  <Clock className="h-4 w-4 text-[#0052FF]" /> Timeline
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-1 before:bottom-1 before:w-0.5 before:bg-[#E2E8F0]">
                  {(c as any).timeline_events?.slice(0, 6).map((event: any, idx: number) => (
                    <div key={idx} className="relative">
                      <div className={`absolute -left-6 top-0.5 h-3 w-3 rounded-full border-2 bg-white ${
                        event.type === "resolved" || event.type === "closed" ? "border-emerald-500" :
                        event.type === "escalated" ? "border-red-500" : "border-blue-500"
                      }`} />
                      <p className="text-xs font-bold text-[#0F172A]">{event.label}</p>
                      {event.description && <p className="text-[11px] text-[#64748B]">{event.description}</p>}
                      <p className="text-[10px] text-[#94A3B8] mt-0.5">{event.date ? new Date(event.date).toLocaleDateString("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }) : ""}</p>
                    </div>
                  )) || (
                    <p className="text-sm text-[#94A3B8]">No timeline events available.</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Internal Notes */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-[#0F172A] flex items-center gap-2">
                  <ClipboardList className="h-4 w-4 text-[#0052FF]" /> Internal Notes
                </CardTitle>
              </CardHeader>
              <CardContent>
                  {(c as any).notes && (c as any).notes.length > 0 ? (
                  <div className="space-y-3">
                    {(c as any).notes?.map((note: any, idx: number) => (
                      <div key={idx} className="p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                        <p className="text-xs text-[#475569]">{note.content || note.text}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <span className="text-[10px] text-[#94A3B8]">{note.author || "Agent"}</span>
                          <span className="text-[10px] text-[#94A3B8]">·</span>
                          <span className="text-[10px] text-[#94A3B8]">{note.created_at ? new Date(note.created_at).toLocaleDateString("en-GB", { day: "2-digit", month: "short" }) : ""}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-[#94A3B8]">No internal notes yet.</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right column — sidebar */}
          <div className="space-y-4">
            {/* Customer */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-[#0F172A] flex items-center gap-2">
                  <User className="h-4 w-4 text-[#0052FF]" /> Customer
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Link href={`/customers?id=${c.customer_id}`} className="flex items-center gap-3 p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] hover:border-[#0052FF] transition-colors">
                  <div className="h-8 w-8 rounded-full bg-[#EFF6FF] flex items-center justify-center text-[#0052FF] font-bold text-xs">
                    {customerName.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-bold text-[#0F172A]">{customerName}</p>
                    <p className="text-[10px] text-[#64748B]">{c.customer?.email || ""}</p>
                  </div>
                </Link>
              </CardContent>
            </Card>

            {/* Case Details */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-[#0F172A]">Case Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-[#64748B]">Priority</span>
                  <Badge className={cn("capitalize", priorityColors[c.priority] || "bg-[#64748B]/10 text-[#64748B]")}>{c.priority || "—"}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-[#64748B]">Severity</span>
                  <Badge className={cn("capitalize", severityColors[c.severity] || "bg-[#64748B]/10 text-[#64748B]")}>{c.severity || "—"}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-[#64748B]">Sentiment</span>
                  <span className="text-xs font-bold capitalize">{c.sentiment || "—"}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-[#64748B]">Theme</span>
                  <span className="text-xs font-bold capitalize">{c.theme || c.category || "—"}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-[#64748B]">Source</span>
                  <span className="text-xs font-bold capitalize flex items-center gap-1">
                    {channelIcons[c.source]}{c.source?.replace(/_/g, " ") || "—"}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-[#64748B]">Complaint ID</span>
                  <span className="text-xs font-mono font-bold">{c.complaint_number || id.slice(0, 8)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-[#64748B]">Filed</span>
                  <span className="text-xs font-mono">{c.created_at ? new Date(c.created_at).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }) : "—"}</span>
                </div>
              </CardContent>
            </Card>

            {/* Assignment & SLA */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-[#0F172A] flex items-center gap-2">
                  <GitBranch className="h-4 w-4 text-[#0052FF]" /> Workflow
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-[#64748B]">Status</span>
                  <Badge className={cn("capitalize", statusColors[workflow.status] || "bg-[#64748B]/10 text-[#64748B]")}>{workflow.status?.replace(/_/g, " ") || "—"}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-[#64748B]">Assigned To</span>
                  <span className="text-xs font-bold">{c.assigned_agent_name || c.assigned_queue || "Unassigned"}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-[#64748B]">Department</span>
                  <span className="text-xs font-bold capitalize">{c.assigned_queue || "—"}</span>
                </div>
                <div className="pt-2 border-t border-[#E2E8F0]">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs text-[#64748B]">SLA Status</span>
                    <span className={cn("text-xs font-bold", slaColors[workflow.sla_status] || "text-[#64748B]")}>
                      {(workflow.sla_status || "unknown").replace(/_/g, " ")}
                    </span>
                  </div>
                  {(c as any).sla_deadline && (
                    <p className="text-[10px] text-[#94A3B8]">Deadline: {new Date((c as any).sla_deadline).toLocaleDateString("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}</p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Escalation */}
            {(c as any).escalation_level && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-semibold text-[#0F172A] flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-[#DC2626]" /> Escalation
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-[#64748B]">Level:</span>
                    <span className="text-xs font-bold capitalize">{(c as any).escalation_level.replace(/_/g, " ")}</span>
                  </div>
                  {(c as any).escalation_reason && <p className="text-xs text-[#64748B] mt-1">{(c as any).escalation_reason}</p>}
                </CardContent>
              </Card>
            )}

            {/* Communications */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold text-[#0F172A] flex items-center gap-2">
                  <MessageSquare className="h-4 w-4 text-[#0052FF]" /> Communications
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Link href={`/interactions/${c.interaction_id}`} className="flex items-center justify-between p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] hover:border-[#0052FF] transition-colors">
                  <span className="text-xs font-bold text-[#0F172A]">View Interaction</span>
                  <ChevronRight className="h-3.5 w-3.5 text-[#94A3B8]" />
                </Link>
                <Link href={`/customer/communication/chat?complaint_id=${id}`} className="flex items-center justify-between p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0] hover:border-[#0052FF] transition-colors">
                  <span className="text-xs font-bold text-[#0F172A]">Continue Conversation</span>
                  <ChevronRight className="h-3.5 w-3.5 text-[#94A3B8]" />
                </Link>
              </CardContent>
            </Card>

            {/* Recommended Resolution */}
            {(c as any).recommended_resolution && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-semibold text-[#0F172A] flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-[#16A34A]" /> Recommended Resolution
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-[#475569]">{(c as any).recommended_resolution}</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
      <AICopilot />
    </DashboardShell>
  );
}

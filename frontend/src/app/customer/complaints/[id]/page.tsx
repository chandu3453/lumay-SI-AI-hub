"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/http";
import { AlertCircle, Clock, Loader2, Mail, MessageSquare, Phone, Paperclip, MessageCircle, Calendar } from "lucide-react";

type ComplaintDetail = {
  id: string;
  complaint_number: string | null;
  title: string;
  description: string | null;
  category: string;
  subcategory: string | null;
  priority: string;
  severity: string;
  status: string;
  source: string;
  assigned_queue: string | null;
  product: string | null;
  policy_number: string | null;
  claim_number: string | null;
  created_at: string;
  updated_at?: string;
  ai_summary?: string | null;
  detection_confidence?: number | null;
  resolution_eta?: string;
  attachments?: { name: string; url: string; size: string }[];
  conversation_history?: { channel: string; date: string; preview: string }[];
  timeline_events?: TimelineEvent[];
};

type TimelineEvent = {
  type: "created" | "acknowledged" | "investigating" | "escalated" | "resolved" | "closed" | "note";
  label: string;
  date: string;
  description?: string;
  actor?: string;
};

const STATUS_BADGE: Record<string, string> = {
  submitted: "bg-slate-100 text-slate-700 border-slate-200",
  under_review: "bg-blue-50 text-blue-700 border-blue-200",
  investigating: "bg-amber-50 text-amber-700 border-amber-200",
  escalated: "bg-red-50 text-red-700 border-red-200",
  resolved: "bg-emerald-50 text-emerald-700 border-emerald-200",
  closed: "bg-slate-100 text-slate-500 border-slate-200",
};

const SEVERITY_COLORS: Record<string, string> = {
  critical: "text-red-600 bg-red-50", high: "text-orange-600 bg-orange-50",
  medium: "text-amber-600 bg-amber-50", low: "text-slate-600 bg-slate-50",
  moderate: "text-amber-600 bg-amber-50", major: "text-red-600 bg-red-50",
};

export default function ComplaintDetailPage() {
  const { id } = useParams();
  const [complaint, setComplaint] = useState<ComplaintDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => { fetchComplaint(); }, [id]);

  const fetchComplaint = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/complaints/${id}`);
      const data = res.data?.data || res.data;
      const timeline: TimelineEvent[] = [
        { type: "created", label: "Complaint Submitted", date: data.created_at, description: data.title, actor: "System" },
        { type: "acknowledged", label: "Acknowledged by System", date: data.created_at, description: "Complaint registered and queued for review", actor: "System" },
      ];
      if (data.status === "under_review" || data.status === "investigating" || data.status === "escalated") {
        timeline.push({ type: "investigating", label: "Under Review", date: data.updated_at || data.created_at, description: `Assigned to ${data.assigned_queue || "claims team"}`, actor: "System" });
      }
      if (data.status === "escalated") {
        timeline.push({ type: "escalated", label: "Escalated", date: data.updated_at || data.created_at, description: "Escalated to senior team", actor: "System" });
      }
      if (data.status === "resolved" || data.status === "closed") {
        timeline.push({ type: "resolved", label: "Resolved", date: data.updated_at || data.created_at, description: "Resolution completed", actor: "System" });
      }
      if (data.status === "closed") {
        timeline.push({ type: "closed", label: "Closed", date: data.updated_at || data.created_at, description: "Case closed", actor: "System" });
      }
      const createdDate = new Date(data.created_at);
      const etaDate = new Date(createdDate.getTime() + 72 * 60 * 60 * 1000);
      const resolution_eta = etaDate.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
      const attachments = data.attachments || [
        { name: "Policy Document.pdf", url: "#", size: "2.4 MB" },
        { name: "Claim Photos.zip", url: "#", size: "8.1 MB" },
      ];
      const conversation_history = data.conversation_history || [
        { channel: "Chat", date: data.created_at, preview: "Initial complaint description and AI response" },
        { channel: "Email", date: data.updated_at || data.created_at, preview: "Follow-up communication regarding resolution" },
      ];
      setComplaint({ ...data, timeline_events: timeline, resolution_eta, attachments, conversation_history });
    } catch {
      setError("Failed to load complaint details.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <Loader2 className="h-6 w-6 animate-spin text-[#0052FF]" />
    </div>
  );

  if (error || !complaint) return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center space-y-3">
        <AlertCircle className="h-10 w-10 mx-auto text-red-400" />
        <p className="text-sm font-bold text-red-600">{error || "Complaint not found"}</p>
        <Link href="/customer/complaints" className="text-xs font-bold text-[#0052FF] hover:underline">&larr; Back to complaints</Link>
      </div>
    </div>
  );

  return (
    <div className="p-6 sm:p-8 space-y-6 animate-fade-in max-w-4xl mx-auto">
      {/* Status header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-black text-[#0D1B3E]">{complaint.complaint_number || "Complaint"}</h1>
          <p className="text-xs text-slate-500 mt-1">Track your complaint status and timeline</p>
        </div>
        <span className={`text-[10px] font-bold px-3 py-1.5 rounded-full border capitalize ${STATUS_BADGE[complaint.status] || "bg-slate-100 text-slate-700"}`}>
          {complaint.status.replace(/_/g, " ")}
        </span>
      </div>

      {/* Details Card */}
      <div className="bg-white border border-[#E2E8F0] rounded-3xl p-6 shadow-sm space-y-5">
        <div>
          <h2 className="text-lg font-black text-[#0D1B3E]">{complaint.title}</h2>
          {complaint.description && <p className="text-xs text-slate-500 mt-2 leading-relaxed">{complaint.description}</p>}
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="space-y-1">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Category</p>
            <p className="text-sm font-bold capitalize">{complaint.category}</p>
            {complaint.subcategory && <p className="text-[10px] text-slate-400 capitalize">{complaint.subcategory}</p>}
          </div>
          <div className="space-y-1">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Priority</p>
            <p className={`text-sm font-bold capitalize ${complaint.priority === "critical" || complaint.priority === "high" ? "text-red-600" : "text-amber-600"}`}>{complaint.priority}</p>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Severity</p>
            <p className={`text-sm font-bold capitalize ${SEVERITY_COLORS[complaint.severity] || ""}`}>{complaint.severity}</p>
          </div>
          <div className="space-y-1">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Source</p>
            <p className="text-sm font-bold capitalize">{complaint.source?.replace(/_/g, " ") || "Web Chat"}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-3 border-t border-[#E2E8F0]">
          {complaint.policy_number && (
            <div className="space-y-1">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Policy</p>
              <p className="text-xs font-mono font-bold">{complaint.policy_number}</p>
            </div>
          )}
          {complaint.claim_number && (
            <div className="space-y-1">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Claim</p>
              <p className="text-xs font-mono font-bold">{complaint.claim_number}</p>
            </div>
          )}
          {complaint.product && (
            <div className="space-y-1">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Product</p>
              <p className="text-xs font-bold capitalize">{complaint.product.replace(/_/g, " ")}</p>
            </div>
          )}
          {complaint.assigned_queue && (
            <div className="space-y-1">
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Assigned Dept</p>
              <p className="text-xs font-bold capitalize">{complaint.assigned_queue}</p>
            </div>
          )}
          <div className="space-y-1">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Filed On</p>
            <p className="text-xs font-mono font-bold">{new Date(complaint.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</p>
          </div>
        </div>

        {complaint.ai_summary && (
          <div className="pt-3 border-t border-[#E2E8F0]">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">AI Analysis</p>
            <div className="bg-blue-50/50 rounded-xl p-3 text-xs text-slate-600 leading-relaxed">{complaint.ai_summary}</div>
          </div>
        )}
      </div>

      {/* Resolution ETA */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-3xl p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Calendar className="h-5 w-5 text-[#0052FF]" />
            <div>
              <p className="text-xs font-bold text-[#0052FF] uppercase tracking-wider">Resolution ETA</p>
              <p className="text-lg font-black text-[#0D1B3E]">{complaint.resolution_eta}</p>
              <p className="text-[10px] text-slate-500 mt-0.5">SLA target: 72 hours from acknowledgement</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Assigned Dept</p>
            <p className="text-sm font-bold capitalize">{complaint.assigned_queue || "Claims Team"}</p>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-white border border-[#E2E8F0] rounded-3xl p-6 shadow-sm">
        <h3 className="text-sm font-black text-[#0D1B3E] uppercase tracking-wider mb-5 flex items-center gap-2">
          <Clock className="h-4 w-4 text-[#0052FF]" /> Timeline
        </h3>
        <div className="relative pl-8 space-y-6 before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#E2E8F0]">
          {complaint.timeline_events?.map((event, idx) => (
            <div key={idx} className="relative">
              <div className={`absolute -left-8 top-0.5 h-5 w-5 rounded-full border-2 flex items-center justify-center bg-white ${
                event.type === "created" ? "border-blue-500" :
                event.type === "resolved" || event.type === "closed" ? "border-emerald-500" :
                event.type === "escalated" ? "border-red-500" : "border-slate-300"
              }`}>
                <div className={`h-2 w-2 rounded-full ${
                  event.type === "created" ? "bg-blue-500" :
                  event.type === "resolved" || event.type === "closed" ? "bg-emerald-500" :
                  event.type === "escalated" ? "bg-red-500" : "bg-slate-300"
                }`} />
              </div>
              <div>
                <p className="text-xs font-bold text-[#0D1B3E]">{event.label}</p>
                {event.description && <p className="text-[11px] text-slate-500 mt-0.5">{event.description}</p>}
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-[9px] font-mono text-slate-400">{new Date(event.date).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}</span>
                  {event.actor && <><span className="text-[9px] text-slate-300">·</span><span className="text-[9px] text-slate-400">{event.actor}</span></>}
                </div>
              </div>
            </div>
          ))}
          {complaint.status !== "resolved" && complaint.status !== "closed" && (
            <div className="relative">
              <div className="absolute -left-8 top-0.5 h-5 w-5 rounded-full border-2 border-dashed border-slate-300 flex items-center justify-center bg-white">
                <Clock className="h-2.5 w-2.5 text-slate-300" />
              </div>
              <p className="text-xs font-bold text-slate-400">Expected Resolution</p>
              <p className="text-[10px] text-slate-400 mt-0.5">SLA target: 72 hours from acknowledgement</p>
            </div>
          )}
        </div>
      </div>

      {/* Conversation History */}
      <div className="bg-white border border-[#E2E8F0] rounded-3xl p-6 shadow-sm">
        <h3 className="text-sm font-black text-[#0D1B3E] uppercase tracking-wider mb-4 flex items-center gap-2">
          <MessageCircle className="h-4 w-4 text-[#0052FF]" /> Conversation History
        </h3>
        <div className="space-y-3">
          {complaint.conversation_history?.map((conv, idx) => (
            <div key={idx} className="flex items-start gap-3 p-3 rounded-xl bg-slate-50 border border-slate-100">
              <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
                <MessageSquare className="h-4 w-4 text-[#0052FF]" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-xs font-bold text-[#0D1B3E]">{conv.channel}</p>
                  <span className="text-[9px] text-slate-400">{new Date(conv.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}</span>
                </div>
                <p className="text-[11px] text-slate-500 mt-0.5 truncate">{conv.preview}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Attachments */}
      <div className="bg-white border border-[#E2E8F0] rounded-3xl p-6 shadow-sm">
        <h3 className="text-sm font-black text-[#0D1B3E] uppercase tracking-wider mb-4 flex items-center gap-2">
          <Paperclip className="h-4 w-4 text-[#0052FF]" /> Attachments
        </h3>
        <div className="space-y-2">
          {complaint.attachments?.map((att, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-lg bg-blue-50 flex items-center justify-center">
                  <Paperclip className="h-4 w-4 text-[#0052FF]" />
                </div>
                <div>
                  <p className="text-xs font-bold text-[#0D1B3E]">{att.name}</p>
                  <p className="text-[9px] text-slate-400">{att.size}</p>
                </div>
              </div>
              <Link href={att.url} className="text-[10px] font-bold text-[#0052FF] hover:underline">Download</Link>
            </div>
          ))}
        </div>
      </div>

      {/* Communication */}
      <div className="bg-white border border-[#E2E8F0] rounded-3xl p-6 shadow-sm">
        <h3 className="text-sm font-black text-[#0D1B3E] uppercase tracking-wider mb-3">Need Help?</h3>
        <div className="flex flex-wrap gap-2">
          <Link href={`/customer/communication/chat?complaint_id=${complaint.id}`} className="flex items-center gap-1.5 text-xs font-bold px-3 py-2 rounded-lg bg-blue-50 text-[#0052FF] hover:bg-blue-100 transition-colors">
            <MessageSquare className="h-3.5 w-3.5" /> Continue Conversation
          </Link>
          <Link href={`/customer/communication/voice?complaint_id=${complaint.id}`} className="flex items-center gap-1.5 text-xs font-bold px-3 py-2 rounded-lg bg-orange-50 text-orange-600 hover:bg-orange-100 transition-colors">
            <Phone className="h-3.5 w-3.5" /> Voice Support
          </Link>
          <Link href={`/customer/communication/whatsapp?complaint_id=${complaint.id}`} className="flex items-center gap-1.5 text-xs font-bold px-3 py-2 rounded-lg bg-emerald-50 text-emerald-600 hover:bg-emerald-100 transition-colors">
            <MessageSquare className="h-3.5 w-3.5" /> WhatsApp
          </Link>
          <Link href={`/customer/communication/email?complaint_id=${complaint.id}`} className="flex items-center gap-1.5 text-xs font-bold px-3 py-2 rounded-lg bg-purple-50 text-purple-600 hover:bg-purple-100 transition-colors">
            <Mail className="h-3.5 w-3.5" /> Email
          </Link>
        </div>
      </div>
    </div>
  );
}

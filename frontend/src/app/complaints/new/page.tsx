"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { complaintsService } from "@/services/complaints.service";
import {
  ArrowLeft, Send, Bot, FileText, User, Phone, Mail, MessageCircle,
  Globe, Radio, ClipboardList, Shield, AlertTriangle, Info, CheckCircle2, Loader2,
} from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/cn";

const CHANNELS = [
  { value: "voice", label: "Voice Call", icon: <Phone className="h-4 w-4" /> },
  { value: "whatsapp", label: "WhatsApp", icon: <MessageCircle className="h-4 w-4" /> },
  { value: "email", label: "Email", icon: <Mail className="h-4 w-4" /> },
  { value: "web_chat", label: "Web Chat", icon: <Globe className="h-4 w-4" /> },
  { value: "smart_call", label: "SMART CALL", icon: <Radio className="h-4 w-4" /> },
  { value: "agent_entered", label: "Agent Entered", icon: <ClipboardList className="h-4 w-4" /> },
];

const PRODUCTS = [
  { value: "motor", label: "Motor Insurance" },
  { value: "medical", label: "Medical Insurance" },
  { value: "travel", label: "Travel Insurance" },
  { value: "home", label: "Home Insurance" },
  { value: "life", label: "Life Insurance" },
  { value: "business", label: "Business Insurance" },
  { value: "renewals", label: "Renewals" },
  { value: "claims", label: "Claims" },
  { value: "payments", label: "Payments" },
  { value: "provider_garage", label: "Provider / Garage" },
  { value: "general", label: "General" },
];

const CATEGORIES = [
  { value: "billing", label: "Billing" },
  { value: "claims", label: "Claims" },
  { value: "policy", label: "Policy" },
  { value: "service", label: "Service" },
  { value: "technical", label: "Technical" },
  { value: "general", label: "General" },
];

const LANGUAGES = [
  { value: "en", label: "English" },
  { value: "ar", label: "Arabic (عربي)" },
  { value: "mixed", label: "Mixed (AR + EN)" },
];

type FormState = {
  channel: string;
  product: string;
  category: string;
  language: string;
  policy_number: string;
  claim_number: string;
  customer_id: string;
  agent_name: string;
  description: string;
  customer_requested_outcome: string;
  regulatory_flag: boolean;
};

const DEFAULT: FormState = {
  channel: "agent_entered",
  product: "general",
  category: "general",
  language: "en",
  policy_number: "",
  claim_number: "",
  customer_id: "",
  agent_name: "",
  description: "",
  customer_requested_outcome: "",
  regulatory_flag: false,
};

function FieldGroup({ label, children, required, hint }: {
  label: string; children: React.ReactNode; required?: boolean; hint?: string;
}) {
  return (
    <div className="space-y-1.5">
      <label className="block text-sm font-medium text-[#0F172A]">
        {label}{required && <span className="ml-1 text-[#DC2626]">*</span>}
      </label>
      {children}
      {hint && <p className="text-xs text-[#64748B]">{hint}</p>}
    </div>
  );
}

export default function NewComplaintPage() {
  const router = useRouter();
  const [form, setForm] = useState<FormState>(DEFAULT);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{ complaint_number: string | null; id: string } | null>(null);

  function set(key: keyof FormState, value: string | boolean) {
    setForm(prev => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.description.trim() || form.description.trim().length < 10) {
      setError("Please enter a complaint description of at least 10 characters.");
      return;
    }
    setSubmitting(true);
    setError(null);

    try {
      const res = await complaintsService.ingest({
        channel: form.channel,
        product: form.product || undefined,
        policy_number: form.policy_number || undefined,
        claim_number: form.claim_number || undefined,
        customer_id: form.customer_id || undefined,
        transcript: form.description,
        language: form.language,
      });
      const data = (res as any)?.data?.data ?? (res as any)?.data;
      setSuccess({
        complaint_number: data?.complaint_number ?? null,
        id: data?.complaint_id ?? "",
      });
    } catch (err: any) {
      setError(err?.message ?? "Failed to create complaint. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (success) {
    return (
      <DashboardShell>
        <div className="max-w-2xl mx-auto flex flex-col items-center justify-center min-h-[60vh] gap-6 animate-fade-in">
          <div className="w-16 h-16 rounded-full bg-[#16A34A]/10 flex items-center justify-center">
            <CheckCircle2 className="h-8 w-8 text-[#16A34A]" />
          </div>
          <div className="text-center space-y-2">
            <h2 className="text-xl font-bold text-[#0F172A]">Complaint Created</h2>
            {success.complaint_number && (
              <p className="text-[#0052FF] font-mono font-semibold text-lg">{success.complaint_number}</p>
            )}
            <p className="text-[#64748B] text-sm max-w-sm">
              AI analysis has been queued. Intelligence fields will be populated within seconds.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => success.id && router.push(`/complaints/${success.id}`)}
              className="px-4 py-2 bg-[#0052FF] text-white rounded-lg text-sm font-medium hover:bg-[#0040CC] transition-colors"
            >
              View Complaint
            </button>
            <button
              onClick={() => { setSuccess(null); setForm(DEFAULT); }}
              className="px-4 py-2 border border-border rounded-lg text-sm font-medium text-[#64748B] hover:bg-muted transition-colors"
            >
              Create Another
            </button>
            <Link
              href="/complaints"
              className="px-4 py-2 border border-border rounded-lg text-sm font-medium text-[#64748B] hover:bg-muted transition-colors"
            >
              Back to List
            </Link>
          </div>
        </div>
        <AICopilot />
      </DashboardShell>
    );
  }

  return (
    <DashboardShell>
      <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
        {/* Header */}
        <div className="space-y-2">
          <Link href="/complaints" className="inline-flex items-center gap-1.5 text-sm text-[#64748B] hover:text-[#0F172A] transition-colors">
            <ArrowLeft className="h-4 w-4" /> Back to Complaints
          </Link>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-[#0F172A]">New Complaint</h1>
              <p className="text-sm text-[#64748B] mt-1">
                FR-001: Record a customer complaint across any channel. AI analysis runs automatically.
              </p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-[#0052FF]/5 border border-[#0052FF]/20 rounded-lg">
              <Bot className="h-4 w-4 text-[#0052FF]" />
              <span className="text-xs font-medium text-[#0052FF]">AI will analyze on submit</span>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Section: Channel & Product */}
          <div className="bg-white rounded-xl border border-border p-6 space-y-5">
            <h2 className="text-sm font-semibold text-[#0F172A] uppercase tracking-wider flex items-center gap-2">
              <Phone className="h-4 w-4 text-[#0052FF]" /> Channel & Product
            </h2>

            <FieldGroup label="Channel" required hint="How did the customer reach us?">
              <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
                {CHANNELS.map(ch => (
                  <button
                    key={ch.value}
                    type="button"
                    onClick={() => set("channel", ch.value)}
                    className={cn(
                      "flex flex-col items-center gap-1.5 p-3 rounded-lg border text-xs font-medium transition-all",
                      form.channel === ch.value
                        ? "bg-[#0052FF]/5 border-[#0052FF] text-[#0052FF]"
                        : "border-border text-[#64748B] hover:border-[#94A3B8]"
                    )}
                  >
                    {ch.icon}
                    <span className="text-[10px] text-center leading-tight">{ch.label}</span>
                  </button>
                ))}
              </div>
            </FieldGroup>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <FieldGroup label="Insurance Product">
                <select
                  value={form.product}
                  onChange={e => set("product", e.target.value)}
                  className="w-full border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#0052FF]/30"
                >
                  {PRODUCTS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
                </select>
              </FieldGroup>
              <FieldGroup label="Language">
                <select
                  value={form.language}
                  onChange={e => set("language", e.target.value)}
                  className="w-full border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#0052FF]/30"
                >
                  {LANGUAGES.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
                </select>
              </FieldGroup>
            </div>
          </div>

          {/* Section: Policy & Claim References */}
          <div className="bg-white rounded-xl border border-border p-6 space-y-5">
            <h2 className="text-sm font-semibold text-[#0F172A] uppercase tracking-wider flex items-center gap-2">
              <FileText className="h-4 w-4 text-[#0052FF]" /> Policy & Claim References
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
              <FieldGroup label="Policy Number">
                <input
                  type="text"
                  value={form.policy_number}
                  onChange={e => set("policy_number", e.target.value)}
                  placeholder="e.g. POL-2025-00123"
                  className="w-full border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#0052FF]/30"
                />
              </FieldGroup>
              <FieldGroup label="Claim Number">
                <input
                  type="text"
                  value={form.claim_number}
                  onChange={e => set("claim_number", e.target.value)}
                  placeholder="e.g. CLM-2025-00456"
                  className="w-full border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#0052FF]/30"
                />
              </FieldGroup>
              <FieldGroup label="Customer ID">
                <input
                  type="text"
                  value={form.customer_id}
                  onChange={e => set("customer_id", e.target.value)}
                  placeholder="UUID or customer number"
                  className="w-full border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#0052FF]/30"
                />
              </FieldGroup>
            </div>
          </div>

          {/* Section: Complaint Details */}
          <div className="bg-white rounded-xl border border-border p-6 space-y-5">
            <h2 className="text-sm font-semibold text-[#0F172A] uppercase tracking-wider flex items-center gap-2">
              <ClipboardList className="h-4 w-4 text-[#0052FF]" /> Complaint Details
            </h2>

            <FieldGroup
              label="Complaint Description / Transcript"
              required
              hint="Paste the full transcript, email body, or describe the customer complaint in detail. AI will analyze this text."
            >
              <textarea
                value={form.description}
                onChange={e => set("description", e.target.value)}
                rows={8}
                placeholder={form.language === "ar"
                  ? "اكتب وصف الشكوى هنا... (يمكن كتابة النص باللغة العربية أو الإنجليزية)"
                  : "Paste transcript or describe the complaint in detail...\n\nExample: The customer called regarding their motor insurance claim submitted on 10th May. They are frustrated that the claim (CLM-2025-00456) has not been processed after 2 weeks. The garage has not been approved yet..."}
                dir={form.language === "ar" ? "rtl" : "ltr"}
                className="w-full border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#0052FF]/30 resize-none font-mono"
              />
            </FieldGroup>

            <FieldGroup
              label="Customer Requested Outcome"
              hint="FR-010: What does the customer expect to happen? (optional but recommended)"
            >
              <input
                type="text"
                value={form.customer_requested_outcome}
                onChange={e => set("customer_requested_outcome", e.target.value)}
                placeholder="e.g. Wants claim processed within 48 hours and garage approval issued today"
                className="w-full border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#0052FF]/30"
              />
            </FieldGroup>

            {/* Regulatory Flag */}
            <div className="flex items-start gap-3 p-4 bg-[#FEF2F2] border border-[#DC2626]/20 rounded-lg">
              <input
                id="regulatory_flag"
                type="checkbox"
                checked={form.regulatory_flag}
                onChange={e => set("regulatory_flag", e.target.checked)}
                className="mt-0.5 h-4 w-4 rounded border-[#DC2626] text-[#DC2626] focus:ring-[#DC2626]"
              />
              <div>
                <label htmlFor="regulatory_flag" className="text-sm font-medium text-[#DC2626] cursor-pointer flex items-center gap-1.5">
                  <Shield className="h-4 w-4" /> Regulatory / Compliance Flag
                </label>
                <p className="text-xs text-[#64748B] mt-0.5">
                  FR-020: Check if this complaint involves potential regulatory or legal implications that require senior review.
                </p>
              </div>
            </div>
          </div>

          {/* AI Notice */}
          <div className="flex items-start gap-3 p-4 bg-[#0052FF]/5 border border-[#0052FF]/20 rounded-xl">
            <Info className="h-4 w-4 text-[#0052FF] mt-0.5 shrink-0" />
            <div className="text-sm text-[#334155] space-y-1">
              <p className="font-medium text-[#0052FF]">AI Analysis will run automatically</p>
              <p className="text-xs text-[#64748B]">
                The system will detect complaint type, classify sentiment and theme, assess escalation risk,
                check for repeat complaints, calculate SLA deadlines, and identify the root cause — all within seconds of submission.
              </p>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 bg-[#FEF2F2] border border-[#DC2626]/30 rounded-lg text-sm text-[#DC2626]">
              <AlertTriangle className="h-4 w-4 shrink-0" /> {error}
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end gap-3">
            <Link
              href="/complaints"
              className="px-4 py-2 border border-border rounded-lg text-sm font-medium text-[#64748B] hover:bg-muted transition-colors"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={submitting || !form.description.trim()}
              className="flex items-center gap-2 px-5 py-2 bg-[#0052FF] text-white rounded-lg text-sm font-medium hover:bg-[#0040CC] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {submitting ? (
                <><Loader2 className="h-4 w-4 animate-spin" /> Creating...</>
              ) : (
                <><Send className="h-4 w-4" /> Submit Complaint</>
              )}
            </button>
          </div>
        </form>
      </div>
      <AICopilot />
    </DashboardShell>
  );
}

"use client";

import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Phone, MessageCircle, Mail, MessageSquare, HelpCircle } from "lucide-react";
import { ROUTES } from "@/lib/constants";
import { complaintsService } from "@/services/complaints.service";

type RecentComplaint = {
  id: string;
  complaint_number: string | null;
  title: string;
  channel: string | null;
  theme: string | null;
  severity: string;
  sla_risk: string | null;
  created_at: string;
};

const CHANNEL_ICONS: Record<string, React.ReactNode> = {
  voice: <Phone className="h-4.5 w-4.5 text-[#10B981]" />,
  phone: <Phone className="h-4.5 w-4.5 text-[#10B981]" />,
  whatsapp: <MessageCircle className="h-4.5 w-4.5 text-[#10B981]" />,
  web_chat: <MessageSquare className="h-4.5 w-4.5 text-[#2563EB]" />,
  email: <Mail className="h-4.5 w-4.5 text-[#2563EB]" />,
};

function severityBadge(severity: string) {
  const tone = severity === "high" || severity === "critical"
    ? "bg-red-50 border-red-100 text-red-600"
    : severity === "medium"
    ? "bg-amber-50 border-amber-100 text-amber-600"
    : "bg-green-50 border-green-100 text-green-600";
  return <span className={`rounded-lg border px-2 py-1 text-[11px] font-bold capitalize ${tone}`}>{severity}</span>;
}

function slaBadge(slaRisk: string | null) {
  if (!slaRisk) return <span className="text-[11px] text-slate-400">—</span>;
  const tone = slaRisk === "breached"
    ? "bg-red-50 border-red-100 text-red-600"
    : slaRisk === "at_risk"
    ? "bg-amber-50 border-amber-100 text-amber-600"
    : "bg-green-50 border-green-100 text-green-600";
  return <span className={`rounded-lg border px-2 py-1 text-[11px] font-bold capitalize ${tone}`}>{slaRisk.replace("_", " ")}</span>;
}

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function useRecentComplaints() {
  return useQuery({
    queryKey: ["dashboard", "recent-complaints"],
    queryFn: async () => {
      const res = await complaintsService.list({ page: 1, page_size: 5 });
      return (res.data.data ?? []) as unknown as RecentComplaint[];
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function RecentComplaintsTable() {
  const router = useRouter();
  const { data: complaints = [], isLoading } = useRecentComplaints();

  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-white shadow-sm overflow-hidden flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-5 border-b border-[#E2E8F0]">
        <h3 className="text-sm font-bold text-[#0F172A] tracking-tight">Recent Complaints</h3>
        <button
          onClick={() => router.push(ROUTES.COMPLAINTS)}
          className="text-xs font-bold text-[#0052FF] hover:underline"
        >
          View all
        </button>
      </div>

      {/* Table container */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-[#E2E8F0] bg-[#F8FAFC]">
              {["ID", "Title", "Channel", "Theme", "Severity", "SLA Risk", "Time"].map((th) => (
                <th key={th} className="text-left text-xs font-bold text-[#64748B] px-6 py-4.5 tracking-tight uppercase">
                  {th}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E2E8F0]">
            {isLoading ? (
              <tr><td colSpan={7} className="px-6 py-8 text-center text-xs font-semibold text-slate-400">Loading…</td></tr>
            ) : complaints.length === 0 ? (
              <tr><td colSpan={7} className="px-6 py-8 text-center text-xs font-semibold text-slate-400">No complaints yet.</td></tr>
            ) : (
              complaints.map((c) => (
                <tr
                  key={c.id}
                  onClick={() => router.push(`${ROUTES.COMPLAINTS}/${c.id}`)}
                  className="hover:bg-[#F8FAFC] transition-colors cursor-pointer"
                >
                  <td className="px-6 py-4.5 text-xs font-bold text-[#0052FF]">
                    {c.complaint_number ?? `${c.id.slice(0, 8)}…`}
                  </td>
                  <td className="px-6 py-4.5 text-xs font-bold text-[#0F172A] max-w-[220px] truncate">
                    {c.title}
                  </td>
                  <td className="px-6 py-4.5">
                    {CHANNEL_ICONS[c.channel ?? ""] ?? <HelpCircle className="h-4.5 w-4.5 text-slate-400" />}
                  </td>
                  <td className="px-6 py-4.5 text-xs font-semibold text-[#334155]">
                    {c.theme ?? "—"}
                  </td>
                  <td className="px-6 py-4.5">{severityBadge(c.severity)}</td>
                  <td className="px-6 py-4.5">{slaBadge(c.sla_risk)}</td>
                  <td className="px-6 py-4.5 text-xs font-bold text-[#64748B]">
                    {timeAgo(c.created_at)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

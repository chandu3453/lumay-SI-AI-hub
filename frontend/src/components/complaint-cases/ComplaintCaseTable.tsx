import { useRouter } from "next/navigation";
import { Phone, Mail, MessageCircle, HelpCircle, MoreHorizontal, ChevronLeft, ChevronRight } from "lucide-react";

import type { CaseItem } from "@/features/complaint-cases/use-complaint-cases";

type ComplaintCaseTableProps = {
  data?: CaseItem[];
  isLoading?: boolean;
  total?: number;
  page?: number;
  pageSize?: number;
  onPageChange?: (page: number) => void;
  selectedIds?: Set<string>;
  onSelectionChange?: (ids: Set<string>) => void;
};

const CHANNEL_ICONS: Record<string, React.ReactNode> = {
  voice: <Phone className="h-3.5 w-3.5 text-[#10B981]" />,
  phone: <Phone className="h-3.5 w-3.5 text-[#10B981]" />,
  whatsapp: <MessageCircle className="h-3.5 w-3.5 text-[#10B981]" />,
  web_chat: <MessageCircle className="h-3.5 w-3.5 text-[#8B5CF6]" />,
  email: <Mail className="h-3.5 w-3.5 text-[#0052FF]" />,
};

function channelIcon(channel: string | null) {
  return CHANNEL_ICONS[channel ?? ""] ?? <HelpCircle className="h-3.5 w-3.5 text-slate-400" />;
}

function badgeClass(tone: "red" | "amber" | "green" | "blue" | "purple" | "slate") {
  const map = {
    red: "bg-red-50 border border-red-100 text-red-600",
    amber: "bg-amber-50 border border-amber-100 text-amber-600",
    green: "bg-green-50 border border-green-100 text-green-600",
    blue: "bg-blue-50 border border-blue-100 text-[#0052FF]",
    purple: "bg-purple-50 border border-purple-100 text-purple-600",
    slate: "bg-slate-50 border border-slate-100 text-slate-500",
  } as const;
  return map[tone];
}

function severityTone(severity: string): "red" | "amber" | "green" {
  if (severity === "high" || severity === "critical") return "red";
  if (severity === "medium") return "amber";
  return "green";
}

function slaTone(slaRisk: string | null): "red" | "amber" | "green" {
  if (slaRisk === "breached") return "red";
  if (slaRisk === "at_risk") return "amber";
  return "green";
}

function statusTone(status: string): "red" | "blue" | "purple" | "green" | "slate" {
  if (status === "escalated") return "red";
  if (status === "submitted" || status === "investigating") return "blue";
  if (status === "under_review") return "purple";
  if (status === "resolved") return "green";
  return "slate";
}

export function ComplaintCaseTable({
  data = [],
  isLoading = false,
  total = 0,
  page = 1,
  pageSize = 10,
  onPageChange,
  selectedIds = new Set(),
  onSelectionChange,
}: ComplaintCaseTableProps) {
  const router = useRouter();
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const toggleAll = () => {
    if (!onSelectionChange) return;
    if (selectedIds.size === data.length) onSelectionChange(new Set());
    else onSelectionChange(new Set(data.map((r) => r.id)));
  };

  const toggleOne = (id: string) => {
    if (!onSelectionChange) return;
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id); else next.add(id);
    onSelectionChange(next);
  };

  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl shadow-sm overflow-hidden flex flex-col w-full text-left">
      <div className="flex items-center justify-between border-b border-[#F1F5F9] px-5 py-4.5 bg-white text-xs font-bold text-[#64748B]">
        <div>
          {total === 0
            ? "No cases found"
            : `Showing ${(page - 1) * pageSize + 1} to ${Math.min(page * pageSize, total)} of ${total} cases`}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[1000px] border-collapse">
          <thead>
            <tr className="border-b border-[#F1F5F9] bg-[#F8FAFC]">
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400 w-12 text-center">
                <input
                  type="checkbox"
                  checked={data.length > 0 && selectedIds.size === data.length}
                  onChange={toggleAll}
                  className="rounded border-[#CBD5E1] h-3.5 w-3.5 cursor-pointer text-[#0052FF] focus:ring-[#0052FF]"
                />
              </th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Case ID</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Category</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Channel</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Theme</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Severity</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">SLA Risk</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Queue</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Received</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Status</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400 w-12 text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#F1F5F9]">
            {isLoading ? (
              <tr>
                <td colSpan={11} className="px-5 py-10 text-center text-xs font-semibold text-slate-400">
                  Loading cases…
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={11} className="px-5 py-10 text-center text-xs font-semibold text-slate-400">
                  No complaint cases match these filters.
                </td>
              </tr>
            ) : (
              data.map((row) => {
                const isChecked = selectedIds.has(row.id);
                return (
                  <tr
                    key={row.id}
                    className="hover:bg-[#F8FAFC] transition-all cursor-pointer"
                    onClick={() => router.push(`/complaints/${row.id}`)}
                  >
                    <td className="px-5 py-3.5 text-center" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => toggleOne(row.id)}
                        className="rounded border-[#CBD5E1] h-3.5 w-3.5 cursor-pointer text-[#0052FF] focus:ring-[#0052FF]"
                      />
                    </td>

                    <td className="px-5 py-3.5">
                      <span className="text-xs font-bold text-[#0052FF] hover:underline block">
                        {row.case_number ?? `${row.id.slice(0, 8)}…`}
                      </span>
                    </td>

                    <td className="px-5 py-3.5">
                      <span className="text-xs font-bold text-[#0F172A] capitalize">{row.category}</span>
                      {row.product ? (
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">{row.product}</span>
                      ) : null}
                    </td>

                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-1.5">
                        <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-slate-50 border border-slate-100 shrink-0">
                          {channelIcon(row.channel)}
                        </div>
                        <span className="text-xs font-bold text-[#475569] capitalize">{row.channel ?? "—"}</span>
                      </div>
                    </td>

                    <td className="px-5 py-3.5">
                      <span className="text-xs font-bold text-[#0F172A]">{row.theme ?? "—"}</span>
                    </td>

                    <td className="px-5 py-3.5">
                      <span className={`inline-block rounded-lg px-2.5 py-0.5 text-[10px] font-bold capitalize ${badgeClass(severityTone(row.severity))}`}>
                        {row.severity}
                      </span>
                    </td>

                    <td className="px-5 py-3.5">
                      {row.sla_risk ? (
                        <span className={`inline-block rounded-lg px-2.5 py-0.5 text-[10px] font-bold capitalize ${badgeClass(slaTone(row.sla_risk))}`}>
                          {row.sla_risk.replace("_", " ")}
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400">—</span>
                      )}
                    </td>

                    <td className="px-5 py-3.5">
                      <span className="text-xs font-bold text-[#0F172A]">{row.assigned_queue ?? "Unassigned"}</span>
                    </td>

                    <td className="px-5 py-3.5 text-xs font-semibold text-[#475569]">
                      {new Date(row.created_at).toLocaleString()}
                    </td>

                    <td className="px-5 py-3.5">
                      <span className={`inline-block rounded-lg px-2.5 py-0.5 text-[10px] font-bold capitalize ${badgeClass(statusTone(row.status))}`}>
                        {row.status.replace("_", " ")}
                      </span>
                    </td>

                    <td className="px-5 py-3.5 text-center" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => router.push(`/complaints/${row.id}`)}
                        className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-all mx-auto shadow-sm"
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between border-t border-[#F1F5F9] px-5 py-4 bg-white text-xs font-bold text-[#64748B]">
        <div>Page {page} of {totalPages}</div>
        <div className="flex items-center gap-1.5">
          <button
            disabled={page <= 1}
            onClick={() => onPageChange?.(page - 1)}
            className="h-8 w-8 flex items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-400 hover:text-slate-600 transition-all shadow-sm disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="h-8 w-8 flex items-center justify-center rounded-xl border border-[#0052FF] bg-[#EFF6FF] text-[#0052FF] shadow-sm">
            {page}
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => onPageChange?.(page + 1)}
            className="h-8 w-8 flex items-center justify-center rounded-xl border border-slate-200 bg-white text-[#94A3B8] hover:text-slate-600 transition-all shadow-sm disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

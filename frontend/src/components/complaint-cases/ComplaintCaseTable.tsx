import { Phone, Mail, MessageCircle, MoreHorizontal, ChevronLeft, ChevronRight, SlidersHorizontal } from "lucide-react";

type CaseItem = {
  id: string;
  extId: string;
  customerName: string;
  custCode: string;
  channel: string;
  channelIcon: React.ReactNode;
  theme: string;
  severity: "low" | "medium" | "high";
  slaStatus: "on_track" | "at_risk" | "overdue";
  assignedName: string;
  assignedRole: string;
  receivedTime: string;
  status: "in_progress" | "new" | "pending_review" | "acknowledged" | "escalated";
};

type ComplaintCaseTableProps = {
  data?: any;
  isLoading?: boolean;
  total?: number;
  page?: number;
  pageSize?: number;
  onPageChange?: (page: number) => void;
  selectedIds?: Set<string>;
  onSelectionChange?: (ids: Set<string>) => void;
};

const MOCK_ROWS: CaseItem[] = [
  {
    id: "C-2025-01568",
    extId: "EXT-98541",
    customerName: "Mohammed Al Hinai",
    custCode: "CUST-000198",
    channel: "Voice Call",
    channelIcon: <Phone className="h-3.5 w-3.5 text-[#10B981]" />,
    theme: "Claim Delays",
    severity: "high",
    slaStatus: "at_risk",
    assignedName: "Fatima Al Lawati",
    assignedRole: "Complaint Officer",
    receivedTime: "May 16, 2025 10:24 AM",
    status: "in_progress",
  },
  {
    id: "C-2025-01567",
    extId: "EXT-98540",
    customerName: "Fatima Al Lawati",
    custCode: "CUST-000199",
    channel: "WhatsApp",
    channelIcon: <MessageCircle className="h-3.5 w-3.5 text-[#10B981]" />,
    theme: "Service Quality",
    severity: "high",
    slaStatus: "at_risk",
    assignedName: "Hamed Al Balushi",
    assignedRole: "Complaint Officer",
    receivedTime: "May 16, 2025 10:21 AM",
    status: "new",
  },
  {
    id: "C-2025-01566",
    extId: "EXT-98539",
    customerName: "Sultan Al Khaldi",
    custCode: "CUST-000200",
    channel: "Email",
    channelIcon: <Mail className="h-3.5 w-3.5 text-[#0052FF]" />,
    theme: "Communication",
    severity: "medium",
    slaStatus: "on_track",
    assignedName: "Aisha Al Raisi",
    assignedRole: "Complaint Officer",
    receivedTime: "May 16, 2025 10:14 AM",
    status: "new",
  },
  {
    id: "C-2025-01565",
    extId: "EXT-98538",
    customerName: "Aisha Al Raisi",
    custCode: "CUST-000201",
    channel: "Web Chat",
    channelIcon: <MessageCircle className="h-3.5 w-3.5 text-[#8B5CF6]" />,
    theme: "Policy & Coverage",
    severity: "medium",
    slaStatus: "on_track",
    assignedName: "Abdullah Al Hasani",
    assignedRole: "Complaint Officer",
    receivedTime: "May 16, 2025 10:08 AM",
    status: "pending_review",
  },
  {
    id: "C-2025-01564",
    extId: "EXT-98537",
    customerName: "Hamed Al Balushi",
    custCode: "CUST-000202",
    channel: "Voice Call",
    channelIcon: <Phone className="h-3.5 w-3.5 text-[#10B981]" />,
    theme: "Payments & Refunds",
    severity: "low",
    slaStatus: "on_track",
    assignedName: "Khalid Al Maamari",
    assignedRole: "Complaint Officer",
    receivedTime: "May 16, 2025 09:59 AM",
    status: "acknowledged",
  },
  {
    id: "C-2025-01563",
    extId: "EXT-98536",
    customerName: "Salma Al Maqbali",
    custCode: "CUST-000203",
    channel: "WhatsApp",
    channelIcon: <MessageCircle className="h-3.5 w-3.5 text-[#10B981]" />,
    theme: "Provider / Garage",
    severity: "high",
    slaStatus: "overdue",
    assignedName: "Supervisor Queue",
    assignedRole: "Supervisor",
    receivedTime: "May 16, 2025 09:41 AM",
    status: "escalated",
  },
  {
    id: "C-2025-01562",
    extId: "EXT-98535",
    customerName: "Yousef Al Harthy",
    custCode: "CUST-000204",
    channel: "Email",
    channelIcon: <Mail className="h-3.5 w-3.5 text-[#0052FF]" />,
    theme: "Renewal",
    severity: "low",
    slaStatus: "on_track",
    assignedName: "Noor Al Shukaili",
    assignedRole: "Complaint Officer",
    receivedTime: "May 16, 2025 09:32 AM",
    status: "in_progress",
  },
  {
    id: "C-2025-01561",
    extId: "EXT-98534",
    customerName: "Ahmed Al Hadi",
    custCode: "CUST-000205",
    channel: "Mobile Chat",
    channelIcon: <MessageCircle className="h-3.5 w-3.5 text-[#8B5CF6]" />,
    theme: "Authorization Issues",
    severity: "high",
    slaStatus: "at_risk",
    assignedName: "Fatima Al Lawati",
    assignedRole: "Complaint Officer",
    receivedTime: "May 16, 2025 09:18 AM",
    status: "new",
  },
  {
    id: "C-2025-01560",
    extId: "EXT-98533",
    customerName: "Maryam Al Farsi",
    custCode: "CUST-000206",
    channel: "Voice Call",
    channelIcon: <Phone className="h-3.5 w-3.5 text-[#10B981]" />,
    theme: "Claim Documentation",
    severity: "medium",
    slaStatus: "on_track",
    assignedName: "Aisha Al Raisi",
    assignedRole: "Complaint Officer",
    receivedTime: "May 16, 2025 08:55 AM",
    status: "pending_review",
  },
  {
    id: "C-2025-01559",
    extId: "EXT-98532",
    customerName: "Rashid Al Zadjali",
    custCode: "CUST-000207",
    channel: "Email",
    channelIcon: <Mail className="h-3.5 w-3.5 text-[#0052FF]" />,
    theme: "Refund Delay",
    severity: "high",
    slaStatus: "overdue",
    assignedName: "Supervisor Queue",
    assignedRole: "Supervisor",
    receivedTime: "May 16, 2025 08:41 AM",
    status: "escalated",
  },
];

export function ComplaintCaseTable({
  page = 1,
  onPageChange,
  selectedIds = new Set(),
  onSelectionChange,
}: ComplaintCaseTableProps) {
  const toggleAll = () => {
    if (!onSelectionChange) return;
    if (selectedIds.size === MOCK_ROWS.length) onSelectionChange(new Set());
    else onSelectionChange(new Set(MOCK_ROWS.map((r) => r.id)));
  };

  const toggleOne = (id: string) => {
    if (!onSelectionChange) return;
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id); else next.add(id);
    onSelectionChange(next);
  };

  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl shadow-sm overflow-hidden flex flex-col w-full text-left">
      {/* Search Header Info bar */}
      <div className="flex items-center justify-between border-b border-[#F1F5F9] px-5 py-4.5 bg-white text-xs font-bold text-[#64748B]">
        <div>Showing 1 to 10 of 2,456 cases</div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 cursor-pointer">
            <span>Sort by:</span>
            <span className="text-[#0F172A]">Received Time</span>
            <div className="border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-[#0F172A] ml-0.5" />
          </div>
          <div className="flex items-center gap-1 border border-slate-200 rounded-xl p-0.5 bg-[#F8FAFC]">
            <button className="h-7 w-7 flex items-center justify-center bg-white rounded-lg text-slate-800 shadow-sm">
              <SlidersHorizontal className="h-3.5 w-3.5" />
            </button>
            <button className="h-7 w-7 flex items-center justify-center rounded-lg text-slate-400 hover:text-slate-600">
              <MoreHorizontal className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Table grid wrapper */}
      <div className="overflow-x-auto">
        <table className="w-full min-w-[1000px] border-collapse">
          <thead>
            <tr className="border-b border-[#F1F5F9] bg-[#F8FAFC]">
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400 w-12 text-center">
                <input
                  type="checkbox"
                  checked={selectedIds.size === MOCK_ROWS.length}
                  onChange={toggleAll}
                  className="rounded border-[#CBD5E1] h-3.5 w-3.5 cursor-pointer text-[#0052FF] focus:ring-[#0052FF]"
                />
              </th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Case ID</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Customer</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Channel</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Theme</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Severity</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">SLA Status</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Assigned To</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Received Time</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Status</th>
              <th className="px-5 py-4 text-[10px] font-extrabold uppercase tracking-wider text-slate-400 w-12 text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#F1F5F9]">
            {MOCK_ROWS.map((row) => {
              const isChecked = selectedIds.has(row.id);
              
              // Style variables for severity
              const sevBadge = row.severity === "high"
                ? "bg-red-50 border border-red-100 text-red-600"
                : row.severity === "medium"
                ? "bg-amber-50 border border-amber-100 text-amber-600"
                : "bg-green-50 border border-green-100 text-green-600";

              // Style variables for SLA
              const slaBadge = row.slaStatus === "overdue"
                ? "bg-red-50 border border-red-100 text-red-600"
                : row.slaStatus === "at_risk"
                ? "bg-amber-50 border border-amber-100 text-amber-600"
                : "bg-green-50 border border-green-100 text-green-600";

              // Style variables for status
              const statusBadge = row.status === "escalated"
                ? "bg-red-50 border border-red-100 text-red-600"
                : row.status === "in_progress"
                ? "bg-blue-50 border border-blue-100 text-[#0052FF]"
                : row.status === "new"
                ? "bg-blue-50 border border-blue-100 text-[#0052FF]"
                : row.status === "acknowledged"
                ? "bg-purple-50 border border-purple-100 text-purple-600"
                : "bg-purple-50 border border-purple-100 text-purple-600"; // Pending Review

              const statusLabel = row.status === "in_progress"
                ? "In Progress"
                : row.status === "new"
                ? "New"
                : row.status === "acknowledged"
                ? "Acknowledged"
                : row.status === "pending_review"
                ? "Pending Review"
                : "Escalated";

              const initials = row.customerName.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);

              return (
                <tr key={row.id} className="hover:bg-[#F8FAFC] transition-all">
                  <td className="px-5 py-3.5 text-center">
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggleOne(row.id)}
                      className="rounded border-[#CBD5E1] h-3.5 w-3.5 cursor-pointer text-[#0052FF] focus:ring-[#0052FF]"
                    />
                  </td>
                  
                  {/* Case ID */}
                  <td className="px-5 py-3.5">
                    <span className="text-xs font-bold text-[#0052FF] hover:underline cursor-pointer block">{row.id}</span>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{row.extId}</span>
                  </td>

                  {/* Customer */}
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2.5">
                      <div className="h-7 w-7 rounded-xl bg-blue-50 border border-blue-100 text-[#0052FF] flex items-center justify-center text-[10px] font-bold shrink-0">
                        {initials}
                      </div>
                      <div>
                        <span className="text-xs font-bold text-[#0F172A] block">{row.customerName}</span>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{row.custCode}</span>
                      </div>
                    </div>
                  </td>

                  {/* Channel */}
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-1.5">
                      <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-slate-50 border border-slate-100 shrink-0">
                        {row.channelIcon}
                      </div>
                      <span className="text-xs font-bold text-[#475569]">{row.channel}</span>
                    </div>
                  </td>

                  {/* Theme */}
                  <td className="px-5 py-3.5">
                    <span className="text-xs font-bold text-[#0F172A]">{row.theme}</span>
                  </td>

                  {/* Severity */}
                  <td className="px-5 py-3.5">
                    <span className={`inline-block rounded-lg px-2.5 py-0.5 text-[10px] font-bold capitalize ${sevBadge}`}>
                      {row.severity}
                    </span>
                  </td>

                  {/* SLA Status */}
                  <td className="px-5 py-3.5">
                    <span className={`inline-block rounded-lg px-2.5 py-0.5 text-[10px] font-bold capitalize ${slaBadge}`}>
                      {row.slaStatus === "on_track" ? "On Track" : row.slaStatus === "at_risk" ? "At Risk" : "Overdue"}
                    </span>
                  </td>

                  {/* Assigned To */}
                  <td className="px-5 py-3.5">
                    <span className="text-xs font-bold text-[#0F172A] block">{row.assignedName}</span>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{row.assignedRole}</span>
                  </td>

                  {/* Received Time */}
                  <td className="px-5 py-3.5 text-xs font-semibold text-[#475569]">
                    {row.receivedTime}
                  </td>

                  {/* Status */}
                  <td className="px-5 py-3.5">
                    <span className={`inline-block rounded-lg px-2.5 py-0.5 text-[10px] font-bold ${statusBadge}`}>
                      {statusLabel}
                    </span>
                  </td>

                  {/* Actions dropdown */}
                  <td className="px-5 py-3.5 text-center">
                    <button className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-all mx-auto shadow-sm">
                      <MoreHorizontal className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="flex items-center justify-between border-t border-[#F1F5F9] px-5 py-4 bg-white text-xs font-bold text-[#64748B]">
        <div>Showing 1 to 10 of 2,456 cases</div>
        <div className="flex items-center gap-1.5">
          <button className="h-8 w-8 flex items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-400 hover:text-slate-600 transition-all shadow-sm">
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button className="h-8 w-8 flex items-center justify-center rounded-xl border border-[#0052FF] bg-[#EFF6FF] text-[#0052FF] shadow-sm">
            1
          </button>
          <button className="h-8 w-8 flex items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 transition-all shadow-sm" onClick={() => onPageChange?.(2)}>
            2
          </button>
          <button className="h-8 w-8 flex items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 transition-all shadow-sm" onClick={() => onPageChange?.(3)}>
            3
          </button>
          <span className="px-1 text-slate-400">...</span>
          <button className="h-8 px-2.5 flex items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 transition-all shadow-sm">
            246
          </button>
          <button className="h-8 w-8 flex items-center justify-center rounded-xl border border-slate-200 bg-white text-[#94A3B8] hover:text-slate-600 transition-all shadow-sm" onClick={() => onPageChange?.(2)}>
            <ChevronRight className="h-4 w-4" />
          </button>

          {/* Page count selector */}
          <div className="relative ml-2">
            <select className="h-8 rounded-xl border border-slate-200 bg-white px-2.5 pr-7 text-xs font-bold text-slate-700 focus:outline-none shadow-sm cursor-pointer appearance-none">
              <option>10 / page</option>
              <option>20 / page</option>
              <option>50 / page</option>
            </select>
            <div className="absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-[#64748B]" />
          </div>
        </div>
      </div>
    </div>
  );
}
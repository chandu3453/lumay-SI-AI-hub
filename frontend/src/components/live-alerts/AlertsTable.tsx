import { useRouter } from "next/navigation";
import { Phone, MessageCircle, Mail, MessageSquare, ShieldAlert, Clock, AlertTriangle, ShieldCheck, AlertCircle, RefreshCw } from "lucide-react";
import { ROUTES } from "@/lib/constants";

const MOCK_ALERTS = [
  {
    id: "A-2025-001",
    time: "2m ago",
    hour: "10:24 AM",
    channelIcon: <Phone className="h-4 w-4 text-[#10B981]" />,
    channelBg: "bg-emerald-50 border border-emerald-100",
    customer: "Mohammed Al Hinai",
    policy: "P-987654 | Motor",
    alertIcon: <ShieldAlert className="h-4 w-4 text-[#EF4444]" />,
    alertText: "High escalation risk",
    summary: "Customer is extremely dissatisfied with claim delay and is threatening to escalate to regulatory authority.",
    severity: <span className="rounded-lg bg-red-50 border border-red-100 px-2.5 py-1 text-[11px] font-bold text-red-600">High</span>,
    sla: <span className="rounded-lg bg-amber-50 border border-amber-100 px-2.5 py-1 text-[11px] font-bold text-amber-600">At Risk</span>,
    status: <span className="rounded-lg bg-blue-50 border border-blue-100 px-2.5 py-1 text-[11px] font-bold text-[#0052FF]">New</span>,
    stripColor: "bg-red-500",
  },
  {
    id: "A-2025-002",
    time: "5m ago",
    hour: "10:21 AM",
    channelIcon: <MessageCircle className="h-4 w-4 text-[#10B981]" />,
    channelBg: "bg-emerald-50 border border-emerald-100",
    customer: "Fatima Al Lawati",
    policy: "P-123456 | Health",
    alertIcon: <ShieldAlert className="h-4 w-4 text-[#EF4444]" />,
    alertText: "Negative sentiment",
    summary: "Customer unhappy with medical provider service quality. Requests immediate resolution.",
    severity: <span className="rounded-lg bg-red-50 border border-red-100 px-2.5 py-1 text-[11px] font-bold text-red-600">High</span>,
    sla: <span className="rounded-lg bg-amber-50 border border-amber-100 px-2.5 py-1 text-[11px] font-bold text-amber-600">At Risk</span>,
    status: <span className="rounded-lg bg-blue-50 border border-blue-100 px-2.5 py-1 text-[11px] font-bold text-[#0052FF]">New</span>,
    stripColor: "bg-red-500",
  },
  {
    id: "A-2025-003",
    time: "12m ago",
    hour: "10:14 AM",
    channelIcon: <Mail className="h-4 w-4 text-[#2563EB]" />,
    channelBg: "bg-blue-50 border border-blue-100",
    customer: "Sultan Al Khaldi",
    policy: "P-555666 | Motor",
    alertIcon: <ShieldCheck className="h-4 w-4 text-[#8B5CF6]" />,
    alertText: "Regulatory keyword",
    summary: "Email contains mention of Consumer Protection Authority and formal complaint.",
    severity: <span className="rounded-lg bg-amber-50 border border-amber-100 px-2.5 py-1 text-[11px] font-bold text-amber-600">Medium</span>,
    sla: <span className="rounded-lg bg-green-50 border border-green-100 px-2.5 py-1 text-[11px] font-bold text-green-600">On Track</span>,
    status: <span className="rounded-lg bg-blue-50 border border-blue-100 px-2.5 py-1 text-[11px] font-bold text-[#0052FF]">New</span>,
    stripColor: "bg-amber-500",
  },
  {
    id: "A-2025-004",
    time: "18m ago",
    hour: "10:08 AM",
    channelIcon: <MessageSquare className="h-4 w-4 text-[#8B5CF6]" />,
    channelBg: "bg-purple-50 border border-purple-100",
    customer: "Aisha Al Raisi",
    policy: "P-778899 | Home",
    alertIcon: <Clock className="h-4 w-4 text-[#F59E0B]" />,
    alertText: "SLA breach risk",
    summary: "Customer waiting for refund more than 10 days. Requesting urgent update.",
    severity: <span className="rounded-lg bg-amber-50 border border-amber-100 px-2.5 py-1 text-[11px] font-bold text-amber-600">Medium</span>,
    sla: <span className="rounded-lg bg-amber-50 border border-amber-100 px-2.5 py-1 text-[11px] font-bold text-amber-600">At Risk</span>,
    status: <span className="rounded-lg bg-purple-50 border border-purple-100 px-2.5 py-1 text-[11px] font-bold text-purple-600">Acknowledged</span>,
    stripColor: "bg-amber-500",
  },
  {
    id: "A-2025-005",
    time: "27m ago",
    hour: "09:59 AM",
    channelIcon: <MessageCircle className="h-4 w-4 text-[#10B981]" />,
    channelBg: "bg-emerald-50 border border-emerald-100",
    customer: "Hamed Al Balushi",
    policy: "P-445586 | Travel",
    alertIcon: <AlertTriangle className="h-4 w-4 text-[#F59E0B]" />,
    alertText: "Repeat complaint",
    summary: "Customer raised similar complaint for the 3rd time regarding travel insurance reimbursement.",
    severity: <span className="rounded-lg bg-green-50 border border-green-100 px-2.5 py-1 text-[11px] font-bold text-green-600">Low</span>,
    sla: <span className="rounded-lg bg-green-50 border border-green-100 px-2.5 py-1 text-[11px] font-bold text-green-600">On Track</span>,
    status: <span className="rounded-lg bg-blue-50 border border-blue-100 px-2.5 py-1 text-[11px] font-bold text-[#0052FF]">New</span>,
    stripColor: "bg-yellow-400",
  },
  {
    id: "A-2025-006",
    time: "45m ago",
    hour: "09:41 AM",
    channelIcon: <Phone className="h-4 w-4 text-[#10B981]" />,
    channelBg: "bg-emerald-50 border border-emerald-100",
    customer: "Yousef Al Harthy",
    policy: "P-334455 | Life",
    alertIcon: <AlertCircle className="h-4 w-4 text-[#F59E0B]" />,
    alertText: "Deteriorating sentiment",
    summary: "Customer losing confidence due to delayed policy approval. Needs follow-up.",
    severity: <span className="rounded-lg bg-green-50 border border-green-100 px-2.5 py-1 text-[11px] font-bold text-green-600">Low</span>,
    sla: <span className="rounded-lg bg-green-50 border border-green-100 px-2.5 py-1 text-[11px] font-bold text-green-600">On Track</span>,
    status: <span className="rounded-lg bg-blue-50 border border-blue-100 px-2.5 py-1 text-[11px] font-bold text-[#0052FF]">New</span>,
    stripColor: "bg-yellow-400",
  },
];

type AlertsTableProps = {
  data?: any;
  isLoading?: boolean;
  total?: number;
  page?: number;
  pageSize?: number;
  onPageChange?: (page: number) => void;
  onOpenComplaint?: (item: any) => void;
  onViewCustomer?: (item: any) => void;
  onViewWorkflow?: (item: any) => void;
  onAssignOfficer?: (item: any) => void;
  onAcknowledge?: (item: any) => void;
  onEscalate?: (item: any) => void;
  onArchive?: (item: any) => void;
};

export function AlertsTable(props: AlertsTableProps) {
  const router = useRouter();

  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-white shadow-sm overflow-hidden flex flex-col">
      {/* Table container */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-[#E2E8F0] bg-[#F8FAFC]">
              {["Time", "Channel", "Customer", "Alert Type", "AI Summary", "Severity", "SLA Risk", "Status", "Actions"].map((th) => (
                <th
                  key={th}
                  className={`text-left text-xs font-bold text-[#64748B] px-6 py-4.5 tracking-tight uppercase ${
                    th === "Channel" ? "text-center" : ""
                  }`}
                >
                  {th}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E2E8F0]">
            {MOCK_ALERTS.map((alert) => (
              <tr
                key={alert.id}
                onClick={() => router.push(ROUTES.COMPLAINTS)}
                className="hover:bg-[#F8FAFC] transition-colors cursor-pointer relative"
              >
                {/* Left colored border strip stripColor */}
                <td className="p-0 w-0 h-full relative">
                  <div className={`absolute left-0 top-0 bottom-0 w-1 ${alert.stripColor}`} />
                </td>

                {/* Time */}
                <td className="px-6 py-4.5 text-left">
                  <div className="flex flex-col -space-y-0.5">
                    <span className="text-xs font-bold text-[#0F172A]">{alert.time}</span>
                    <span className="text-[10px] font-bold text-slate-400">{alert.hour}</span>
                  </div>
                </td>

                {/* Channel */}
                <td className="px-6 py-4.5 text-center">
                  <div className="flex justify-center">
                    <div className={`flex h-8 w-8 items-center justify-center rounded-xl ${alert.channelBg}`}>
                      {alert.channelIcon}
                    </div>
                  </div>
                </td>

                {/* Customer */}
                <td className="px-6 py-4.5 text-left">
                  <div className="flex flex-col -space-y-0.5 min-w-[120px]">
                    <span className="text-xs font-bold text-[#0F172A]">{alert.customer}</span>
                    <span className="text-[10px] font-bold text-slate-400">{alert.policy}</span>
                  </div>
                </td>

                {/* Alert Type */}
                <td className="px-6 py-4.5 text-left">
                  <div className="flex items-center gap-2 font-bold text-xs text-[#0F172A]">
                    {alert.alertIcon}
                    <span>{alert.alertText}</span>
                  </div>
                </td>

                {/* AI Summary */}
                <td className="px-6 py-4.5 text-left text-xs font-semibold text-slate-500 max-w-sm">
                  <p className="line-clamp-2 leading-relaxed">{alert.summary}</p>
                </td>

                {/* Severity */}
                <td className="px-6 py-4.5 text-left">
                  {alert.severity}
                </td>

                {/* SLA Risk */}
                <td className="px-6 py-4.5 text-left">
                  {alert.sla}
                </td>

                {/* Status */}
                <td className="px-6 py-4.5 text-left">
                  {alert.status}
                </td>

                {/* Actions */}
                <td className="px-6 py-4.5 text-left">
                  <button className="flex h-8 w-8 items-center justify-center rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-all font-bold text-lg leading-0">
                    ...
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between px-6 py-4 bg-[#F8FAFC] border-t border-[#E2E8F0] text-xs font-bold text-slate-400">
        <span>Showing 1 to 6 of 6 live alerts</span>
        <div className="flex items-center gap-1.5 text-[#10B981]">
          <RefreshCw className="h-3.5 w-3.5 animate-spin" />
          <span>Auto-updating in real time</span>
        </div>
      </div>
    </div>
  );
}
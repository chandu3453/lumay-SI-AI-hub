import { useRouter } from "next/navigation";
import { Phone, MessageCircle, Mail, MessageSquare, Frown, Meh, Smile } from "lucide-react";
import { ROUTES } from "@/lib/constants";

const MOCK_COMPLAINTS = [
  {
    id: "C-2025-01568",
    customer: "Mohammed Al Hinai",
    channel: <Phone className="h-4.5 w-4.5 text-[#10B981]" />,
    theme: "Claim Delays",
    sentiment: <Frown className="h-4.5 w-4.5 text-[#EF4444]" />,
    severity: <span className="rounded-lg bg-red-50 border border-red-100 px-2 py-1 text-[11px] font-bold text-red-600">High</span>,
    sla: <span className="rounded-lg bg-amber-50 border border-amber-100 px-2 py-1 text-[11px] font-bold text-amber-600">At Risk</span>,
    time: "10m ago",
  },
  {
    id: "C-2025-01567",
    customer: "Fatima Al Lawati",
    channel: <MessageCircle className="h-4.5 w-4.5 text-[#10B981]" />,
    theme: "Service Quality",
    sentiment: <Frown className="h-4.5 w-4.5 text-[#EF4444]" />,
    severity: <span className="rounded-lg bg-red-50 border border-red-100 px-2 py-1 text-[11px] font-bold text-red-600">High</span>,
    sla: <span className="rounded-lg bg-amber-50 border border-amber-100 px-2 py-1 text-[11px] font-bold text-amber-600">At Risk</span>,
    time: "18m ago",
  },
  {
    id: "C-2025-01566",
    customer: "Sultan Al Khaldi",
    channel: <Mail className="h-4.5 w-4.5 text-[#2563EB]" />,
    theme: "Communication",
    sentiment: <Meh className="h-4.5 w-4.5 text-[#F59E0B]" />,
    severity: <span className="rounded-lg bg-amber-50 border border-amber-100 px-2 py-1 text-[11px] font-bold text-amber-600">Medium</span>,
    sla: <span className="rounded-lg bg-green-50 border border-green-100 px-2 py-1 text-[11px] font-bold text-green-600">On Track</span>,
    time: "32m ago",
  },
  {
    id: "C-2025-01565",
    customer: "Aisha Al Raisi",
    channel: <MessageSquare className="h-4.5 w-4.5 text-[#2563EB]" />,
    theme: "Policy & Coverage",
    sentiment: <Meh className="h-4.5 w-4.5 text-[#F59E0B]" />,
    severity: <span className="rounded-lg bg-amber-50 border border-amber-100 px-2 py-1 text-[11px] font-bold text-amber-600">Medium</span>,
    sla: <span className="rounded-lg bg-green-50 border border-green-100 px-2 py-1 text-[11px] font-bold text-green-600">On Track</span>,
    time: "45m ago",
  },
  {
    id: "C-2025-01564",
    customer: "Hamed Al Balushi",
    channel: <Phone className="h-4.5 w-4.5 text-[#10B981]" />,
    theme: "Payments & Refunds",
    sentiment: <Smile className="h-4.5 w-4.5 text-[#10B981]" />,
    severity: <span className="rounded-lg bg-green-50 border border-green-100 px-2 py-1 text-[11px] font-bold text-green-600">Low</span>,
    sla: <span className="rounded-lg bg-green-50 border border-green-100 px-2 py-1 text-[11px] font-bold text-green-600">On Track</span>,
    time: "1h ago",
  },
];

export function RecentComplaintsTable() {
  const router = useRouter();

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
              {["ID", "Customer", "Channel", "Theme", "Sentiment", "Severity", "SLA Status", "Time"].map((th) => (
                <th key={th} className="text-left text-xs font-bold text-[#64748B] px-6 py-4.5 tracking-tight uppercase">
                  {th}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E2E8F0]">
            {MOCK_COMPLAINTS.map((c) => (
              <tr
                key={c.id}
                onClick={() => router.push(`${ROUTES.COMPLAINTS}/${c.id}`)}
                className="hover:bg-[#F8FAFC] transition-colors cursor-pointer"
              >
                {/* ID */}
                <td className="px-6 py-4.5 text-xs font-bold text-[#0052FF]">
                  {c.id}
                </td>
                {/* Customer */}
                <td className="px-6 py-4.5 text-xs font-bold text-[#0F172A]">
                  {c.customer}
                </td>
                {/* Channel */}
                <td className="px-6 py-4.5">
                  {c.channel}
                </td>
                {/* Theme */}
                <td className="px-6 py-4.5 text-xs font-semibold text-[#334155]">
                  {c.theme}
                </td>
                {/* Sentiment */}
                <td className="px-6 py-4.5">
                  {c.sentiment}
                </td>
                {/* Severity */}
                <td className="px-6 py-4.5">
                  {c.severity}
                </td>
                {/* SLA Status */}
                <td className="px-6 py-4.5">
                  {c.sla}
                </td>
                {/* Time */}
                <td className="px-6 py-4.5 text-xs font-bold text-[#64748B]">
                  {c.time}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
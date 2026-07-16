import { AlertTriangle, Clock, User, CheckCircle2, MessageSquare, Shield, Settings, ChevronLeft, ChevronRight } from "lucide-react";

type FeedItem = {
  id: string;
  title: string;
  description: string;
  time: string;
  icon: React.ReactNode;
  iconBg: string;
  iconColor: string;
  leftStripColor: string;
  unread: boolean;
  badge?: React.ReactNode;
};

const TODAY_ITEMS: FeedItem[] = [
  {
    id: "N-1",
    title: "High Risk Complaint Detected",
    description: "A high risk complaint has been detected for customer Fatima Al Lawati (CUST-2025-01567) Channel: WhatsApp",
    time: "10:21 AM",
    icon: <AlertTriangle className="h-5 w-5" />,
    iconBg: "bg-red-50 border border-red-100",
    iconColor: "text-red-600",
    leftStripColor: "bg-red-500",
    unread: true,
    badge: (
      <span className="rounded bg-red-50 border border-red-100 px-2 py-0.5 text-[9px] font-bold text-red-600">
        High Risk
      </span>
    ),
  },
  {
    id: "N-2",
    title: "SLA Breach Warning",
    description: "SLA is at risk for case C-2025-01565 (Policy & Coverage) Due in 2 hours • Assigned to Aisha Al Raisi",
    time: "09:45 AM",
    icon: <Clock className="h-5 w-5" />,
    iconBg: "bg-amber-50 border border-amber-100",
    iconColor: "text-amber-600",
    leftStripColor: "bg-amber-500",
    unread: true,
  },
  {
    id: "N-3",
    title: "Case Assigned to You",
    description: "Case C-2025-01566 (Communication) has been assigned to you Channel: Email • Customer: Sultan Al Khaldi",
    time: "09:20 AM",
    icon: <User className="h-5 w-5" />,
    iconBg: "bg-purple-50 border border-purple-100",
    iconColor: "text-purple-600",
    leftStripColor: "bg-purple-500",
    unread: true,
  },
  {
    id: "N-4",
    title: "Complaint Resolved",
    description: "Case C-2025-01564 (Payments & Refunds) has been resolved Resolved by Khalid Al Maamari",
    time: "08:55 AM",
    icon: <CheckCircle2 className="h-5 w-5" />,
    iconBg: "bg-green-50 border border-green-100",
    iconColor: "text-green-600",
    leftStripColor: "bg-green-500",
    unread: true,
  },
];

const YESTERDAY_ITEMS: FeedItem[] = [
  {
    id: "N-5",
    title: "Investigation Overdue",
    description: "Investigation is overdue for case C-2025-01563 (Provider / Garage) Overdue by 1 day • Escalated to Supervisor Queue",
    time: "Yesterday, 05:30 PM",
    icon: <Clock className="h-5 w-5" />,
    iconBg: "bg-amber-50 border border-amber-100",
    iconColor: "text-amber-600",
    leftStripColor: "bg-amber-500",
    unread: true,
  },
  {
    id: "N-6",
    title: "New Customer Feedback",
    description: "New survey feedback received for policy P-987654 Rating: 2/5 • Channel: Web Survey",
    time: "Yesterday, 03:15 PM",
    icon: <MessageSquare className="h-5 w-5" />,
    iconBg: "bg-blue-50 border border-blue-100",
    iconColor: "text-[#0052FF]",
    leftStripColor: "bg-[#0052FF]",
    unread: false,
  },
  {
    id: "N-7",
    title: "Regulatory Risk Alert",
    description: "Potential regulatory risk detected in case C-2025-01561 Category: Refund Delay • Severity: High",
    time: "Yesterday, 11:10 AM",
    icon: <Shield className="h-5 w-5" />,
    iconBg: "bg-red-50 border border-red-100",
    iconColor: "text-red-600",
    leftStripColor: "bg-red-500",
    unread: false,
  },
  {
    id: "N-8",
    title: "System Update",
    description: "Document ingestion completed for 32 new interactions All channels",
    time: "Yesterday, 09:00 AM",
    icon: <Settings className="h-5 w-5" />,
    iconBg: "bg-slate-50 border border-slate-100",
    iconColor: "text-slate-500",
    leftStripColor: "bg-slate-400",
    unread: false,
  },
];

export function NotificationTimeline() {
  const renderItem = (item: FeedItem) => (
    <div
      key={item.id}
      className={`flex items-start gap-4 p-4.5 rounded-2xl border transition-all hover:shadow-sm ${
        item.unread
          ? "bg-[#F8FAFC] border-slate-100"
          : "bg-white border-[#E2E8F0]"
      }`}
    >
      {/* Left indicator strip */}
      <div className={`h-10 w-1.5 rounded-full shrink-0 ${item.leftStripColor}`} />

      {/* Styled Icon */}
      <div className={`h-11 w-11 rounded-xl flex items-center justify-center shrink-0 border ${item.iconBg} ${item.iconColor}`}>
        {item.icon}
      </div>

      {/* Middle text blocks */}
      <div className="flex-1 min-w-0 text-left">
        <div className="flex items-center gap-2">
          <h4 className="text-xs font-bold text-[#0F172A] truncate">{item.title}</h4>
          {item.badge}
          {item.unread && <div className="h-1.5 w-1.5 rounded-full bg-[#0052FF]" />}
        </div>
        <p className="text-[11px] font-semibold text-[#64748B] leading-relaxed mt-1">
          {item.description}
        </p>
      </div>

      {/* Right time value */}
      <div className="text-[10px] font-bold text-slate-400 shrink-0 whitespace-nowrap">
        {item.time}
      </div>
    </div>
  );

  return (
    <div className="space-y-6 text-left">
      {/* Today Section */}
      <div>
        <h3 className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-3.5">
          Today
        </h3>
        <div className="space-y-3">
          {TODAY_ITEMS.map(renderItem)}
        </div>
      </div>

      {/* Yesterday Section */}
      <div className="pt-2">
        <h3 className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider mb-3.5">
          Yesterday
        </h3>
        <div className="space-y-3">
          {YESTERDAY_ITEMS.map(renderItem)}
        </div>
      </div>

      {/* Pagination Footer */}
      <div className="flex items-center justify-between border-t border-[#F1F5F9] pt-5 mt-8 text-xs font-bold text-[#64748B]">
        <div>Showing 1 to 8 of 12 notifications</div>
        <div className="flex items-center gap-1.5">
          <button className="h-8 w-8 flex items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-400 hover:text-slate-600 transition-all shadow-sm">
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button className="h-8 w-8 flex items-center justify-center rounded-xl border border-[#0052FF] bg-[#EFF6FF] text-[#0052FF] shadow-sm">
            1
          </button>
          <button className="h-8 w-8 flex items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 transition-all shadow-sm">
            2
          </button>
          <button className="h-8 w-8 flex items-center justify-center rounded-xl border border-slate-200 bg-white text-[#94A3B8] hover:text-slate-600 transition-all shadow-sm">
            <ChevronRight className="h-4 w-4" />
          </button>

          <div className="relative ml-2">
            <select className="h-8 rounded-xl border border-slate-200 bg-white px-2.5 pr-7 text-xs font-bold text-slate-700 focus:outline-none shadow-sm cursor-pointer appearance-none">
              <option>10 / page</option>
            </select>
            <div className="absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-[#64748B]" />
          </div>
        </div>
      </div>
    </div>
  );
}
import Link from "next/link";
import { Clock, MessageCircle, Mail, Shield, CreditCard } from "lucide-react";
import { ROUTES } from "@/lib/constants";

const MOCK_THEMES = [
  { category: "Claim Delays", count: 845, percent: 100, icon: <Clock className="h-3.5 w-3.5 text-[#64748B]" /> },
  { category: "Service Quality", count: 612, percent: 72, icon: <MessageCircle className="h-3.5 w-3.5 text-[#64748B]" /> },
  { category: "Communication", count: 481, percent: 57, icon: <Mail className="h-3.5 w-3.5 text-[#64748B]" /> },
  { category: "Policy & Coverage", count: 325, percent: 38, icon: <Shield className="h-3.5 w-3.5 text-[#64748B]" /> },
  { category: "Payments & Refunds", count: 305, percent: 36, icon: <CreditCard className="h-3.5 w-3.5 text-[#64748B]" /> },
];

export function ComplaintThemes() {
  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-sm flex flex-col h-96">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-sm font-bold text-[#0F172A] tracking-tight">Top Complaint Themes</h3>
        <Link
          href={ROUTES.COMPLAINTS}
          className="text-xs font-bold text-[#0052FF] hover:underline"
        >
          View all
        </Link>
      </div>

      {/* Progress Bars List */}
      <div className="flex-1 flex flex-col justify-between py-1.5">
        {MOCK_THEMES.map((theme) => (
          <div key={theme.category} className="space-y-1.5">
            <div className="flex items-center justify-between text-xs font-bold">
              <div className="flex items-center gap-2">
                {theme.icon}
                <span className="text-[#0F172A]">{theme.category}</span>
              </div>
              <span className="text-[#64748B]">{theme.count}</span>
            </div>
            <div className="h-1.5 rounded-full bg-[#F1F5F9] overflow-hidden">
              <div
                className="h-full rounded-full bg-[#0052FF] transition-all duration-500"
                style={{ width: `${theme.percent}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
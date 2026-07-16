"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, AlertTriangle, Users, FileText, BarChart3, Bell, Settings, Shield, ChevronRight, MessageSquare } from "lucide-react";
import { cn } from "@/lib/cn";
import { ROUTES } from "@/lib/constants";

const NAV_ITEMS = [
  { label: "Dashboard", href: ROUTES.DASHBOARD, icon: LayoutDashboard },
  { label: "Complaints", href: ROUTES.COMPLAINTS, icon: AlertTriangle },
  { label: "Live Alerts", href: ROUTES.LIVE_ALERTS, icon: Bell },
  { label: "Interactions", href: ROUTES.INTERACTIONS, icon: MessageSquare },
  { label: "Customers", href: ROUTES.CUSTOMERS, icon: Users },
  { label: "Complaint Cases", href: ROUTES.COMPLAINT_CASES, icon: FileText },
  { label: "Analytics", href: ROUTES.ANALYTICS, icon: BarChart3 },
  { label: "Reports", href: ROUTES.REPORTS, icon: FileText },
  { label: "Notifications", href: ROUTES.NOTIFICATIONS, icon: Bell },
  { label: "Administration", href: ROUTES.ADMINISTRATION, icon: Shield },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-60 flex-col border-r border-[#E2E8F0] bg-white">
      <div className="flex h-16 items-center gap-2.5 border-b border-[#E2E8F0] px-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#2563EB]">
          <Shield className="h-4 w-4 text-white" />
        </div>
        <span className="text-base font-semibold text-[#0F172A]">LuMay</span>
      </div>

      <nav className="flex-1 space-y-0.5 p-3">
        {NAV_ITEMS.map(({ label, href, icon: Icon }) => {
          const isActive = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={label}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-[#2563EB]/10 text-[#2563EB]"
                  : "text-[#64748B] hover:bg-[#F8FAFC] hover:text-[#0F172A]",
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-[#E2E8F0] p-4">
        <div className="flex items-center gap-3 rounded-lg bg-[#F8FAFC] p-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#2563EB]/10 text-[#2563EB] text-xs font-semibold">
            AD
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-[#0F172A] truncate">Admin User</p>
            <p className="text-xs text-[#94A3B8] truncate">admin@lumay.ai</p>
          </div>
          <ChevronRight className="h-4 w-4 text-[#94A3B8]" />
        </div>
      </div>
    </aside>
  );
}
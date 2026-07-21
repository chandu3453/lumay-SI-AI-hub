import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  MessageSquare,
  GitBranch,
  Bell,
  BarChart3,
  FileText,
  Search,
  Settings,
  UserCog,
  ChevronDown,
  Shield,
  Radio,
  FolderKanban,
  Building2,
  Sparkles,
} from "lucide-react";

import { cn } from "@/lib/cn";
import { ROUTES } from "@/lib/constants";
import { useAuthStore } from "@/stores/auth.store";

const NAV_ITEMS = [
  { label: "Dashboard", href: ROUTES.DASHBOARD, icon: <LayoutDashboard className="h-4.5 w-4.5" /> },
  { label: "Interactions", href: ROUTES.INTERACTIONS, icon: <MessageSquare className="h-4.5 w-4.5" /> },
  { label: "Customers", href: ROUTES.CUSTOMERS, icon: <Users className="h-4.5 w-4.5" /> },
  { label: "Complaint Cases", href: ROUTES.COMPLAINT_CASES, icon: <FolderKanban className="h-4.5 w-4.5" /> },
  { label: "Workflows", href: ROUTES.WORKFLOW, icon: <GitBranch className="h-4.5 w-4.5" /> },
  { label: "Live Alerts", href: ROUTES.LIVE_ALERTS, icon: <Radio className="h-4.5 w-4.5" /> },
  { label: "Analytics", href: ROUTES.ANALYTICS, icon: <BarChart3 className="h-4.5 w-4.5" /> },
  { label: "Enterprise Analytics", href: ROUTES.ENTERPRISE_ANALYTICS, icon: <Sparkles className="h-4.5 w-4.5" /> },
  { label: "Reports", href: ROUTES.REPORTS, icon: <FileText className="h-4.5 w-4.5" /> },
  { label: "Notifications", href: ROUTES.NOTIFICATIONS, icon: <Bell className="h-4.5 w-4.5" /> },
  { label: "Administration", href: ROUTES.ADMINISTRATION, icon: <Building2 className="h-4.5 w-4.5" /> },
  { label: "Settings", href: ROUTES.SETTINGS, icon: <Settings className="h-4.5 w-4.5" /> },
];

export function Sidebar() {
  const pathname = usePathname();
  const user = useAuthStore((s) => s.user);
  const displayName = user?.full_name || "Employee";
  const initials = user?.full_name
    ? user.full_name
        .split(" ")
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0]?.toUpperCase())
        .join("")
    : "E";

  return (
    <aside className="hidden lg:flex w-64 flex-col border-r border-[#E2E8F0] bg-white shrink-0">
      {/* Navigation Links list */}
      <nav className="flex-1 space-y-1 py-6 px-4">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3.5 rounded-xl px-4 py-3 text-sm font-bold transition-all duration-150 active:scale-[0.98]",
                isActive
                  ? "bg-[#EFF6FF] text-[#0052FF]"
                  : "text-[#64748B] hover:bg-[#F8FAFC] hover:text-[#0F172A]"
              )}
            >
              <span className={cn("shrink-0", isActive ? "text-[#0052FF]" : "text-[#64748B] group-hover:text-[#0F172A]")}>
                {item.icon}
              </span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* User profile card at the bottom */}
      <div className="p-4 border-t border-slate-100">
        <div className="flex items-center justify-between rounded-xl border border-slate-100 bg-[#F8FAFC] p-3 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-[#0052FF] text-xs font-bold">
              {initials}
            </div>
            <div className="flex flex-col text-left">
              <span className="text-xs font-bold text-[#0F172A]">{displayName}</span>
              <span className="text-[10px] font-semibold text-slate-400">—</span>
            </div>
          </div>
          <ChevronDown className="h-3.5 w-3.5 text-[#94A3B8]" />
        </div>
      </div>
    </aside>
  );
}
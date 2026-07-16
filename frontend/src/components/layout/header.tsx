import { useEffect, useState } from "react";
import Link from "next/link";
import { LogOut, Moon, Sun, Bell, Search, HelpCircle, ChevronDown } from "lucide-react";
import { useTheme } from "next-themes";
import { usePathname, useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/hooks/use-auth";
import { ROUTES } from "@/lib/constants";
import { cn } from "@/lib/cn";
import { Logo } from "@/components/auth/Logo";

export function Header() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const { user, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [query, setQuery] = useState("");

  useEffect(() => setMounted(true), []);

  const initials = user?.full_name
    ? user.full_name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
    : "AA";

  const handleSearchKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && query.trim()) {
      router.push(`${ROUTES.SEARCH}?q=${encodeURIComponent(query.trim())}`);
    }
  };

  // Determine top subtitle based on pathname to match CEO-approved mockups
  const isComplaintsRoute =
    pathname.startsWith("/complaints") ||
    pathname.startsWith("/live-alerts") ||
    pathname.startsWith("/interactions") ||
    pathname.startsWith("/customers") ||
    pathname.startsWith("/complaint-cases") ||
    pathname.startsWith("/analytics") ||
    pathname.startsWith("/reports") ||
    pathname.startsWith("/notifications") ||
    pathname.startsWith("/administration");

  const titleText = isComplaintsRoute ? "SMART Insurance AI Hub" : "SMART AI Hub";
  const subtitleText = isComplaintsRoute ? "Complaints & Sentiment Intelligence" : "Complaints & Sentiment";
  const isAdminRoute = pathname.startsWith("/administration");

  return (
    <header className="flex h-20 items-center justify-between border-b border-[#E2E8F0] bg-white px-6 shrink-0 shadow-[0_2px_15px_rgb(0,0,0,0.01)]">
      {/* Left side: Logo & Subtitle */}
      <div className="flex items-center">
        <Link href={ROUTES.DASHBOARD} className="hover:opacity-95 transition-opacity">
          <Logo iconOnly={true} />
        </Link>
        <div className="flex flex-col -space-y-1.5 ml-2.5 text-left">
          <span className="text-lg font-bold tracking-tight text-[#0F172A]">LuMay</span>
          <span className="text-[11px] font-semibold tracking-wider text-[#10B981] uppercase">Insurance</span>
        </div>

        <div className="mx-4 h-8 w-[1px] bg-slate-200" />
        
        <div className="flex flex-col -space-y-1 text-left">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
            {titleText}
          </span>
          <span className="text-sm font-semibold tracking-tight text-[#475569]">
            {subtitleText}
          </span>
        </div>
      </div>

      {/* Middle: Styled Search Bar */}
      <div className="relative flex-1 max-w-lg mx-8 hidden md:block">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#94A3B8]" />
        <input
          type="text"
          placeholder="Search complaints, customers, cases..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleSearchKeyDown}
          className="flex h-11 w-full rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] pl-10 pr-4 text-sm text-[#0F172A] placeholder:text-[#94A3B8] outline-none transition-all focus:border-[#2563EB] focus:bg-white focus:ring-1 focus:ring-[#2563EB]"
        />
      </div>

      {/* Right side: Help, Bell, User profile */}
      <div className="flex items-center gap-4">
        {/* Help Center */}
        <button className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-100 bg-white text-slate-400 hover:text-slate-600 hover:border-slate-200 transition-all shadow-sm">
          <HelpCircle className="h-5 w-5" />
        </button>

        {/* Bell Alert */}
        <button className="relative flex h-10 w-10 items-center justify-center rounded-xl border border-slate-100 bg-white text-slate-400 hover:text-slate-600 hover:border-slate-200 transition-all shadow-sm">
          <Bell className="h-5 w-5" />
          <span className="absolute -top-1.5 -right-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-[10px] font-bold text-white shadow-sm ring-2 ring-white animate-pulse">
            5
          </span>
        </button>

        {/* User Profile dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-3 rounded-xl border border-slate-100 bg-white p-1.5 pr-3 hover:border-slate-200 transition-all shadow-sm text-left active:scale-[0.98]">
              <Avatar className="h-8 w-8 rounded-lg bg-blue-50 text-[#0052FF] font-bold">
                <AvatarFallback className="rounded-lg bg-blue-50 text-[#0052FF] text-xs font-bold">
                  {initials}
                </AvatarFallback>
              </Avatar>
              <div className="hidden lg:flex flex-col -space-y-1">
                <span className="text-xs font-bold text-[#0F172A]">
                  {user?.full_name ?? "Ahmed Al Badi"}
                </span>
                <span className="text-[10px] font-medium text-[#64748B]">
                  {isAdminRoute ? "System Administrator" : "Complaint Officer"}
                </span>
              </div>
              <ChevronDown className="h-3.5 w-3.5 text-[#94A3B8]" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56 rounded-xl shadow-lg border-[#E2E8F0]">
            <DropdownMenuLabel className="p-3">
              <div className="flex flex-col">
                <span className="text-sm font-bold text-[#0F172A]">{user?.full_name ?? "Ahmed Al Badi"}</span>
                <span className="text-xs font-medium text-[#64748B]">{user?.email ?? "ahmed.albadi@lumay.ai"}</span>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-slate-100" />
            
            {/* Theme switcher inside dropdown */}
            {mounted && (
              <DropdownMenuItem 
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                className="flex items-center justify-between p-2.5 text-slate-700 hover:bg-slate-50 rounded-lg cursor-pointer"
              >
                <span className="text-xs font-semibold">Toggle Theme</span>
                {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </DropdownMenuItem>
            )}
            
            <DropdownMenuSeparator className="bg-slate-100" />
            <DropdownMenuItem onClick={logout} className="p-2.5 text-red-600 font-semibold hover:bg-red-50 rounded-lg cursor-pointer flex items-center">
              <LogOut className="mr-2 h-4 w-4" />
              <span className="text-xs">Log out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
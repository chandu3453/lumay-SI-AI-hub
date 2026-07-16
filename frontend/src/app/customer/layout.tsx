"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Bell, CreditCard, FileText, MessageSquare, PhoneCall, RefreshCw, 
  ShieldCheck, Download, LogOut, Search, Home, FileDigit, AlertTriangle,
  User, HelpCircle, Bot, Sparkles
} from "lucide-react";

type CustomerSession = { email: string; name: string };

export default function CustomerLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [session, setSession] = useState<CustomerSession | null>(null);
  const [showNotifications, setShowNotifications] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    if (pathname === "/customer/login") return;
    
    const s = sessionStorage.getItem("customer-session") || localStorage.getItem("customer-session");
    if (!s) {
      router.push("/customer/login");
      return;
    }
    setSession(JSON.parse(s));
  }, [pathname, router]);

  // Handle logout
  const handleLogout = () => {
    sessionStorage.removeItem("customer-session");
    localStorage.removeItem("customer-session");
    localStorage.removeItem("demo-role");
    router.push("/");
  };

  if (!isMounted) return null;

  // Don't render sidebar/header on login page
  if (pathname === "/customer/login") {
    return <>{children}</>;
  }

  // Must have a session to view portal pages
  if (!session) return null;

  const unreadNotifs = 3;

  const SidebarItem = ({ icon: Icon, label, href, badge = 0 }: any) => {
    // Basic active path matching
    const active = pathname === href || (href !== "/customer/dashboard" && pathname.startsWith(href));
    
    return (
      <Link href={href} className={`flex items-center justify-between px-4 py-3 rounded-xl transition-colors ${active ? "bg-blue-50 text-blue-600 font-bold" : "text-slate-600 hover:bg-slate-50 font-medium"}`}>
        <div className="flex items-center gap-3">
          <Icon className={`h-5 w-5 ${active ? "text-blue-600" : "text-slate-400"}`} />
          <span className="text-sm">{label}</span>
        </div>
        {badge > 0 && <span className="bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">{badge}</span>}
      </Link>
    );
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] font-sans antialiased text-[#0D1B3E] flex overflow-hidden">
      
      {/* ── LEFT SIDEBAR ── */}
      <aside className="w-64 bg-white border-r border-[#E2E8F0] flex flex-col justify-between hidden lg:flex shrink-0 h-screen overflow-y-auto">
        <div>
          <div className="p-6">
            <Link href="/customer/dashboard" className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-blue-100 text-[#0052FF] flex items-center justify-center">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <div>
                <span className="text-lg font-black tracking-tight leading-none block">LuMay</span>
                <span className="text-[10px] font-bold text-emerald-500 tracking-wider uppercase block">Insurance</span>
              </div>
            </Link>
          </div>
          <nav className="px-3 space-y-1 mt-2">
            <SidebarItem icon={Home} label="Dashboard" href="/customer/dashboard" />
            <SidebarItem icon={FileDigit} label="My Policies" href="/customer/policies" />
            <SidebarItem icon={FileText} label="My Claims" href="/customer/claims" />
            <SidebarItem icon={AlertTriangle} label="My Complaints" href="/customer/complaints" />
            <SidebarItem icon={MessageSquare} label="Communication" href="/customer/communication" />
            <SidebarItem icon={CreditCard} label="Payments" href="/customer/payments" />
            <SidebarItem icon={RefreshCw} label="Renewals" href="/customer/renewals" />
            <SidebarItem icon={Download} label="Documents" href="/customer/documents" />
            <SidebarItem icon={Bell} label="Notifications" href="/customer/notifications" badge={unreadNotifs} />
            <SidebarItem icon={User} label="Profile" href="/customer/profile" />
            <SidebarItem icon={HelpCircle} label="Support Center" href="/customer/support" />
          </nav>
        </div>
        
        <div className="p-4 mt-6">
          <div className="bg-slate-50 rounded-2xl p-4 border border-[#E2E8F0]">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="h-4 w-4 text-[#0052FF]" />
              <h4 className="text-sm font-bold text-[#0D1B3E]">LuMay VIP</h4>
            </div>
            <p className="text-xs text-slate-500 mb-1">Member since 2022</p>
            <p className="text-[10px] text-slate-400 mb-4">You are a valued<br/>VIP customer <span className="text-amber-500">👑</span></p>
            <button className="w-full bg-[#0052FF] hover:bg-blue-600 text-white text-xs font-bold py-2 rounded-xl transition-colors">
              Upgrade Benefits
            </button>
          </div>
        </div>
      </aside>

      {/* ── MAIN CONTENT AREA ── */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        
        {/* Header */}
        <header className="h-20 bg-white border-b border-[#E2E8F0] px-6 sm:px-8 flex items-center justify-between shrink-0">
          <div className="flex-1 max-w-xl">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input type="text" placeholder="Search policies, claims, docs..." className="w-full bg-slate-50 border border-[#E2E8F0] rounded-full pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:border-blue-300 focus:bg-white transition-all" />
            </div>
          </div>
          <div className="flex items-center gap-4 pl-4">
            <button onClick={() => setShowNotifications(!showNotifications)} className="relative p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-500">
              <Bell className="h-5 w-5" />
              {unreadNotifs > 0 && <span className="absolute top-0 right-0 h-4 w-4 rounded-full bg-red-500 text-[9px] font-bold text-white flex items-center justify-center border-2 border-white">{unreadNotifs}</span>}
            </button>
            <button onClick={handleLogout} className="flex items-center gap-2 hover:bg-slate-50 p-1.5 pr-3 rounded-full border border-transparent hover:border-[#E2E8F0] transition-all">
              <div className="h-8 w-8 rounded-full bg-blue-100 text-[#0052FF] flex items-center justify-center font-bold text-xs uppercase">
                {session.name.substring(0, 2)}
              </div>
              <div className="text-left hidden sm:block">
                <p className="text-xs font-bold text-[#0D1B3E]">{session.name}</p>
                <p className="text-[10px] text-slate-500">VIP Customer</p>
              </div>
            </button>
          </div>
        </header>

        {/* Scrollable Content */}
        <main className={`flex-1 ${pathname.includes("/communication") ? "overflow-hidden" : "overflow-y-auto"}`}>
          {children}
          {!pathname.includes("/communication") && <div className="h-16" />} {/* Bottom padding */}
        </main>
      </div>

      {/* Floating AI Widget */}
      {!pathname.includes("/communication") && (
        <Link href="/customer/communication/chat" className="fixed bottom-6 right-6 z-50">
          <div className="bg-[#002288] text-white rounded-2xl p-5 shadow-2xl w-72 flex flex-col items-center justify-center overflow-hidden relative group hover:scale-105 transition-transform">
            <div className="absolute inset-0 bg-gradient-to-tr from-blue-700 to-blue-900 opacity-50" />
            <div className="relative z-10 flex flex-col items-center">
              <h3 className="text-sm font-bold mb-1 text-center">LuMay AI is here for you</h3>
              <p className="text-[11px] text-blue-200 text-center mb-4 leading-tight">Get instant answers, 24/7<br/>from your AI assistant.</p>
              <div className="bg-white text-blue-700 text-xs font-bold px-5 py-2 rounded-full flex items-center gap-2 hover:bg-blue-50 transition-colors cursor-pointer">
                <MessageSquare className="h-4 w-4" /> Start Chat
              </div>
            </div>
            <div className="absolute right-4 -bottom-2 opacity-50 group-hover:opacity-100 transition-opacity">
              <Bot className="h-12 w-12 text-white" />
            </div>
          </div>
        </Link>
      )}

    </div>
  );
}

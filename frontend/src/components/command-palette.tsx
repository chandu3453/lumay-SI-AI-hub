"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/cn";
import { useDemoStore } from "@/stores/demo.store";
import {
  Search,
  LayoutDashboard,
  FolderKanban,
  Users,
  FileText,
  GitBranch,
  Bell,
  BarChart3,
  BookOpen,
  Settings,
  LogIn,
  MonitorPlay,
  RotateCcw,
  MessageSquare,
  ArrowUpRight,
  Flag,
  AlertTriangle,
  Gauge,
  Flame,
  type LucideIcon,
} from "lucide-react";

type Action = {
  id: string;
  label: string;
  description: string;
  icon: LucideIcon;
  route?: string;
  action?: () => void;
  category: string;
};

export function CommandPalette() {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedIdx, setSelectedIdx] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const demoEnabled = useDemoStore((s) => s.enabled);
  const setEnabled = useDemoStore((s) => s.setEnabled);
  const addEvent = useDemoStore((s) => s.addEvent);

  const actions: Action[] = [
    { id: "dashboard", label: "Dashboard", description: "View employee dashboard", icon: LayoutDashboard, route: "/dashboard", category: "Navigate" },
    { id: "complaint-cases", label: "Complaint Cases", description: "View and manage all complaint cases", icon: FolderKanban, route: "/complaint-cases", category: "Navigate" },
    { id: "customers", label: "Customers", description: "View customer directory", icon: Users, route: "/customers", category: "Navigate" },
    { id: "interactions", label: "Interactions", description: "View interaction log", icon: MessageSquare, route: "/interactions", category: "Navigate" },
    { id: "workflows", label: "Workflows", description: "View workflow engine", icon: GitBranch, route: "/workflow", category: "Navigate" },
    { id: "analytics", label: "Analytics", description: "View analytics dashboard", icon: BarChart3, route: "/analytics", category: "Navigate" },
    { id: "reports", label: "Reports", description: "View reports", icon: FileText, route: "/reports", category: "Navigate" },
    { id: "notifications", label: "Notifications", description: "View notifications", icon: Bell, route: "/notifications", category: "Navigate" },
    { id: "knowledge", label: "Knowledge Base", description: "Search knowledge base", icon: BookOpen, route: "/knowledge", category: "Navigate" },
    { id: "settings", label: "Settings", description: "System settings", icon: Settings, route: "/settings", category: "Navigate" },
    { id: "search", label: "Search Everything", description: "Enterprise search across all entities", icon: Search, route: "/search", category: "Actions" },
    { id: "customer-portal", label: "Customer Portal", description: "Open customer portal in new tab", icon: LogIn, route: "/customer/dashboard", category: "Actions" },
    { id: "complaint-queue", label: "Open Complaint Queue", description: "View and manage complaint queue", icon: FolderKanban, route: "/complaint-cases", category: "Actions" },
    { id: "assigned-cases", label: "Assigned Complaint Cases", description: "View cases assigned to you", icon: Flag, route: "/complaint-cases?assigned=me", category: "Actions" },
    { id: "high-priority", label: "High Priority Cases", description: "View high and critical priority cases", icon: AlertTriangle, route: "/complaint-cases?priority=high,critical", category: "Actions" },
    { id: "sla-dashboard", label: "SLA Dashboard", description: "View SLA performance and breaches", icon: Gauge, route: "/analytics?tab=sla", category: "Actions" },
    { id: "escalations", label: "Today's Escalations", description: "View today's escalated complaint cases", icon: Flame, route: "/complaint-cases?tab=escalated", category: "Actions" },
    ...(demoEnabled ? [
      { id: "demo-toggle", label: "Disable Demo Mode", description: "Turn off live simulation mode", icon: MonitorPlay, action: () => setEnabled(false), category: "Demo" },
    ] : [
      { id: "demo-toggle", label: "Enable Demo Mode", description: "Turn on live simulation mode", icon: MonitorPlay, action: () => setEnabled(true), category: "Demo" },
    ]),
    { id: "demo-reset", label: "Reset Demo Data", description: "Restore all demo data to initial state", icon: RotateCcw, route: "/demo/reset", category: "Demo" },
  ];

  const filtered = query.trim()
    ? actions.filter((a) => {
        const q = query.toLowerCase();
        return a.label.toLowerCase().includes(q) || a.description.toLowerCase().includes(q) || a.category.toLowerCase().includes(q);
      })
    : actions;

  const navigateTo = useCallback((action: Action) => {
    setOpen(false);
    setQuery("");
    if (action.action) {
      action.action();
    } else if (action.route) {
      if (action.id === "customer-portal") {
        window.open(action.route, "_blank");
      } else {
        router.push(action.route);
      }
    }
  }, [router]);

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((prev) => !prev);
        setSelectedIdx(0);
      }
      if (e.key === "Escape") {
        setOpen(false);
        setQuery("");
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  useEffect(() => {
    setSelectedIdx(0);
  }, [query]);

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIdx((prev) => Math.min(prev + 1, filtered.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIdx((prev) => Math.max(prev - 1, 0));
    } else if (e.key === "Enter" && filtered[selectedIdx]) {
      e.preventDefault();
      navigateTo(filtered[selectedIdx]);
    }
  }

  if (!open) return null;

  const categories = [...new Set(filtered.map((a) => a.category))];

  return (
    <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh]">
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" onClick={() => { setOpen(false); setQuery(""); }} />
      <div className="relative w-full max-w-2xl rounded-2xl border border-[#E2E8F0] bg-white shadow-2xl shadow-black/20 animate-in fade-in slide-in-from-top-4 duration-200">
        <div className="flex items-center border-b border-[#E2E8F0] px-4">
          <Search className="h-5 w-5 text-[#94A3B8] shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search pages, actions, and more..."
            className="flex-1 border-0 bg-transparent px-3 py-4 text-sm text-[#0F172A] outline-none placeholder:text-[#94A3B8]"
          />
          <kbd className="hidden sm:inline-flex items-center gap-1 rounded-md border border-[#E2E8F0] bg-[#F8FAFC] px-2 py-1 text-[10px] font-medium text-[#94A3B8]">
            ESC
          </kbd>
        </div>

        <div className="max-h-[400px] overflow-y-auto p-2">
          {filtered.length === 0 ? (
            <div className="flex flex-col items-center py-8 text-center">
              <Search className="mb-2 h-8 w-8 text-[#CBD5E1]" />
              <p className="text-sm font-medium text-[#64748B]">No results found</p>
              <p className="text-xs text-[#94A3B8] mt-1">Try a different search term</p>
            </div>
          ) : (
            categories.map((cat) => (
              <div key={cat}>
                <p className="px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-[#94A3B8]">
                  {cat}
                </p>
                {filtered
                  .filter((a) => a.category === cat)
                  .map((action, idx) => {
                    const globalIdx = filtered.indexOf(action);
                    const Icon = action.icon;
                    return (
                      <button
                        key={action.id}
                        onClick={() => navigateTo(action)}
                        onMouseEnter={() => setSelectedIdx(globalIdx)}
                        className={cn(
                          "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-colors",
                          globalIdx === selectedIdx
                            ? "bg-[#F1F5F9] text-[#0F172A]"
                            : "text-[#475569] hover:bg-[#F8FAFC]",
                        )}
                      >
                        <div className={cn(
                          "flex h-8 w-8 items-center justify-center rounded-lg",
                          globalIdx === selectedIdx ? "bg-white shadow-sm" : "bg-[#F8FAFC]",
                        )}>
                          <Icon className="h-4 w-4 text-[#64748B]" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-[#0F172A]">{action.label}</p>
                          <p className="text-xs text-[#94A3B8] truncate">{action.description}</p>
                        </div>
                        {action.route && (
                          <ArrowUpRight className="h-3.5 w-3.5 text-[#CBD5E1]" />
                        )}
                      </button>
                    );
                  })}
              </div>
            ))
          )}
        </div>

        <div className="border-t border-[#E2E8F0] px-4 py-2">
          <div className="flex items-center gap-4 text-[10px] text-[#94A3B8]">
            <span><kbd className="rounded border border-[#E2E8F0] px-1.5 py-0.5 text-[10px]">↑↓</kbd> Navigate</span>
            <span><kbd className="rounded border border-[#E2E8F0] px-1.5 py-0.5 text-[10px]">↵</kbd> Open</span>
            <span><kbd className="rounded border border-[#E2E8F0] px-1.5 py-0.5 text-[10px]">Esc</kbd> Close</span>
          </div>
        </div>
      </div>
    </div>
  );
}



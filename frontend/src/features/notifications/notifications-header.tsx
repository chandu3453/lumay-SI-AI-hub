import { Settings } from "lucide-react";

export function NotificationsHeader() {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-5">
      <div className="space-y-0.5 text-left">
        <h1 className="text-2xl font-extrabold tracking-tight text-[#0F172A]">Notifications</h1>
        <p className="text-sm font-medium text-[#64748B]">Stay updated on alerts, case activities and system updates.</p>
      </div>
      
      <div className="flex items-center gap-3">
        <button className="flex h-10 items-center justify-center rounded-xl border border-slate-200 bg-white px-4 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-all shadow-sm">
          <span>Mark all as read</span>
        </button>
        <button className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-all shadow-sm">
          <Settings className="h-4.5 w-4.5" />
        </button>
      </div>
    </div>
  );
}
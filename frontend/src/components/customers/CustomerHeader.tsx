import { Download } from "lucide-react";

export function CustomerHeader() {
  return (
    <div className="flex items-center justify-between w-full border-b border-slate-100 pb-5">
      <div className="space-y-0.5 text-left">
        <h1 className="text-2xl font-extrabold tracking-tight text-[#0F172A]">Customers</h1>
        <p className="text-sm font-medium text-[#64748B]">View customer profiles, interaction history, and complaint overview.</p>
      </div>
      
      {/* Export Action Button */}
      <button className="flex h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-all shadow-sm">
        <Download className="h-4 w-4 text-[#94A3B8]" />
        <span>Export</span>
      </button>
    </div>
  );
}
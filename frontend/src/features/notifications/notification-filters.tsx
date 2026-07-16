import { Calendar } from "lucide-react";

type FiltersState = {
  types: string[];
  priorities: string[];
  channels: string[];
  dateRange: string;
};

type NotificationFiltersProps = {
  filters: FiltersState;
  onChange: (filters: FiltersState) => void;
};

export function NotificationFilters({ filters, onChange }: NotificationFiltersProps) {
  const applyFilters = () => onChange(filters);
  const resetFilters = () => {
    onChange({ types: [], priorities: [], channels: [], dateRange: "7d" });
  };

  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm space-y-5 text-left w-full">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <h3 className="text-sm font-extrabold text-[#0F172A]">Filters</h3>
        <button onClick={resetFilters} className="text-xs font-bold text-[#0052FF] hover:underline">
          Clear all
        </button>
      </div>

      {/* Type */}
      <div className="space-y-2">
        <h4 className="text-xs font-bold text-[#0F172A] uppercase tracking-wider">Type</h4>
        <div className="space-y-1.5 font-bold text-slate-500 text-xs">
          {[
            { id: "alerts", label: "Alerts", count: 4, checked: true },
            { id: "case_updates", label: "Case Updates", count: 5, checked: true },
            { id: "sla_deadlines", label: "SLA & Deadlines", count: 2, checked: true },
            { id: "system", label: "System", count: 1, checked: true },
          ].map((item) => (
            <label key={item.id} className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                defaultChecked={item.checked}
                className="rounded border-[#CBD5E1] text-[#0052FF] focus:ring-[#0052FF] h-3.5 w-3.5"
              />
              <span>{item.label}</span>
              <span className="text-slate-400 font-semibold ml-auto">{item.count}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Priority */}
      <div className="space-y-2">
        <h4 className="text-xs font-bold text-[#0F172A] uppercase tracking-wider">Priority</h4>
        <div className="space-y-1.5 font-bold text-slate-500 text-xs">
          {[
            { id: "high", label: "High", count: 3, checked: true },
            { id: "medium", label: "Medium", count: 4, checked: true },
            { id: "low", label: "Low", count: 5, checked: false },
          ].map((item) => (
            <label key={item.id} className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                defaultChecked={item.checked}
                className="rounded border-[#CBD5E1] text-[#0052FF] focus:ring-[#0052FF] h-3.5 w-3.5"
              />
              <span>{item.label}</span>
              <span className="text-slate-400 font-semibold ml-auto">{item.count}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Channel */}
      <div className="space-y-2">
        <h4 className="text-xs font-bold text-[#0F172A] uppercase tracking-wider">Channel</h4>
        <div className="space-y-1.5 font-bold text-slate-500 text-xs">
          {[
            { id: "voice", label: "Voice Call", count: 2, checked: false },
            { id: "whatsapp", label: "WhatsApp", count: 3, checked: false },
            { id: "email", label: "Email", count: 2, checked: false },
            { id: "web_chat", label: "Web Chat", count: 2, checked: false },
            { id: "smart_call", label: "SMART CALL", count: 1, checked: false },
            { id: "survey", label: "Survey", count: 1, checked: false },
            { id: "crm_manual", label: "CRM / Manual", count: 1, checked: false },
          ].map((item) => (
            <label key={item.id} className="flex items-center gap-2 cursor-pointer select-none">
              <input
                type="checkbox"
                defaultChecked={item.checked}
                className="rounded border-[#CBD5E1] text-[#0052FF] focus:ring-[#0052FF] h-3.5 w-3.5"
              />
              <span>{item.label}</span>
              <span className="text-slate-400 font-semibold ml-auto">{item.count}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Date Range */}
      <div className="space-y-2">
        <h4 className="text-xs font-bold text-[#0F172A] uppercase tracking-wider">Date Range</h4>
        <div className="relative">
          <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#94A3B8] pointer-events-none" />
          <select
            defaultValue="7d"
            className="w-full text-xs font-bold border border-[#E2E8F0] rounded-xl pl-9 pr-8 h-10 bg-white text-[#334155] focus:outline-none focus:border-[#2563EB] cursor-pointer appearance-none shadow-sm"
          >
            <option value="today">Today</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-[#64748B]" />
        </div>
      </div>

      {/* Apply Filters Button */}
      <button
        onClick={applyFilters}
        className="w-full h-10 rounded-xl bg-[#0052FF] text-xs font-bold text-white shadow-md hover:bg-blue-700 transition-all active:scale-[0.98]"
      >
        Apply Filters
      </button>
    </div>
  );
}
import { Search, Calendar } from "lucide-react";

type ComplaintCaseFiltersProps = {
  search: string; onSearchChange: (v: string) => void;
  channel: string; onChannelChange: (v: string) => void;
  theme: string; onThemeChange: (v: string) => void;
  severity: string; onSeverityChange: (v: string) => void;
  slaStatus: string; onSlaStatusChange: (v: string) => void;
  assignedTo: string; onAssignedToChange: (v: string) => void;
  dateFrom: string; dateTo: string; onDateFromChange: (v: string) => void; onDateToChange: (v: string) => void;
  onClear: () => void; onApply: () => void;
};

const selectClass = "h-10 rounded-xl border border-[#E2E8F0] bg-white px-3.5 text-xs font-bold text-[#334155] focus:outline-none focus:border-[#2563EB] shadow-sm cursor-pointer appearance-none pr-8 relative";

export function ComplaintCaseFilters({
  search, onSearchChange, channel, onChannelChange, theme, onThemeChange,
  severity, onSeverityChange, slaStatus, onSlaStatusChange, assignedTo, onAssignedToChange,
  dateFrom, dateTo, onDateFromChange, onDateToChange, onClear, onApply,
}: ComplaintCaseFiltersProps) {
  return (
    <div className="flex flex-wrap items-center gap-3.5 bg-white border border-[#E2E8F0] rounded-2xl p-4.5 shadow-sm text-left w-full">
      {/* Search Input */}
      <div className="relative w-full sm:w-44">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#94A3B8]" />
        <input
          type="text"
          placeholder="Search cases..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="h-10 w-full rounded-xl border border-[#E2E8F0] pl-10 pr-4 text-xs font-bold text-[#0F172A] placeholder:text-[#94A3B8] outline-none focus:border-[#2563EB]"
        />
      </div>

      {/* Channel Select */}
      <div className="relative">
        <select value={channel} onChange={(e) => onChannelChange(e.target.value)} className={selectClass}>
          <option value="">All Channels</option>
          <option value="voice">Voice Call</option>
          <option value="whatsapp">WhatsApp</option>
          <option value="email">Email</option>
          <option value="web_chat">Web Chat</option>
          <option value="mobile_chat">Mobile Chat</option>
        </select>
        <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-[#64748B]" />
      </div>

      {/* Theme Select */}
      <div className="relative">
        <select value={theme} onChange={(e) => onThemeChange(e.target.value)} className={selectClass}>
          <option value="">All Themes</option>
          <option value="claim_delays">Claim Delays</option>
          <option value="service_quality">Service Quality</option>
          <option value="communication">Communication</option>
          <option value="policy_coverage">Policy & Coverage</option>
          <option value="payments_refunds">Payments & Refunds</option>
          <option value="garage">Provider / Garage</option>
        </select>
        <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-[#64748B]" />
      </div>

      {/* Severity Select */}
      <div className="relative">
        <select value={severity} onChange={(e) => onSeverityChange(e.target.value)} className={selectClass}>
          <option value="">All Severity</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-[#64748B]" />
      </div>

      {/* SLA Status Select */}
      <div className="relative">
        <select value={slaStatus} onChange={(e) => onSlaStatusChange(e.target.value)} className={selectClass}>
          <option value="">All SLA Status</option>
          <option value="on_track">On Track</option>
          <option value="at_risk">At Risk</option>
          <option value="overdue">Overdue</option>
        </select>
        <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-[#64748B]" />
      </div>

      {/* Assigned To Select */}
      <div className="relative">
        <select value={assignedTo} onChange={(e) => onAssignedToChange(e.target.value)} className={selectClass}>
          <option value="">Assigned To</option>
          <option value="me">Assigned to Me</option>
          <option value="unassigned">Unassigned</option>
        </select>
        <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-[#64748B]" />
      </div>

      {/* Date Picker Input */}
      <div className="relative flex items-center gap-1.5 rounded-xl border border-[#E2E8F0] px-3.5 h-10 bg-white shadow-sm w-full sm:w-auto">
        <Calendar className="h-4 w-4 text-[#94A3B8] shrink-0" />
        <input
          type="date"
          value={dateFrom}
          onChange={(e) => onDateFromChange(e.target.value)}
          className="text-xs font-bold text-[#334155] outline-none bg-transparent cursor-pointer w-24"
        />
        <span className="text-xs font-bold text-[#94A3B8]">—</span>
        <input
          type="date"
          value={dateTo}
          onChange={(e) => onDateToChange(e.target.value)}
          className="text-xs font-bold text-[#334155] outline-none bg-transparent cursor-pointer w-24"
        />
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 ml-auto">
        <button
          onClick={onClear}
          className="h-10 rounded-xl border border-[#E2E8F0] bg-white px-4.5 text-xs font-bold text-[#64748B] shadow-sm hover:bg-[#F8FAFC] transition-all"
        >
          Clear
        </button>
        <button
          onClick={onApply}
          className="h-10 rounded-xl bg-[#0052FF] px-5 text-xs font-bold text-white shadow-md hover:bg-blue-700 transition-all active:scale-[0.98]"
        >
          Apply
        </button>
      </div>
    </div>
  );
}
import { Search, Calendar } from "lucide-react";

type CustomerFiltersProps = {
  search: string;
  onSearchChange: (value: string) => void;
  segment: string;
  onSegmentChange: (value: string) => void;
  riskLevel: string;
  onRiskLevelChange: (value: string) => void;
  customerType: string;
  onCustomerTypeChange: (value: string) => void;
  dateFrom: string;
  dateTo: string;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onClear: () => void;
  onApply: () => void;
};

const selectClass = "h-10 rounded-xl border border-[#E2E8F0] bg-white px-3.5 text-xs font-bold text-[#334155] focus:outline-none focus:border-[#2563EB] shadow-sm cursor-pointer appearance-none pr-8 relative";

export function CustomerFilters({
  search,
  onSearchChange,
  segment,
  onSegmentChange,
  riskLevel,
  onRiskLevelChange,
  customerType,
  onCustomerTypeChange,
  dateFrom,
  dateTo,
  onDateFromChange,
  onDateToChange,
  onClear,
  onApply,
}: CustomerFiltersProps) {
  return (
    <div className="flex flex-wrap items-center gap-3.5 bg-white border border-[#E2E8F0] rounded-2xl p-4.5 shadow-sm text-left">
      {/* Search Input */}
      <div className="relative w-full sm:w-56">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#94A3B8]" />
        <input
          type="text"
          placeholder="Search customers..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="h-10 w-full rounded-xl border border-[#E2E8F0] pl-10 pr-4 text-xs font-bold text-[#0F172A] placeholder:text-[#94A3B8] outline-none focus:border-[#2563EB]"
        />
      </div>

      {/* Segment Select */}
      <div className="relative">
        <select value={segment} onChange={(e) => onSegmentChange(e.target.value)} className={selectClass}>
          <option value="">All Segments</option>
          <option value="individual">Individual</option>
          <option value="corporate">Corporate</option>
          <option value="sme">SME</option>
          <option value="vip">VIP</option>
        </select>
        <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-[#64748B]" />
      </div>

      {/* Risk Level Select */}
      <div className="relative">
        <select value={riskLevel} onChange={(e) => onRiskLevelChange(e.target.value)} className={selectClass}>
          <option value="">All Risk Levels</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
        <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-[#64748B]" />
      </div>

      {/* Customer Type Select */}
      <div className="relative">
        <select value={customerType} onChange={(e) => onCustomerTypeChange(e.target.value)} className={selectClass}>
          <option value="">All Customer Types</option>
          <option value="new">New</option>
          <option value="existing">Existing</option>
          <option value="vip">VIP</option>
          <option value="former">Former</option>
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
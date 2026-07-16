import { ChevronRight, Grid, List } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import type { Customer } from "@/types/domain";

const MOCK_CUSTOMERS = [
  {
    id: "CUST-000198",
    full_name: "Mohammed Al Hinai",
    email: "m.hinai@email.com",
    mobile_number: "+968 9123 4567",
    risk_level: "high",
    complaint_count: 5,
    last_interaction: "May 16, 2025 / 10:24 AM",
    initials: "MH",
  },
  {
    id: "CUST-000199",
    full_name: "Fatima Al Lawati",
    email: "f.lawati@email.com",
    mobile_number: "+968 9876 5432",
    risk_level: "high",
    complaint_count: 3,
    last_interaction: "May 16, 2025 / 10:21 AM",
    initials: "FL",
  },
  {
    id: "CUST-000200",
    full_name: "Sultan Al Khaldi",
    email: "s.khaldi@email.com",
    mobile_number: "+968 9012 3456",
    risk_level: "medium",
    complaint_count: 2,
    last_interaction: "May 16, 2025 / 10:14 AM",
    initials: "SK",
  },
  {
    id: "CUST-000201",
    full_name: "Aisha Al Raisi",
    email: "a.alraisi@email.com",
    mobile_number: "+968 9345 6789",
    risk_level: "medium",
    complaint_count: 2,
    last_interaction: "May 16, 2025 / 10:08 AM",
    initials: "AR",
  },
  {
    id: "CUST-000202",
    full_name: "Hamed Al Balushi",
    email: "h.balushi@email.com",
    mobile_number: "+968 9120 6789",
    risk_level: "low",
    complaint_count: 1,
    last_interaction: "May 16, 2025 / 09:59 AM",
    initials: "HB",
  },
  {
    id: "CUST-000203",
    full_name: "Salma Al Maqbali",
    email: "s.maqbali@email.com",
    mobile_number: "+968 9099 1122",
    risk_level: "high",
    complaint_count: 4,
    last_interaction: "May 16, 2025 / 09:41 AM",
    initials: "SM",
  },
  {
    id: "CUST-000204",
    full_name: "Yousef Al Harthy",
    email: "y.harthy@email.com",
    mobile_number: "+968 9988 7766",
    risk_level: "low",
    complaint_count: 0,
    last_interaction: "May 16, 2025 / 09:32 AM",
    initials: "YH",
  },
  {
    id: "CUST-000205",
    full_name: "Ahmed Al Hadi",
    email: "a.hadi@email.com",
    mobile_number: "+968 9444 2211",
    risk_level: "medium",
    complaint_count: 1,
    last_interaction: "May 16, 2025 / 09:18 AM",
    initials: "AA",
  },
  {
    id: "CUST-000206",
    full_name: "Maryam Al Farsi",
    email: "m.farsi@email.com",
    mobile_number: "+968 9566 8877",
    risk_level: "high",
    complaint_count: 6,
    last_interaction: "May 16, 2025 / 08:55 AM",
    initials: "MF",
  },
  {
    id: "CUST-000207",
    full_name: "Rashid Al Zadjali",
    email: "r.zadjali@email.com",
    mobile_number: "+968 9222 3344",
    risk_level: "medium",
    complaint_count: 2,
    last_interaction: "May 16, 2025 / 08:41 AM",
    initials: "RZ",
  },
];

type CustomerTableProps = {
  data: Customer[];
  isLoading: boolean;
  total?: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  selectedId: string | null;
  onSelect: (customer: any) => void;
};

export function CustomerTable({ selectedId, onSelect }: CustomerTableProps) {
  return (
    <div className="flex flex-col bg-white border border-[#E2E8F0] rounded-2xl shadow-sm overflow-hidden text-left">
      {/* Sub header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-[#E2E8F0]">
        <span className="text-xs font-bold text-slate-400">Showing 1 to 10 of 24,568 customers</span>
        <div className="flex items-center gap-2">
          {/* Sort selection */}
          <div className="text-[10px] font-bold text-slate-400 mr-1 flex items-center gap-1">
            <span>Sort by:</span>
            <select className="bg-transparent text-slate-600 outline-none cursor-pointer">
              <option>Recently Active</option>
              <option>Total Complaints</option>
            </select>
          </div>
          {/* List/Grid layout icons */}
          <div className="flex border border-slate-200 rounded-lg p-0.5">
            <button className="p-1 rounded bg-slate-100 text-slate-600">
              <List className="h-3.5 w-3.5" />
            </button>
            <button className="p-1 rounded text-slate-400 hover:text-slate-600">
              <Grid className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-[#E2E8F0] bg-[#F8FAFC]">
              {["Customer", "Contact", "Risk Level", "Complaints", "Last Interaction", ""].map((th) => (
                <th key={th} className="text-left text-[11px] font-bold text-[#64748B] px-5 py-4 tracking-tight uppercase">
                  {th}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E2E8F0]">
            {MOCK_CUSTOMERS.map((cust) => {
              const isSelected = selectedId === cust.id;
              return (
                <tr
                  key={cust.id}
                  onClick={() => onSelect(cust)}
                  className={`hover:bg-[#F8FAFC] transition-colors cursor-pointer ${
                    isSelected ? "bg-[#EFF6FF]" : ""
                  }`}
                >
                  {/* Customer initials avatar name & code */}
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-8 w-8 rounded-lg bg-blue-50 text-[#0052FF] font-bold">
                        <AvatarFallback className="rounded-lg bg-blue-50 text-[#0052FF] text-[10px] font-bold">
                          {cust.initials}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex flex-col -space-y-0.5">
                        <span className="text-xs font-bold text-[#0F172A]">{cust.full_name}</span>
                        <span className="text-[10px] font-bold text-slate-400">{cust.id}</span>
                      </div>
                    </div>
                  </td>

                  {/* Contact */}
                  <td className="px-5 py-4">
                    <div className="flex flex-col -space-y-0.5">
                      <span className="text-xs font-semibold text-[#334155]">{cust.mobile_number}</span>
                      <span className="text-[10px] font-bold text-slate-400">{cust.email}</span>
                    </div>
                  </td>

                  {/* Risk Level Badge */}
                  <td className="px-5 py-4">
                    {cust.risk_level === "high" ? (
                      <span className="rounded-lg bg-red-50 border border-red-100 px-2 py-0.5 text-[10px] font-bold text-red-600 capitalize">High</span>
                    ) : cust.risk_level === "medium" ? (
                      <span className="rounded-lg bg-amber-50 border border-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-600 capitalize">Medium</span>
                    ) : (
                      <span className="rounded-lg bg-green-50 border border-green-100 px-2 py-0.5 text-[10px] font-bold text-green-600 capitalize">Low</span>
                    )}
                  </td>

                  {/* Complaints Count */}
                  <td className="px-5 py-4 text-xs font-bold text-[#0052FF]">
                    {cust.complaint_count}
                  </td>

                  {/* Last Interaction */}
                  <td className="px-5 py-4 text-xs font-bold text-slate-500 whitespace-nowrap">
                    {cust.last_interaction}
                  </td>

                  {/* Chevron Right */}
                  <td className="px-5 py-4 text-right">
                    <ChevronRight className="h-4 w-4 text-[#94A3B8] ml-auto" />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="flex items-center justify-between px-5 py-4 bg-[#F8FAFC] border-t border-[#E2E8F0] text-xs font-bold text-slate-400">
        <div className="flex items-center gap-1">
          <button className="h-7 w-7 rounded-lg border border-slate-200 bg-white flex items-center justify-center text-slate-400 hover:text-slate-600 shadow-sm">&lt;</button>
          <button className="h-7 w-7 rounded-lg border border-slate-200 bg-[#EFF6FF] text-[#0052FF] flex items-center justify-center shadow-sm">1</button>
          <button className="h-7 w-7 rounded-lg border border-slate-200 bg-white flex items-center justify-center text-slate-500 hover:text-slate-600 shadow-sm">2</button>
          <button className="h-7 w-7 rounded-lg border border-slate-200 bg-white flex items-center justify-center text-slate-500 hover:text-slate-600 shadow-sm">3</button>
          <span className="px-1 text-slate-300">...</span>
          <button className="h-7 w-7 rounded-lg border border-slate-200 bg-white flex items-center justify-center text-slate-500 hover:text-slate-600 shadow-sm">2457</button>
          <button className="h-7 w-7 rounded-lg border border-slate-200 bg-white flex items-center justify-center text-slate-400 hover:text-slate-600 shadow-sm">&gt;</button>
        </div>
        <select className="h-7 rounded-lg border border-slate-200 bg-white px-2.5 outline-none cursor-pointer text-slate-500 shadow-sm">
          <option>10 / page</option>
          <option>20 / page</option>
          <option>50 / page</option>
        </select>
      </div>
    </div>
  );
}
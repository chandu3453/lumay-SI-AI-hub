import { MoreHorizontal, Edit, FileText } from "lucide-react";

export function ScheduledReportsTable() {
  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl shadow-sm text-left overflow-hidden w-full">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-[#F1F5F9] bg-white">
        <h3 className="text-sm font-bold text-[#0F172A] tracking-tight">Upcoming Scheduled Reports</h3>
        <button className="text-xs font-bold text-[#0052FF] hover:underline transition-all">
          View All Scheduled Reports
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] border-collapse text-left">
          <thead>
            <tr className="border-b border-[#F1F5F9] bg-[#F8FAFC] text-[10px] font-extrabold uppercase tracking-wider text-slate-400">
              <th className="px-5 py-4">Report</th>
              <th className="px-5 py-4">Frequency</th>
              <th className="px-5 py-4">Next Run</th>
              <th className="px-5 py-4">Format</th>
              <th className="px-5 py-4">Recipients</th>
              <th className="px-5 py-4">Status</th>
              <th className="px-5 py-4 w-24 text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#F1F5F9] text-xs font-bold text-[#0F172A]">
            <tr className="hover:bg-[#F8FAFC] transition-colors">
              <td className="px-5 py-3.5">
                <span className="text-xs font-bold text-[#0F172A] block">Daily High Risk Alert Report</span>
                <span className="text-[10px] font-bold text-slate-400 mt-0.5 block">Daily summary of high risk and escalated complaints.</span>
              </td>
              <td className="px-5 py-3.5 text-[#475569] font-semibold">
                Daily
              </td>
              <td className="px-5 py-3.5 text-[#475569]">
                May 17, 2025 08:00 AM
              </td>
              <td className="px-5 py-3.5">
                <span className="inline-flex items-center gap-1 text-[10px] font-bold text-red-600 bg-red-50 border border-red-100 rounded-lg px-2.5 py-0.5">
                  <FileText className="h-3 w-3 shrink-0" />
                  PDF
                </span>
              </td>
              <td className="px-5 py-3.5 text-[#475569]">
                complaints@lumay.com + 4 more
              </td>
              <td className="px-5 py-3.5">
                <span className="inline-flex items-center gap-1.5 rounded-lg bg-green-50 border border-green-100 px-2.5 py-0.5 text-[10px] font-bold text-[#10B981]">
                  <div className="h-1.5 w-1.5 rounded-full bg-[#10B981]" />
                  Active
                </span>
              </td>
              <td className="px-5 py-3.5 text-center">
                <div className="flex items-center justify-center gap-2">
                  <button className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-all shadow-sm">
                    <Edit className="h-3.5 w-3.5" />
                  </button>
                  <button className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-all shadow-sm">
                    <MoreHorizontal className="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
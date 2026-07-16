import { Clock, Users, GitBranch, FolderPlus, Settings } from "lucide-react";

// TODO: Replace with API-driven type once the activity log endpoint is available
type MockActivity = {
  icon: React.ReactNode;
  iconBg: string;
  iconColor: string;
  activity: string;
  details: string;
  user: string;
  initials: string;
  userBg: string;
  timestamp: string;
  status: string;
};

// Will be populated from the API — kept as an empty placeholder until integration
const ACTIVITIES: MockActivity[] = [];

export function ActivityTable() {
  return (
    <div className="space-y-4 text-left w-full">
      <h3 className="text-sm font-bold text-[#0F172A] tracking-tight">Recent System Activity</h3>
      
      <div className="bg-white border border-[#E2E8F0] rounded-2xl shadow-sm overflow-hidden flex flex-col w-full">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] border-collapse">
            <thead>
              <tr className="border-b border-[#F1F5F9] bg-[#F8FAFC] text-[10px] font-extrabold uppercase tracking-wider text-slate-400">
                <th className="px-5 py-4 w-60">Activity</th>
                <th className="px-5 py-4">Details</th>
                <th className="px-5 py-4 w-52">User</th>
                <th className="px-5 py-4 w-48">Date & Time</th>
                <th className="px-5 py-4 w-28">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9] text-xs font-bold text-[#0F172A]">
              {ACTIVITIES.map((row, idx) => (
                <tr key={idx} className="hover:bg-[#F8FAFC] transition-colors">
                  <td className="px-5 py-3.5 flex items-center gap-2.5">
                    <div className={`h-8 w-8 rounded-lg shrink-0 flex items-center justify-center border ${row.iconBg} ${row.iconColor}`}>
                      {row.icon}
                    </div>
                    <span className="text-[#0F172A] font-bold">{row.activity}</span>
                  </td>
                  <td className="px-5 py-3.5 text-slate-400 font-semibold max-w-[340px] truncate">
                    {row.details}
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2">
                      <div className={`h-6 w-6 rounded-full shrink-0 flex items-center justify-center text-[9px] font-bold text-white ${row.userBg}`}>
                        {row.initials}
                      </div>
                      <span className="text-[#475569]">{row.user}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3.5 text-[#475569]">
                    {row.timestamp}
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="inline-flex items-center gap-1.5 rounded-lg bg-green-50 border border-green-100 px-2.5 py-0.5 text-[10px] font-bold text-[#10B981]">
                      <div className="h-1.5 w-1.5 rounded-full bg-[#10B981]" />
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-[#F1F5F9] px-5 py-3 bg-white text-xs font-bold text-[#64748B]">
          <span>Showing 1 to 5 of 25 activities</span>
          <button className="h-8.5 px-4 flex items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 transition-all shadow-sm">
            View All Activity
          </button>
        </div>
      </div>
    </div>
  );
}
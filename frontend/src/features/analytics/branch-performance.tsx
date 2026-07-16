type BranchItem = {
  name: string;
  total: number;
  highRisk: number;
  resolved: number;
  slaBreachRate: number;
  progressBarColor: string;
};

const MOCK_BRANCHES: BranchItem[] = [
  { name: "Muscat", total: 568, highRisk: 82, resolved: 412, slaBreachRate: 8, progressBarColor: "bg-red-500" },
  { name: "Salalah", total: 412, highRisk: 54, resolved: 298, slaBreachRate: 6, progressBarColor: "bg-orange-400" },
  { name: "Sohar", total: 298, highRisk: 36, resolved: 214, slaBreachRate: 5, progressBarColor: "bg-orange-400" },
  { name: "Nizwa", total: 246, highRisk: 28, resolved: 176, slaBreachRate: 3, progressBarColor: "bg-yellow-400" },
  { name: "Sur", total: 194, highRisk: 18, resolved: 138, slaBreachRate: 0, progressBarColor: "bg-slate-200" },
];

export function BranchPerformance() {
  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm text-left">
      <h3 className="text-sm font-bold text-[#0F172A] tracking-tight mb-4.5">Top Branches by Complaint Volume</h3>
      
      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-100 text-slate-400 font-bold">
              <th className="py-2.5">Branch</th>
              <th className="py-2.5 text-right">Total Complaints</th>
              <th className="py-2.5 text-right">High Risk</th>
              <th className="py-2.5 text-right">Resolved</th>
              <th className="py-2.5 text-right w-40">SLA Breach Rate</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-[#0F172A] font-bold">
            {MOCK_BRANCHES.map((b) => (
              <tr key={b.name} className="hover:bg-slate-50 transition-colors">
                <td className="py-3">{b.name}</td>
                <td className="py-3 text-right">{b.total}</td>
                <td className="py-3 text-right text-red-600">{b.highRisk}</td>
                <td className="py-3 text-right text-[#10B981]">{b.resolved}</td>
                <td className="py-3 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <span className="text-[10px] text-slate-500 w-6 text-right">{b.slaBreachRate}%</span>
                    <div className="h-1.5 w-16 bg-slate-100 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full ${b.progressBarColor}`} style={{ width: `${b.slaBreachRate * 8}%` }} />
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
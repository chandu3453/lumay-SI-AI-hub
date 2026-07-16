import { TrendingUp, ArrowUp } from "lucide-react";
import { LineChart, Line, ResponsiveContainer } from "recharts";

type IssueItem = {
  issue: string;
  relatedCases: number;
  trend: number;
  sparklineData: { value: number }[];
};

const MOCK_ISSUES: IssueItem[] = [
  {
    issue: "Delay in Claim Settlement",
    relatedCases: 512,
    trend: 18,
    sparklineData: [{ value: 10 }, { value: 15 }, { value: 13 }, { value: 20 }, { value: 18 }, { value: 25 }],
  },
  {
    issue: "Poor Provider / Garage Service",
    relatedCases: 398,
    trend: 12,
    sparklineData: [{ value: 8 }, { value: 10 }, { value: 14 }, { value: 12 }, { value: 16 }, { value: 19 }],
  },
  {
    issue: "Refund Processing Delay",
    relatedCases: 344,
    trend: 10,
    sparklineData: [{ value: 15 }, { value: 12 }, { value: 10 }, { value: 16 }, { value: 14 }, { value: 22 }],
  },
  {
    issue: "Communication Gaps",
    relatedCases: 270,
    trend: 6,
    sparklineData: [{ value: 20 }, { value: 18 }, { value: 15 }, { value: 19 }, { value: 17 }, { value: 21 }],
  },
  {
    issue: "Policy Coverage Disputes",
    relatedCases: 221,
    trend: 8,
    sparklineData: [{ value: 5 }, { value: 12 }, { value: 8 }, { value: 14 }, { value: 11 }, { value: 16 }],
  },
];

export function RecurringIssues() {
  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm text-left">
      <h3 className="text-sm font-bold text-[#0F172A] tracking-tight mb-4.5">Recurring Issues (Top 5)</h3>
      
      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-100 text-slate-400 font-bold">
              <th className="py-2.5">Issue</th>
              <th className="py-2.5 text-right">Related Cases</th>
              <th className="py-2.5 text-right">Trend</th>
              <th className="py-2.5 text-right w-28">Trend Line</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-[#0F172A] font-bold">
            {MOCK_ISSUES.map((item) => (
              <tr key={item.issue} className="hover:bg-slate-50 transition-colors">
                <td className="py-3.5">{item.issue}</td>
                <td className="py-3.5 text-right">{item.relatedCases}</td>
                <td className="py-3.5 text-right">
                  <span className="inline-flex items-center gap-0.5 text-red-600 font-bold">
                    <ArrowUp className="h-3 w-3 stroke-[2.5]" />
                    {item.trend}%
                  </span>
                </td>
                <td className="py-3.5">
                  <div className="h-7 w-20 ml-auto">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={item.sparklineData}>
                        <Line
                          type="monotone"
                          dataKey="value"
                          stroke="#EF4444"
                          strokeWidth={1.5}
                          dot={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
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
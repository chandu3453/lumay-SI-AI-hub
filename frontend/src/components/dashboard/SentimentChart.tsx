import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

const MOCK_DATA = [
  { name: "Positive", value: 52, color: "#10B981" },
  { name: "Neutral", value: 28, color: "#F59E0B" },
  { name: "Negative", value: 20, color: "#EF4444" },
];

export function SentimentChart() {
  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-sm flex flex-col h-96">
      {/* Title */}
      <h3 className="text-sm font-bold text-[#0F172A] tracking-tight mb-6">Sentiment Overview</h3>

      {/* Content wrapper */}
      <div className="flex flex-col items-center justify-center flex-1 gap-6 sm:flex-row lg:flex-col xl:flex-row">
        {/* Donut Chart */}
        <div className="h-36 w-36 shrink-0 relative">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={MOCK_DATA}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={36}
                outerRadius={56}
                paddingAngle={0}
              >
                {MOCK_DATA.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend */}
        <div className="flex-1 w-full space-y-3.5">
          {MOCK_DATA.map((entry) => (
            <div key={entry.name} className="flex items-center justify-between text-xs font-bold">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
                <span className="text-[#64748B]">{entry.name}</span>
              </div>
              <span className="text-[#0F172A]">{entry.value}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid } from "recharts";

type ComplaintTrendChartProps = {
  data: { month: string; count: number }[];
  isLoading: boolean;
};

const MOCK_TREND = [
  { month: "Dec", count: 3 },
  { month: "Jan", count: 3.5 },
  { month: "Feb", count: 5.2 },
  { month: "Mar", count: 4.8 },
  { month: "Apr", count: 3.2 },
  { month: "May", count: 5 },
];

export function ComplaintTrendChart({ isLoading }: ComplaintTrendChartProps) {
  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm text-left flex flex-col h-52">
      <h3 className="text-xs font-bold text-[#0F172A] tracking-tight mb-4">Complaint Trend (Last 6 Months)</h3>
      
      <div className="flex-1 min-h-0 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={MOCK_TREND} margin={{ top: 5, right: 5, bottom: -5, left: -25 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
            <XAxis
              dataKey="month"
              tick={{ fontSize: 9, fill: "#94A3B8", fontWeight: "bold" }}
              axisLine={false}
              tickLine={false}
              dy={5}
            />
            <YAxis
              tick={{ fontSize: 9, fill: "#94A3B8", fontWeight: "bold" }}
              axisLine={false}
              tickLine={false}
              domain={[0, 8]}
              ticks={[0, 2, 4, 6, 8]}
              dx={-5}
            />
            <Tooltip
              contentStyle={{
                borderRadius: 8,
                border: "1px solid #E2E8F0",
                fontSize: 10,
                fontWeight: "bold",
              }}
            />
            <Line
              type="monotone"
              dataKey="count"
              stroke="#EF4444"
              strokeWidth={2}
              dot={{ r: 3, fill: "#EF4444", strokeWidth: 1 }}
              activeDot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
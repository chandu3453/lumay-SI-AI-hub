import { useState } from "react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

const MOCK_DATA = [
  { date: "May 10", value: 2100 },
  { date: "May 11", value: 2500 },
  { date: "May 12", value: 2400 },
  { date: "May 13", value: 3200 },
  { date: "May 14", value: 2950 },
  { date: "May 15", value: 3300 },
  { date: "May 16", value: 2800 },
];

export function TrendChart() {
  const [activeTab, setActiveTab] = useState<"this" | "last">("this");

  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-sm flex flex-col h-96">
      {/* Header with Switcher Tabs */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-sm font-bold text-[#0F172A] tracking-tight">Complaint Trend</h3>
        <div className="flex rounded-xl bg-slate-100 p-1">
          <button
            onClick={() => setActiveTab("this")}
            className={`rounded-lg px-3 py-1.5 text-xs font-bold transition-all ${
              activeTab === "this"
                ? "bg-white text-[#0052FF] shadow-sm"
                : "text-slate-500 hover:text-slate-900"
            }`}
          >
            This Week
          </button>
          <button
            onClick={() => setActiveTab("last")}
            className={`rounded-lg px-3 py-1.5 text-xs font-bold transition-all ${
              activeTab === "last"
                ? "bg-white text-[#0052FF] shadow-sm"
                : "text-slate-500 hover:text-slate-900"
            }`}
          >
            Last Week
          </button>
        </div>
      </div>

      {/* Chart container */}
      <div className="flex-1 min-h-0 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={MOCK_DATA} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="complaintTrendGlow" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563EB" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 10, fill: "#94A3B8", fontWeight: "bold" }}
              axisLine={false}
              tickLine={false}
              dy={10}
            />
            <YAxis
              tick={{ fontSize: 10, fill: "#94A3B8", fontWeight: "bold" }}
              axisLine={false}
              tickLine={false}
              dx={-5}
              tickFormatter={(v) => (v >= 1000 ? `${v / 1000}K` : v)}
              domain={[0, 4000]}
              ticks={[0, 1000, 2000, 3000, 4000]}
            />
            <Tooltip
              contentStyle={{
                borderRadius: 12,
                border: "1px solid #E2E8F0",
                boxShadow: "0 4px 12px rgba(0, 0, 0, 0.03)",
                fontSize: 12,
                fontWeight: "bold",
              }}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#0052FF"
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#complaintTrendGlow)"
              dot={{ r: 4, fill: "#0052FF", stroke: "#FFFFFF", strokeWidth: 1.5 }}
              activeDot={{ r: 6, fill: "#0052FF", stroke: "#FFFFFF", strokeWidth: 2 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
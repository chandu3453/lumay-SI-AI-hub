import { Users, ShieldCheck, Settings, AlertTriangle, ArrowUpRight } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

type MetricItem = {
  label: string;
  value: string;
  trend: string;
  trendColor: string;
  icon: React.ReactNode;
  iconBg: string;
  iconColor: string;
};

const METRICS: MetricItem[] = [
  {
    label: "Total Users",
    value: "128",
    trend: "+ 12% vs last 30 days",
    trendColor: "text-green-600",
    icon: <Users className="h-4 w-4" />,
    iconBg: "bg-blue-50 border border-blue-100",
    iconColor: "text-blue-600",
  },
  {
    label: "Active Roles",
    value: "18",
    trend: "No change",
    trendColor: "text-slate-400",
    icon: <ShieldCheck className="h-4 w-4" />,
    iconBg: "bg-green-50 border border-green-100",
    iconColor: "text-green-600",
  },
  {
    label: "System Configurations",
    value: "146",
    trend: "+ 8% vs last 30 days",
    trendColor: "text-green-600",
    icon: <Settings className="h-4 w-4" />,
    iconBg: "bg-purple-50 border border-purple-100",
    iconColor: "text-purple-600",
  },
  {
    label: "Pending Changes",
    value: "7",
    trend: "Requires review",
    trendColor: "text-amber-600",
    icon: <AlertTriangle className="h-4 w-4" />,
    iconBg: "bg-amber-50 border border-amber-100",
    iconColor: "text-amber-600",
  },
];

const SLA_DATA = [
  { name: "On Track", value: 12, percentage: "66.7%", color: "#10B981" },
  { name: "At Risk", value: 4, percentage: "22.2%", color: "#F59E0B" },
  { name: "Breached", value: 2, percentage: "11.1%", color: "#EF4444" },
];

export function SystemOverview() {
  return (
    <div className="space-y-6 text-left">
      {/* Title */}
      <div>
        <h3 className="text-sm font-bold text-[#0F172A] tracking-tight">System Overview</h3>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {METRICS.map((metric) => (
          <div key={metric.label} className="bg-white border border-[#E2E8F0] rounded-2xl p-4 shadow-sm flex flex-col justify-between h-[120px]">
            <div className="flex items-start justify-between">
              <div className={`h-8 w-8 rounded-xl flex items-center justify-center shrink-0 border ${metric.iconBg} ${metric.iconColor}`}>
                {metric.icon}
              </div>
            </div>
            
            <div className="mt-2.5">
              <span className="text-xl font-extrabold text-[#0F172A] block">{metric.value}</span>
              <span className="text-[10px] font-bold text-slate-400 block mt-0.5">{metric.label}</span>
            </div>

            <div className="mt-1.5 flex items-center gap-0.5 text-[9px] font-bold">
              {metric.trend.includes("+") && <ArrowUpRight className="h-3 w-3 text-green-600 shrink-0" />}
              <span className={metric.trendColor}>{metric.trend}</span>
            </div>
          </div>
        ))}
      </div>

      {/* SLA Policies Summary card */}
      <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-50 pb-3 mb-4">
          <h4 className="text-xs font-bold text-[#0F172A] tracking-tight">SLA Policies Summary</h4>
          <button className="text-[10px] font-bold text-[#0052FF] hover:underline">View All</button>
        </div>

        {/* Donut layout side-by-side */}
        <div className="flex items-center gap-4">
          {/* Donut chart */}
          <div className="relative h-28 w-28 shrink-0">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={SLA_DATA}
                  dataKey="value"
                  innerRadius={28}
                  outerRadius={44}
                  paddingAngle={2}
                >
                  {SLA_DATA.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-sm font-extrabold text-[#0F172A]">18</span>
              <span className="text-[8px] font-bold text-slate-400 uppercase tracking-wider">Total</span>
            </div>
          </div>

          {/* Legends list */}
          <div className="space-y-2 flex-1 min-w-0">
            {SLA_DATA.map((entry) => (
              <div key={entry.name} className="flex items-center gap-1.5 text-[10px] font-bold">
                <div className="h-2 w-2 rounded-full shrink-0" style={{ backgroundColor: entry.color }} />
                <span className="text-slate-500 w-14 truncate">{entry.name}</span>
                <span className="text-[#0F172A] ml-auto">{entry.value}</span>
                <span className="text-slate-400 font-semibold">({entry.percentage})</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
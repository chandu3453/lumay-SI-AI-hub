"use client";

import { useState } from "react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { ReportTemplates } from "@/features/reports/report-templates";
import { ReportsTable } from "@/features/reports/reports-table";
import { ScheduledReportsTable } from "@/features/reports/scheduled-reports-table";
import { Calendar, SlidersHorizontal, Plus, Download } from "lucide-react";
import { cn } from "@/lib/cn";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

// Data sets for bottom report charts
const VOLUME_DATA = [
  { name: "May 10", Total: 330, Resolved: 180, HighRisk: 65 },
  { name: "May 11", Total: 340, Resolved: 190, HighRisk: 68 },
  { name: "May 12", Total: 375, Resolved: 210, HighRisk: 72 },
  { name: "May 13", Total: 360, Resolved: 200, HighRisk: 78 },
  { name: "May 14", Total: 410, Resolved: 245, HighRisk: 82 },
  { name: "May 15", Total: 380, Resolved: 220, HighRisk: 80 },
  { name: "May 16", Total: 400, Resolved: 235, HighRisk: 78 },
];

const SEVERITY_DATA = [
  { name: "High", value: 312, percentage: "12.7%", color: "#EF4444" },
  { name: "Medium", value: 876, percentage: "35.7%", color: "#F59E0B" },
  { name: "Low", value: 1268, percentage: "51.6%", color: "#10B981" },
];

const TOP_THEMES = [
  { name: "Claim Delays", count: 567, percentage: 23 },
  { name: "Service Quality", count: 442, percentage: 18 },
  { name: "Payments & Refunds", count: 346, percentage: 14 },
  { name: "Communication", count: 270, percentage: 11 },
  { name: "Policy & Coverage", count: 221, percentage: 9 },
];

const tabList = [
  { id: "my-reports", label: "My Reports" },
  { id: "scheduled-reports", label: "Scheduled Reports" },
  { id: "shared-reports", label: "Shared Reports" },
];

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState("my-reports");

  return (
    <DashboardShell>
      <div className="space-y-8 animate-fade-in text-left">
        {/* Page Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-5">
          <div className="space-y-0.5">
            <h1 className="text-2xl font-extrabold tracking-tight text-[#0F172A]">Reports</h1>
            <p className="text-sm font-medium text-[#64748B]">Generate and schedule reports to monitor complaints, sentiment and performance.</p>
          </div>
          
          <div className="flex items-center gap-3">
            <button className="flex h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-all shadow-sm">
              <Calendar className="h-4 w-4 text-[#94A3B8]" />
              <span>May 10, 2025 - May 16, 2025</span>
            </button>
            <button className="flex h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-all shadow-sm">
              <SlidersHorizontal className="h-4 w-4 text-[#94A3B8]" />
              <span>Filters</span>
            </button>
            <button className="flex h-10 items-center gap-2 rounded-xl bg-[#0052FF] px-4.5 text-xs font-bold text-white shadow-md hover:bg-blue-700 transition-all active:scale-[0.98]">
              <Plus className="h-4 w-4" />
              <span>New Report</span>
            </button>
          </div>
        </div>

        {/* Report Templates Grid */}
        <ReportTemplates />

        {/* Navigation Tabs */}
        <div className="flex border-b border-[#E2E8F0] w-full text-left">
          {tabList.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "px-4 py-3 text-xs font-bold transition-all relative border-b-2 -mb-[1px]",
                  isActive
                    ? "border-[#0052FF] text-[#0052FF]"
                    : "border-transparent text-[#64748B] hover:text-[#0F172A]"
                )}
              >
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Reports Table List */}
        <ReportsTable activeTab={activeTab} />

        {/* Bottom charts row */}
        <div className="grid grid-cols-1 lg:grid-cols-[1.5fr_1fr_1.1fr] gap-6 items-start w-full">
          {/* Complaint Volume Trend */}
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm flex flex-col h-[280px]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-bold text-[#0F172A] tracking-tight">Complaint Volume Trend</h3>
              <div className="relative">
                <select className="h-7 rounded-lg border border-slate-200 bg-white px-2.5 pr-7 text-[10px] font-bold text-slate-700 focus:outline-none cursor-pointer appearance-none">
                  <option>Daily</option>
                  <option>Weekly</option>
                  <option>Monthly</option>
                </select>
                <div className="absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none border-l-3 border-r-3 border-t-3 border-l-transparent border-r-transparent border-t-[#64748B]" />
              </div>
            </div>

            <div className="flex-1 min-h-0 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={VOLUME_DATA} margin={{ top: 10, right: 10, bottom: -5, left: -25 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                  <XAxis
                    dataKey="name"
                    tick={{ fontSize: 9, fill: "#94A3B8", fontWeight: "bold" }}
                    axisLine={false}
                    tickLine={false}
                    dy={5}
                  />
                  <YAxis
                    tick={{ fontSize: 9, fill: "#94A3B8", fontWeight: "bold" }}
                    axisLine={false}
                    tickLine={false}
                    domain={[0, 500]}
                    ticks={[0, 100, 200, 300, 400, 500]}
                    dx={-5}
                  />
                  <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid #E2E8F0", fontSize: 10 }} />
                  <Line type="monotone" dataKey="Total" stroke="#0052FF" strokeWidth={2} dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="Resolved" stroke="#10B981" strokeWidth={2} dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="HighRisk" stroke="#EF4444" strokeWidth={2} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Complaints by Severity */}
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm flex flex-col h-[280px]">
            <h3 className="text-xs font-bold text-[#0F172A] tracking-tight mb-4">Complaints by Severity</h3>
            
            <div className="relative flex-1 min-h-0">
              <ResponsiveContainer width="100%" height="70%">
                <PieChart>
                  <Pie
                    data={SEVERITY_DATA}
                    dataKey="value"
                    innerRadius={45}
                    outerRadius={62}
                    paddingAngle={2}
                  >
                    {SEVERITY_DATA.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              
              <div className="absolute inset-0 flex flex-col items-center justify-center -translate-y-4">
                <span className="text-base font-extrabold text-[#0F172A]">2,456</span>
                <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">Total</span>
              </div>

              {/* Legends list */}
              <div className="flex justify-around text-[9px] font-bold text-[#475569] border-t border-slate-50 pt-3 mt-1.5">
                {SEVERITY_DATA.map((entry) => (
                  <div key={entry.name} className="flex items-center gap-1">
                    <div className="h-2 w-2 rounded-full shrink-0" style={{ backgroundColor: entry.color }} />
                    <span>{entry.name}</span>
                    <span className="text-slate-400">{entry.value} ({entry.percentage})</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Top 5 Complaint Themes */}
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm flex flex-col h-[280px] justify-between text-left">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-bold text-[#0F172A] tracking-tight">Top 5 Complaint Themes</h3>
              <div className="relative">
                <select className="h-6 rounded-lg border border-slate-200 bg-white px-2.5 pr-7 text-[9px] font-bold text-slate-700 focus:outline-none cursor-pointer appearance-none">
                  <option>This Week</option>
                </select>
                <div className="absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none border-l-3 border-r-3 border-t-3 border-l-transparent border-r-transparent border-t-[#64748B]" />
              </div>
            </div>

            <div className="flex-1 flex flex-col justify-around py-1">
              {TOP_THEMES.map((theme) => (
                <div key={theme.name} className="space-y-0.5">
                  <div className="flex items-center justify-between text-[10px] font-bold">
                    <span className="text-[#0F172A] truncate max-w-[120px]">{theme.name}</span>
                    <span className="text-slate-400">{theme.count} ({theme.percentage}%)</span>
                  </div>
                  <div className="h-1 rounded-full bg-slate-100 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-[#0052FF]"
                      style={{ width: `${theme.percentage * 4}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Scheduled Reports Row */}
        <ScheduledReportsTable />
      </div>
      <AICopilot />
    </DashboardShell>
  );
}
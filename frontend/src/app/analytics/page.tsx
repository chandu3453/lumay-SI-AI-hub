"use client";

import { useState } from "react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { KPICards } from "@/features/analytics/kpi-cards";
import { BranchPerformance } from "@/features/analytics/branch-performance";
import { RecurringIssues } from "@/features/analytics/recurring-issues";
import { Calendar, SlidersHorizontal, Download, ArrowUp, ArrowDown, Shield, Bell, AlertTriangle, Languages, Car, Landmark, Activity, Sparkles, AlertCircle } from "lucide-react";
import {
  AreaChart,
  Area,
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
import {
  useThemeDistribution,
  useSentimentTrend,
  useLanguageSplit,
  useSpikeDetection,
  useProviderBreakdown,
  useProductBreakdown,
} from "@/features/analytics/use-analytics";

const COLORS = ["#0052FF", "#10B981", "#3B82F6", "#8B5CF6", "#EC4899", "#F59E0B", "#EF4444", "#94A3B8"];

export default function AnalyticsPage() {
  const [days, setDays] = useState(30);
  
  // Phase 2 Hooks (FR-015 / FR-019)
  const { data: themeData, isLoading: themeLoading } = useThemeDistribution(days);
  const { data: sentimentTrend, isLoading: sentimentLoading } = useSentimentTrend(days);
  const { data: langSplit, isLoading: langLoading } = useLanguageSplit();
  const { data: spikeData, isLoading: spikeLoading } = useSpikeDetection(7, 30);
  const { data: providerData, isLoading: providerLoading } = useProviderBreakdown(days);
  const { data: productData, isLoading: productLoading } = useProductBreakdown(days);

  // Map theme data for Recharts Pie / List
  const themes = themeData?.breakdown ?? [
    { name: "Claim Delays", count: 567, percentage: 23 },
    { name: "Service Quality", count: 442, percentage: 18 },
    { name: "Payments & Refunds", count: 344, percentage: 14 },
    { name: "Communication", count: 270, percentage: 11 },
    { name: "Policy & Coverage", count: 221, percentage: 9 },
  ];

  // Map sentiment trend for AreaChart
  const sentimentChartData = sentimentTrend?.history ?? [
    { date: "May 10", positive: 45, neutral: 35, negative: 20 },
    { date: "May 11", positive: 48, neutral: 34, negative: 18 },
    { date: "May 12", positive: 47, neutral: 33, negative: 20 },
    { date: "May 13", positive: 50, neutral: 32, negative: 18 },
    { date: "May 14", positive: 52, neutral: 33, negative: 15 },
  ];

  // Map channel data
  const channels = themeData?.channels ?? [
    { name: "Voice Call", value: 42, count: 1031, color: "#0052FF" },
    { name: "WhatsApp", value: 24, count: 590, color: "#10B981" },
    { name: "Email", value: 15, count: 369, color: "#3B82F6" },
    { name: "Web Chat", value: 11, count: 270, color: "#8B5CF6" },
    { name: "SMART CALL", value: 5, count: 121, color: "#EC4899" },
  ];

  // Map language distribution
  const languages = langSplit?.distribution 
    ? Object.entries(langSplit.distribution).map(([key, info]: any) => ({
        name: key === "ar" ? "Arabic" : key === "en" ? "English" : key === "mixed" ? "Mixed" : "Other",
        value: info.pct,
        count: info.count,
      }))
    : [
        { name: "English", value: 72 },
        { name: "Arabic", value: 18 },
        { name: "Mixed", value: 10 },
      ];

  return (
    <DashboardShell>
      <div className="space-y-8 animate-fade-in text-left">
        {/* Page Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-5">
          <div className="space-y-0.5">
            <h1 className="text-2xl font-extrabold tracking-tight text-[#0F172A]">LuMay Intelligence & Analytics</h1>
            <p className="text-sm font-medium text-[#64748B]">Insights, automated spike detection, and Arabic-English sentiment analytics.</p>
          </div>
          
          <div className="flex items-center gap-3">
            <select 
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="h-10 rounded-xl border border-slate-200 bg-white px-4 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-all shadow-sm focus:outline-none cursor-pointer"
            >
              <option value={7}>Last 7 Days</option>
              <option value={30}>Last 30 Days</option>
              <option value={90}>Last 90 Days</option>
            </select>
            <button className="flex h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-all shadow-sm">
              <Download className="h-4 w-4 text-[#94A3B8]" />
              <span>Export Report</span>
            </button>
          </div>
        </div>

        {/* KPI Cards Row */}
        <KPICards />

        {/* FR-015: Spike Detection Widget & Highlights */}
        {spikeData && (
          <div className={`p-5 rounded-2xl border transition-all ${
            spikeData.is_spike 
              ? "bg-[#FEF2F2] border-[#FCA5A5] text-[#991B1B]" 
              : "bg-[#F8FAFC] border-[#E2E8F0] text-[#1E293B]"
          }`}>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className={`p-2.5 rounded-xl ${spikeData.is_spike ? "bg-[#FEE2E2]" : "bg-white border border-[#E2E8F0]"}`}>
                  <AlertTriangle className={`h-6 w-6 ${spikeData.is_spike ? "text-[#EF4444]" : "text-[#0052FF]"}`} />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-[#0F172A] flex items-center gap-2">
                    Automated Spike & Theme Detection
                    {spikeData.is_spike && (
                      <span className="text-[10px] uppercase font-extrabold tracking-wide px-2 py-0.5 rounded-md bg-[#EF4444] text-white animate-pulse">
                        Volume Spike Active
                      </span>
                    )}
                  </h3>
                  <p className="text-xs text-[#64748B] mt-0.5">
                    Currently tracking <strong>{spikeData.current_count} complaints</strong> in the last {spikeData.window_days} days vs baseline average of <strong>{spikeData.baseline_avg}</strong> (Ratio: <strong>{spikeData.spike_ratio}x</strong>).
                  </p>
                </div>
              </div>

              {spikeData.emerging_themes && spikeData.emerging_themes.length > 0 && (
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Spiking Themes:</span>
                  {spikeData.emerging_themes.map((theme: any) => (
                    <span 
                      key={theme.theme} 
                      className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-[#0F172A] shadow-sm flex items-center gap-1.5"
                    >
                      <Sparkles className="h-3 w-3 text-[#F59E0B]" />
                      {theme.label} ({theme.current_count} cases, +{Math.round((theme.spike_ratio - 1) * 100)}%)
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Charts Row 1: Sentiment, Channel, Theme */}
        <div className="grid grid-cols-1 lg:grid-cols-[1.2fr_0.9fr_0.9fr] gap-6 items-start">
          
          {/* Sentiment Trend Area Chart */}
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm flex flex-col h-[340px]">
            <h3 className="text-xs font-bold text-[#0F172A] tracking-tight mb-4 flex items-center gap-1.5">
              Sentiment Trend
            </h3>
            <div className="flex-1 min-h-0 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={sentimentChartData} margin={{ top: 10, right: 10, bottom: -5, left: -25 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                  <XAxis dataKey="date" tick={{ fontSize: 9, fill: "#94A3B8", fontWeight: "bold" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 9, fill: "#94A3B8", fontWeight: "bold" }} axisLine={false} tickLine={false} domain={[0, 100]} />
                  <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid #E2E8F0", fontSize: 10 }} />
                  <Area type="monotone" dataKey="positive" stackId="1" stroke="#10B981" fill="#D1FAE5" opacity={0.6} />
                  <Area type="monotone" dataKey="neutral" stackId="1" stroke="#F59E0B" fill="#FEF3C7" opacity={0.6} />
                  <Area type="monotone" dataKey="negative" stackId="1" stroke="#EF4444" fill="#FEE2E2" opacity={0.6} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Languages distribution (FR-019) */}
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm flex flex-col h-[340px]">
            <h3 className="text-xs font-bold text-[#0F172A] tracking-tight mb-4 flex items-center gap-1.5">
              <Languages className="h-4 w-4 text-[#0052FF]" /> Multilingual Distribution
            </h3>
            
            <div className="relative flex-1 min-h-0">
              <ResponsiveContainer width="100%" height="60%">
                <PieChart>
                  <Pie
                    data={languages}
                    dataKey="value"
                    innerRadius={48}
                    outerRadius={65}
                    paddingAngle={2}
                  >
                    {languages.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              
              <div className="absolute inset-0 flex flex-col items-center justify-center -translate-y-4">
                <span className="text-base font-extrabold text-[#0F172A]">
                  {langSplit?.arabic_complaint_percentage ?? 28}%
                </span>
                <span className="text-[8px] font-bold text-slate-400 uppercase tracking-wider">Arabic / Mixed</span>
              </div>

              {/* Legends list */}
              <div className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-[10px] font-bold text-[#475569] border-t border-slate-50 pt-3 mt-1">
                {languages.map((entry, index) => (
                  <div key={entry.name} className="flex items-center gap-1.5 truncate">
                    <div className="h-2 w-2 rounded-full shrink-0" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                    <span className="truncate">{entry.name}</span>
                    <span className="text-slate-400 ml-auto">{entry.value}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Theme list */}
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm flex flex-col h-[340px] justify-between">
            <h3 className="text-xs font-bold text-[#0F172A] tracking-tight mb-4">Top Complaint Themes</h3>
            <div className="flex-1 flex flex-col justify-between py-1 overflow-y-auto space-y-3">
              {themes.slice(0, 5).map((theme: any) => (
                <div key={theme.name} className="space-y-1">
                  <div className="flex items-center justify-between text-[10px] font-bold">
                    <span className="text-[#0F172A] truncate max-w-[120px]">{theme.name.replace(/_/g, " ")}</span>
                    <span className="text-slate-400">{theme.percentage}% ({theme.count})</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-slate-100 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-[#0052FF]"
                      style={{ width: `${theme.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* FR-015: Product Breakdown & Provider breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          
          {/* Insurance Product Breakdown */}
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm text-left space-y-4">
            <div>
              <h3 className="text-xs font-bold text-[#0F172A] tracking-tight flex items-center gap-2">
                <Car className="h-4 w-4 text-[#0052FF]" /> Product-level Analysis
              </h3>
              <p className="text-[11px] text-muted-foreground mt-0.5">Complaints volume split by insurance product type.</p>
            </div>

            <div className="space-y-3">
              {productData?.breakdown ? (
                productData.breakdown.map((prod: any, index: number) => (
                  <div key={prod.product} className="flex items-center justify-between p-2.5 rounded-xl border border-slate-50 hover:bg-slate-50 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="h-2 w-2 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                      <span className="text-xs font-semibold text-[#0F172A] capitalize">{prod.label}</span>
                    </div>
                    <div className="flex items-center gap-4 text-xs font-bold">
                      <span className="text-[#0F172A]">{prod.count} cases</span>
                      <span className="text-slate-400 w-10 text-right">{prod.pct}%</span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-muted-foreground">No product breakdown available.</p>
              )}
            </div>
          </div>

          {/* Provider / Garage Breakdown */}
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm text-left space-y-4">
            <div>
              <h3 className="text-xs font-bold text-[#0F172A] tracking-tight flex items-center gap-2">
                <Landmark className="h-4 w-4 text-[#0052FF]" /> Provider & Network Feedback
              </h3>
              <p className="text-[11px] text-muted-foreground mt-0.5">Complaints listing specific repair garages, medical centers, or claim providers.</p>
            </div>

            <div className="space-y-3">
              {providerData?.breakdown && providerData.breakdown.length > 0 ? (
                providerData.breakdown.map((prov: any) => (
                  <div key={prov.provider} className="flex items-center justify-between p-2.5 rounded-xl border border-slate-50 hover:bg-slate-50 transition-colors">
                    <span className="text-xs font-semibold text-[#0F172A] truncate max-w-[200px]">{prov.provider}</span>
                    <div className="flex items-center gap-4 text-xs font-bold">
                      <span className="text-[#EF4444]">{prov.count} complaints</span>
                      <span className="text-slate-400 w-10 text-right">{prov.pct}%</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="py-6 text-center text-xs text-muted-foreground">
                  No provider-specific complaints detected in this timeframe.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Branches Table & Recurring Issues */}
        <div className="grid grid-cols-1 lg:grid-cols-[1.55fr_1fr] gap-8 items-start w-full">
          <BranchPerformance />
          <RecurringIssues />
        </div>
      </div>
      <AICopilot />
    </DashboardShell>
  );
}
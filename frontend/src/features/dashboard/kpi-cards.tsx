"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { useDashboardKPIs } from "@/features/dashboard/use-dashboard";
import { Users, MessageSquare, AlertTriangle, GitBranch, Bell, Clock, Activity, Shield } from "lucide-react";

const items = [
  { label: "Total Customers", key: "total_customers", icon: <Users className="h-4 w-4 text-blue-500" /> },
  { label: "Interactions", key: "total_interactions", icon: <MessageSquare className="h-4 w-4 text-emerald-500" /> },
  { label: "Complaints", key: "total_complaints", icon: <AlertTriangle className="h-4 w-4 text-orange-500" />, badgeKey: "open_complaints", badgeLabel: "open" },
  { label: "Workflows", key: "total_workflows", icon: <GitBranch className="h-4 w-4 text-purple-500" />, badgeKey: "active_workflows", badgeLabel: "active" },
  { label: "Notifications", key: "total_notifications", icon: <Bell className="h-4 w-4 text-pink-500" /> },
  { label: "Avg Resolution", key: "avg_resolution_time_hours", icon: <Clock className="h-4 w-4 text-cyan-500" />, fmt: (v: number) => `${v}h` },
  { label: "SLA Compliance", key: "sla_compliance_rate", icon: <Shield className="h-4 w-4 text-emerald-500" />, fmt: (v: number) => `${v}%` },
  { label: "Avg Sentiment", key: "avg_sentiment_score", icon: <Activity className="h-4 w-4 text-rose-500" />, fmt: (v: number) => v.toFixed(2) },
];

export function KpiCards() {
  const { data: kpis, isLoading } = useDashboardKPIs();

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {items.map((item) => (
          <Card key={item.key}>
            <CardHeader className="pb-2"><Skeleton className="h-4 w-28" /></CardHeader>
            <CardContent><Skeleton className="h-8 w-16" /></CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!kpis) return null;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {items.map((item) => {
        const value = item.fmt ? item.fmt((kpis as any)[item.key]) : (kpis as any)[item.key];
        const badge = item.badgeKey ? `${(kpis as any)[item.badgeKey]}` : null;
        return (
          <Card key={item.key} className="hover:shadow-md transition-shadow duration-200">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{item.label}</CardTitle>
              {item.icon}
            </CardHeader>
            <CardContent>
              <div className="stat-value">{value}</div>
              {badge && <Badge variant="neutral" className="mt-1.5">{badge} {item.badgeLabel}</Badge>}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
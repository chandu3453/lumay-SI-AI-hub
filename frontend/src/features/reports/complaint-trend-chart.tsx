"use client";

import { useState } from "react";
import { useReportTrends } from "./use-reports";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/cn";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts";

const granularities = ["Daily", "Weekly", "Monthly"] as const;

export function ComplaintTrendChart() {
  const [granularity, setGranularity] = useState<string>("Daily");
  const { data: trends, isLoading } = useReportTrends();

  const data = trends?.slice(-30) ?? [];

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-semibold text-[#0F172A]">Complaint Volume Trend</CardTitle>
          <div className="flex items-center gap-1 bg-muted rounded-lg p-0.5">
            {granularities.map((g) => (
              <button
                key={g}
                onClick={() => setGranularity(g)}
                className={cn(
                  "px-3 py-1 text-xs font-medium rounded-md transition-colors",
                  granularity === g
                    ? "bg-white text-[#0F172A] shadow-sm"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                {g}
              </button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="h-72">
        {isLoading ? (
          <Skeleton className="h-full w-full" />
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{
                  borderRadius: 8,
                  border: "1px solid #E2E8F0",
                  boxShadow: "0 1px 3px 0 rgb(0 0 0 / 0.04)",
                  fontSize: 12,
                }}
              />
              <Legend
                wrapperStyle={{ fontSize: 11, paddingTop: 8 }}
                iconType="circle"
                iconSize={6}
              />
              <Line type="monotone" dataKey="total" stroke="#2563EB" strokeWidth={2} dot={false} name="Total" />
              <Line type="monotone" dataKey="resolved" stroke="#16A34A" strokeWidth={2} dot={false} name="Resolved" />
              <Line type="monotone" dataKey="high_risk" stroke="#DC2626" strokeWidth={2} dot={false} name="High Risk" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
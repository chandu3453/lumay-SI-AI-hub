"use client";

import { useAnalyticsKPIs } from "./use-analytics";
import { Card, CardContent } from "@/components/ui/card";

export function AnalyticsHeader() {
  const { data: kpis, isLoading } = useAnalyticsKPIs();

  const highRiskCases = kpis?.high_risk ?? 0;
  const totalComplaints = kpis?.total_complaints ?? 0;
  const escalationRate = kpis?.escalation_rate ?? 0;

  return (
    <div className="grid grid-cols-3 gap-4">
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-[#64748B]">High-Risk Cases</p>
          <p className="mt-1 text-3xl font-bold text-[#DC2626]">
            {isLoading ? "..." : highRiskCases}
          </p>
          <p className="mt-1 text-xs text-[#64748B]">
            {totalComplaints > 0
              ? `${Math.round((highRiskCases / totalComplaints) * 100)}% of total cases`
              : "No data"}
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-[#64748B]">Escalation Rate</p>
          <p className="mt-1 text-3xl font-bold text-[#F59E0B]">
            {isLoading ? "..." : `${escalationRate}%`}
          </p>
          <p className="mt-1 text-xs text-[#64748B]">
            {isLoading ? "" : `${kpis?.escalated_cases ?? 0} escalated cases`}
          </p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-[#64748B]">Repeat Complaint Rate</p>
          <p className="mt-1 text-3xl font-bold text-[#8B5CF6]">
            {isLoading ? "..." : `${kpis?.repeat_complaint_rate ?? 0}%`}
          </p>
          <p className="mt-1 text-xs text-[#64748B]">Indicating pattern recurrence</p>
        </CardContent>
      </Card>
    </div>
  );
}
"use client";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { WorkflowList } from "@/features/workflow/workflow-list";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { InsuranceFilter } from "@/components/insurance/InsuranceFilter";

export default function WorkflowPage() {
  return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-start justify-between gap-4">
          <div className="page-header mb-0">
            <h1>Workflows</h1>
            <p>Complaint resolution and escalation workflows</p>
          </div>
          <InsuranceFilter />
        </div>
        <WorkflowList />
      </div>
      <AICopilot />
    </DashboardShell>
  );
}
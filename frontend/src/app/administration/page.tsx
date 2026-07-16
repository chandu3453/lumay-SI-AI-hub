"use client";

import { useState } from "react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import {
  AdministrationHeader,
  AdministrationTabs,
  ConfigurationGrid,
  SystemOverview,
  IntegrationList,
  ActivityTable,
} from "@/features/administration";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FolderKanban, Clock, GitBranch, Users, Radio, Settings, FileText } from "lucide-react";

const TAB_CONTENT: Record<string, { icon: React.ReactNode; sections: { title: string; items: string[] }[] }> = {
  categories: {
    icon: <FolderKanban className="h-4 w-4" />,
    sections: [
      { title: "Complaint Categories", items: ["Claim Processing", "Policy Service", "Billing", "Underwriting", "Customer Service"] },
      { title: "Subcategories", items: ["Delay", "Denial", "Error", "Misrepresentation", "Non-disclosure"] },
      { title: "Severity Classification", items: ["Critical", "High", "Medium", "Low", "Info"] },
    ],
  },
  sla: {
    icon: <Clock className="h-4 w-4" />,
    sections: [
      { title: "Response Time SLAs", items: ["Critical: 15 min", "High: 1 hour", "Medium: 4 hours", "Low: 24 hours"] },
      { title: "Resolution Time SLAs", items: ["Critical: 4 hours", "High: 24 hours", "Medium: 3 days", "Low: 7 days"] },
      { title: "Escalation Thresholds", items: ["SLA at 75%: Warning", "SLA at 90%: Supervisor Alert", "SLA Breached: Auto-escalate"] },
    ],
  },
  routing: {
    icon: <GitBranch className="h-4 w-4" />,
    sections: [
      { title: "Assignment Rules", items: ["Round Robin", "Skill-based", "Priority-based", "Manual Assignment"] },
      { title: "Escalation Paths", items: ["Team Lead → Manager → Director", "Supervisor Review → Compliance", "Auto-escalation Rules"] },
    ],
  },
  users: {
    icon: <Users className="h-4 w-4" />,
    sections: [
      { title: "Roles", items: ["Agent", "Senior Agent", "Team Lead", "Supervisor", "Manager", "Administrator", "Compliance Officer"] },
      { title: "Permissions", items: ["View Cases", "Assign Cases", "Escalate", "Resolve", "Close", "Administrative"] },
      { title: "Teams", items: ["Claims Processing", "Policy Services", "Customer Support", "Compliance", "Quality Assurance"] },
    ],
  },
  channels: {
    icon: <Radio className="h-4 w-4" />,
    sections: [
      { title: "Active Channels", items: ["Voice", "Email", "WhatsApp", "Web Chat", "Smart Call", "CRM", "Manual Entry"] },
      { title: "Channel Routing", items: ["Voice → Claims Team", "Email → General Queue", "WhatsApp → Customer Support", "Web Chat → AI Triage"] },
    ],
  },
  "audit-logs": {
    icon: <FileText className="h-4 w-4" />,
    sections: [
      { title: "Audit Categories", items: ["User Actions", "System Changes", "Data Access", "Security Events", "Compliance Reviews"] },
      { title: "Retention Policy", items: ["Audit Logs: 7 years", "Access Logs: 1 year", "System Events: 90 days"] },
    ],
  },
  settings: {
    icon: <Settings className="h-4 w-4" />,
    sections: [
      { title: "System Configuration", items: ["Platform Name", "Support Email", "Business Hours", "Holiday Calendar"] },
      { title: "Integration Settings", items: ["API Endpoints", "Webhook URLs", "SSO Configuration", "Data Sync Schedule"] },
    ],
  },
};

export default function AdministrationPage() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in text-left">
        {/* Header */}
        <AdministrationHeader />

        {/* Tabs */}
        <AdministrationTabs active={activeTab} onChange={setActiveTab} />

        {activeTab === "overview" ? (
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_310px] gap-6 items-start">
            {/* Left Column */}
            <div className="space-y-6 min-w-0">
              {/* Configuration Center card */}
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-bold text-[#0F172A] tracking-tight">Configuration Center</h3>
                  <p className="text-[11px] font-semibold text-slate-400 mt-0.5">Manage all system configurations from one place.</p>
                </div>
                <ConfigurationGrid />
              </div>
              
              {/* Activity Table */}
              <ActivityTable />
            </div>

            {/* Right Column */}
            <div className="space-y-6 shrink-0 hidden lg:block">
              <SystemOverview />
              <IntegrationList />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-6">
            <div className="space-y-4">
              {TAB_CONTENT[activeTab]?.sections.map((section) => (
                <Card key={section.title}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-semibold text-[#0F172A]">{section.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-1.5">
                      {section.items.map((item) => (
                        <div key={item} className="flex items-center justify-between py-1.5 px-2 rounded-md hover:bg-accent transition-colors">
                          <span className="text-sm text-[#0F172A]">{item}</span>
                          <Badge variant="outline" className="text-[10px]">Configure</Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            <div className="space-y-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-semibold text-[#0F172A]">
                    {activeTab === "categories" ? "Categories & Taxonomy" :
                     activeTab === "sla" ? "SLA & Deadlines" :
                     activeTab === "routing" ? "Routing & Escalation" :
                     activeTab === "users" ? "Users & Roles" :
                     activeTab === "channels" ? "Channels & Sources" :
                     activeTab === "settings" ? "System Settings" :
                     "Audit Logs"} Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Configure and manage {activeTab === "categories" ? "complaint categories and taxonomy" :
                     activeTab === "sla" ? "SLA thresholds and deadlines" :
                     activeTab === "routing" ? "routing and escalation rules" :
                     activeTab === "users" ? "user roles and permissions" :
                     activeTab === "channels" ? "communication channels and sources" :
                     activeTab === "settings" ? "system-level settings" :
                     "audit log configuration"} for your organization.
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>
      <AICopilot />
    </DashboardShell>
  );
}


"use client";

import { useState } from "react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bell, Shield, User, Globe, Lock, Database, ChevronRight } from "lucide-react";

const SETTINGS_SECTIONS = [
  {
    title: "Profile",
    icon: User,
    description: "Manage your account details and preferences",
    items: ["Full Name", "Email Address", "Phone Number", "Language", "Timezone"],
  },
  {
    title: "Notifications",
    icon: Bell,
    description: "Configure alert and notification preferences",
    items: ["Email Notifications", "Push Notifications", "SMS Alerts", "Digest Frequency"],
  },
  {
    title: "Security",
    icon: Lock,
    description: "Manage security settings and access controls",
    items: ["Password", "Two-Factor Auth", "Session Management", "API Keys"],
  },
  {
    title: "Regional",
    icon: Globe,
    description: "Configure regional and localization settings",
    items: ["Country", "Currency", "Date Format", "Number Format"],
  },
  {
    title: "Compliance",
    icon: Shield,
    description: "Regulatory and compliance configuration",
    items: ["Data Retention", "Audit Logging", "Consent Management", "Reporting Standards"],
  },
  {
    title: "Data & Storage",
    icon: Database,
    description: "Manage data storage and export settings",
    items: ["Data Export", "Archive Policy", "Backup Schedule", "Storage Quota"],
  },
];

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState("Profile");

  return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in">
        <div className="page-header">
          <h1>Settings</h1>
          <p>System configuration and platform preferences</p>
        </div>

        <div className="grid grid-cols-[240px_1fr] gap-6">
          <div className="space-y-1">
            {SETTINGS_SECTIONS.map((section) => {
              const Icon = section.icon;
              return (
                <button
                  key={section.title}
                  onClick={() => setActiveSection(section.title)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors text-left ${
                    activeSection === section.title
                      ? "bg-primary/10 text-primary font-medium"
                      : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  }`}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  <span>{section.title}</span>
                </button>
              );
            })}
          </div>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-semibold text-[#0F172A]">{activeSection}</CardTitle>
              <p className="text-xs text-muted-foreground">
                {SETTINGS_SECTIONS.find((s) => s.title === activeSection)?.description}
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {SETTINGS_SECTIONS.find((s) => s.title === activeSection)?.items.map((item) => (
                  <div key={item} className="flex items-center justify-between py-2.5 px-3 rounded-lg border border-border hover:bg-accent transition-colors cursor-pointer">
                    <span className="text-sm text-[#0F172A]">{item}</span>
                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
      <AICopilot />
    </DashboardShell>
  );
}

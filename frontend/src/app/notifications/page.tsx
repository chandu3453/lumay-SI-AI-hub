"use client";

import { useState } from "react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import {
  NotificationsHeader,
  NotificationsTabs,
  NotificationFeed,
  NotificationFilters,
} from "@/features/notifications";

export default function NotificationsPage() {
  const [activeTab, setActiveTab] = useState("all");

  const mockFilters = {
    types: [],
    priorities: [],
    channels: [],
    dateRange: "7d",
  };

  const handleFilterChange = () => {};

  return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in text-left">
        {/* Header */}
        <NotificationsHeader />

        {/* Full-width Tabs */}
        <NotificationsTabs active={activeTab} onChange={setActiveTab} />

        {/* Split Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_290px] gap-6 items-start">
          <div className="min-w-0">
            <NotificationFeed />
          </div>
          <div className="hidden lg:block shrink-0">
            <NotificationFilters filters={mockFilters} onChange={handleFilterChange} />
          </div>
        </div>
      </div>
      <AICopilot />
    </DashboardShell>
  );
}
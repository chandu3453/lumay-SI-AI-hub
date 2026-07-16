"use client";

import { cn } from "@/lib/cn";
import { Badge } from "@/components/ui/badge";

export type ComplaintTabId = "all" | "open" | "assigned_to_me" | "high_risk" | "critical" | "overdue" | "resolved" | "closed" | "repeat";

type ComplaintTab = {
  id: ComplaintTabId;
  label: string;
};

const TABS: ComplaintTab[] = [
  { id: "all", label: "All Complaints" },
  { id: "open", label: "Open" },
  { id: "assigned_to_me", label: "Assigned To Me" },
  { id: "high_risk", label: "High Risk" },
  { id: "critical", label: "Critical" },
  { id: "overdue", label: "Overdue" },
  { id: "resolved", label: "Resolved" },
  { id: "closed", label: "Closed" },
  { id: "repeat", label: "Repeat Complaints" },
];

type ComplaintTabsProps = {
  activeTab: ComplaintTabId;
  onTabChange: (tab: ComplaintTabId) => void;
  counts: Record<string, number>;
};

export function ComplaintTabs({ activeTab, onTabChange, counts }: ComplaintTabsProps) {
  return (
    <div className="flex gap-1 border-b border-border overflow-x-auto">
      {TABS.map((tab) => {
        const count = counts[tab.id] ?? 0;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "flex items-center gap-2 px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-colors",
              activeTab === tab.id
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground",
            )}
          >
            {tab.label}
            <Badge variant={activeTab === tab.id ? "default" : "neutral"} className="text-[10px] px-1.5 py-0 h-4">
              {count}
            </Badge>
          </button>
        );
      })}
    </div>
  );
}
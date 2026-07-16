"use client";

import { cn } from "@/lib/cn";

const tabs = [
  { key: "my-reports", label: "My Reports", count: 12 },
  { key: "scheduled", label: "Scheduled", count: 5 },
  { key: "shared", label: "Shared", count: 3 },
];

type ReportsTabsProps = {
  active: string;
  onChange: (key: string) => void;
};

export function ReportsTabs({ active, onChange }: ReportsTabsProps) {
  return (
    <div className="flex items-center gap-1 border-b border-border">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={cn(
            "flex items-center gap-2 px-4 py-2.5 text-sm font-medium transition-colors border-b-2 -mb-[1px]",
            active === tab.key
              ? "text-primary border-primary"
              : "text-muted-foreground border-transparent hover:text-foreground",
          )}
        >
          {tab.label}
          <span
            className={cn(
              "inline-flex items-center justify-center min-w-5 h-5 px-1.5 rounded-full text-[11px] font-medium",
              active === tab.key
                ? "bg-primary/10 text-primary"
                : "bg-muted text-muted-foreground",
            )}
          >
            {tab.count}
          </span>
        </button>
      ))}
    </div>
  );
}
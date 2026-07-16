"use client";

import { CalendarRange, Download, Plus } from "lucide-react";

export function ReportsToolbar() {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button className="flex items-center gap-2 px-4 py-2 text-sm border border-border rounded-lg bg-white hover:bg-accent transition-colors">
          <CalendarRange className="h-4 w-4 text-muted-foreground" />
          <span>Date Range</span>
        </button>
        <button className="flex items-center gap-2 px-4 py-2 text-sm border border-border rounded-lg bg-white hover:bg-accent transition-colors">
          <span>Filters</span>
        </button>
      </div>
      <div className="flex items-center gap-3">
        <button className="flex items-center gap-2 px-4 py-2 text-sm border border-border rounded-lg bg-white hover:bg-accent transition-colors">
          <Download className="h-4 w-4 text-muted-foreground" />
          <span>Export All</span>
        </button>
        <button className="flex items-center gap-2 px-4 py-2 text-sm bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 shadow-sm transition-colors">
          <Plus className="h-4 w-4" />
          <span>New Report</span>
        </button>
      </div>
    </div>
  );
}
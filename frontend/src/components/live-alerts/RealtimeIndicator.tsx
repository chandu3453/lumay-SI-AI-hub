"use client";

import { RefreshCw } from "lucide-react";

export function RealtimeIndicator() {
  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground">
      <span className="relative flex h-2 w-2">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75" />
        <span className="relative inline-flex rounded-full h-2 w-2 bg-success" />
      </span>
      Auto-updating in real time
      <RefreshCw className="h-3 w-3 text-muted-foreground/50" />
    </div>
  );
}
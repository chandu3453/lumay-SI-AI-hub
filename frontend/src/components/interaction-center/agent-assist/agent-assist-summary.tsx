"use client";

import type { AgentAssistInsight } from "@/features/agent-assist/types";

export function AgentAssistSummary({ insight }: { insight: AgentAssistInsight }) {
  return (
    <div className="space-y-1">
      <h3 className="text-xs font-semibold text-muted-foreground">Live Summary</h3>
      <p className="text-sm">{insight.summary || "No summary available yet."}</p>
    </div>
  );
}

"use client";

import { Badge } from "@/components/ui/badge";
import type { AgentAssistInsight } from "@/features/agent-assist/types";

export function AgentAssistIntent({ insight }: { insight: AgentAssistInsight }) {
  if (!insight.intent) return null;
  const confidencePct =
    insight.intent_confidence != null ? Math.round(insight.intent_confidence * 100) : null;

  return (
    <div className="space-y-1">
      <h3 className="text-xs font-semibold text-muted-foreground">Detected Intent</h3>
      <div className="flex items-center gap-1.5">
        <Badge variant="default">{insight.intent}</Badge>
        {confidencePct != null ? (
          <span className="text-[11px] text-muted-foreground">{confidencePct}% confidence</span>
        ) : null}
      </div>
    </div>
  );
}

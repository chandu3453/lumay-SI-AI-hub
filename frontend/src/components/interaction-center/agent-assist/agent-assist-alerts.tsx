"use client";

import { AlertTriangle } from "lucide-react";

import { cn } from "@/lib/cn";
import type { AgentAssistAlert } from "@/features/agent-assist/types";

const SEVERITY_CLASSES: Record<string, string> = {
  info: "border-border bg-muted/30 text-foreground",
  warning: "border-warning/30 bg-warning/10 text-warning",
  critical: "border-destructive/30 bg-destructive/10 text-destructive",
};

export function AgentAssistAlerts({ alerts }: { alerts: AgentAssistAlert[] }) {
  if (alerts.length === 0) return null;
  return (
    <div className="space-y-1.5">
      <h3 className="text-xs font-semibold text-muted-foreground">Alerts</h3>
      {alerts.map((alert, index) => (
        <div
          key={index}
          className={cn(
            "flex items-start gap-1.5 rounded-md border p-2 text-xs",
            SEVERITY_CLASSES[alert.severity] ?? SEVERITY_CLASSES.info,
          )}
        >
          <AlertTriangle className="mt-0.5 h-3 w-3 shrink-0" />
          <span>{alert.message}</span>
        </div>
      ))}
    </div>
  );
}

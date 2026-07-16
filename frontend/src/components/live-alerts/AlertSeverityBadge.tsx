"use client";

import { Badge } from "@/components/ui/badge";

const severityVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  high: "destructive",
  medium: "warning",
  low: "neutral",
  critical: "destructive",
};

type AlertSeverityBadgeProps = {
  severity: string | null | undefined;
};

export function AlertSeverityBadge({ severity }: AlertSeverityBadgeProps) {
  if (!severity) return <span className="text-sm text-muted-foreground">—</span>;
  const variant = severityVariant[severity] ?? "neutral";
  return (
    <Badge variant={variant} className="capitalize">
      {severity}
    </Badge>
  );
}
"use client";

import { Badge } from "@/components/ui/badge";

const severityVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  low: "neutral",
  medium: "default",
  high: "warning",
  critical: "destructive",
};

type SeverityBadgeProps = {
  severity: string;
};

export function SeverityBadge({ severity }: SeverityBadgeProps) {
  const variant = severityVariant[severity] ?? "neutral";
  return (
    <Badge variant={variant} className="capitalize">
      {severity}
    </Badge>
  );
}
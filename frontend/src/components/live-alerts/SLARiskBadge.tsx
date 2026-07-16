"use client";

import { Badge } from "@/components/ui/badge";

const slaVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  on_track: "success",
  at_risk: "warning",
  overdue: "destructive",
  breached: "destructive",
};

const slaLabel: Record<string, string> = {
  on_track: "On Track",
  at_risk: "At Risk",
  overdue: "Overdue",
  breached: "Breached",
};

type SLARiskBadgeProps = {
  risk: string | null | undefined;
};

export function SLARiskBadge({ risk }: SLARiskBadgeProps) {
  if (!risk) return <span className="text-sm text-muted-foreground">—</span>;
  const variant = slaVariant[risk] ?? "neutral";
  const label = slaLabel[risk] ?? risk;
  return (
    <Badge variant={variant} className="capitalize">
      {label}
    </Badge>
  );
}
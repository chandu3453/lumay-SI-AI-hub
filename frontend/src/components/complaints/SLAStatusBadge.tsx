"use client";

import { Badge } from "@/components/ui/badge";

const slaVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  on_track: "success",
  at_risk: "warning",
  overdue: "destructive",
  breached: "destructive",
  completed: "success",
};

const slaLabel: Record<string, string> = {
  on_track: "On Track",
  at_risk: "At Risk",
  overdue: "Overdue",
  breached: "Breached",
  completed: "Completed",
};

type SLAStatusBadgeProps = {
  status: string | null | undefined;
};

export function SLAStatusBadge({ status }: SLAStatusBadgeProps) {
  if (!status) return <span className="text-sm text-muted-foreground">—</span>;
  const variant = slaVariant[status] ?? "neutral";
  const label = slaLabel[status] ?? status;
  return (
    <Badge variant={variant} className="capitalize">
      {label}
    </Badge>
  );
}
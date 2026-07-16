"use client";

import { Badge } from "@/components/ui/badge";

const statusVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  new: "destructive",
  acknowledged: "warning",
  investigating: "default",
  resolved: "success",
  closed: "neutral",
};

const statusLabel: Record<string, string> = {
  new: "New",
  acknowledged: "Acknowledged",
  investigating: "Investigating",
  resolved: "Resolved",
  closed: "Closed",
};

type AlertStatusBadgeProps = {
  status: string | null | undefined;
};

export function AlertStatusBadge({ status }: AlertStatusBadgeProps) {
  if (!status) return <span className="text-sm text-muted-foreground">—</span>;
  const variant = statusVariant[status] ?? "neutral";
  const label = statusLabel[status] ?? status;
  return (
    <Badge variant={variant} className="capitalize">
      {label}
    </Badge>
  );
}
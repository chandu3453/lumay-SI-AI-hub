"use client";

import { Badge } from "@/components/ui/badge";

const priorityVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  low: "neutral",
  medium: "default",
  high: "warning",
  critical: "destructive",
};

type PriorityBadgeProps = {
  priority: string;
};

export function PriorityBadge({ priority }: PriorityBadgeProps) {
  const variant = priorityVariant[priority] ?? "neutral";
  return (
    <Badge variant={variant} className="capitalize">
      {priority}
    </Badge>
  );
}
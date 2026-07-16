"use client";

import { Badge } from "@/components/ui/badge";

const statusVariant: Record<string, "success" | "warning" | "neutral" | "default" | "destructive"> = {
  new: "warning",
  in_progress: "default",
  closed: "success",
  completed: "success",
  received: "neutral",
  processing: "default",
  classified: "warning",
  linked: "success",
  failed: "destructive",
  archived: "neutral",
};

const statusLabel: Record<string, string> = {
  new: "New",
  in_progress: "In Progress",
  closed: "Closed",
  completed: "Completed",
  received: "Received",
  processing: "Processing",
  classified: "Classified",
  linked: "Linked",
  failed: "Failed",
  archived: "Archived",
};

type InteractionStatusBadgeProps = {
  status: string;
};

export function InteractionStatusBadge({ status }: InteractionStatusBadgeProps) {
  const variant = statusVariant[status] ?? "neutral";
  const label = statusLabel[status] ?? status;
  return (
    <Badge variant={variant} className="capitalize">
      {label}
    </Badge>
  );
}
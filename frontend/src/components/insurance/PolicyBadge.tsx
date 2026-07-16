"use client";

import { cn } from "@/lib/cn";

type PolicyBadgeProps = {
  policyNumber?: string | null;
  className?: string;
};

export function PolicyBadge({ policyNumber, className }: PolicyBadgeProps) {
  if (!policyNumber) return null;
  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-medium bg-muted text-muted-foreground",
        className,
      )}
    >
      {policyNumber}
    </span>
  );
}

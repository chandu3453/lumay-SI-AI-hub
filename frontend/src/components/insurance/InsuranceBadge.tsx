"use client";

import { getLineColor } from "@/lib/insurance";
import { cn } from "@/lib/cn";

type InsuranceBadgeProps = {
  line?: string | null;
  className?: string;
};

export function InsuranceBadge({ line, className }: InsuranceBadgeProps) {
  if (!line) return null;
  const color = getLineColor(line);
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-medium",
        className,
      )}
      style={{
        backgroundColor: `${color}12`,
        color: color,
      }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: color }} />
      {line}
    </span>
  );
}

"use client";

import { INSURANCE_LINES } from "@/lib/insurance";
import { cn } from "@/lib/cn";

type InsuranceSelectorProps = {
  value: string;
  onChange: (value: string) => void;
  className?: string;
  includeAll?: boolean;
};

export function InsuranceSelector({ value, onChange, className, includeAll = true }: InsuranceSelectorProps) {
  const items = includeAll ? INSURANCE_LINES : INSURANCE_LINES.filter((l) => l !== "All");
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={cn(
        "text-sm border border-border rounded-lg px-3 py-2 bg-white text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-primary/20 min-w-[160px]",
        className,
      )}
    >
      {items.map((line) => (
        <option key={line} value={line}>
          {line === "All" ? "All Insurance Lines" : line}
        </option>
      ))}
    </select>
  );
}

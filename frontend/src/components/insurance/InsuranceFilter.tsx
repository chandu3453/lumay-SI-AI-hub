"use client";

import { useInsuranceStore } from "@/stores/insurance.store";
import { INSURANCE_LINES } from "@/lib/insurance";
import { cn } from "@/lib/cn";

type InsuranceFilterProps = {
  className?: string;
};

export function InsuranceFilter({ className }: InsuranceFilterProps) {
  const selectedLine = useInsuranceStore((s) => s.selectedLine);
  const setSelectedLine = useInsuranceStore((s) => s.setSelectedLine);

  return (
    <select
      value={selectedLine}
      onChange={(e) => setSelectedLine(e.target.value)}
      className={cn(
        "text-sm border border-border rounded-lg px-3 py-1.5 bg-white text-[#0F172A] focus:outline-none focus:ring-2 focus:ring-primary/20 min-w-[160px]",
        className,
      )}
    >
      {INSURANCE_LINES.map((line) => (
        <option key={line} value={line}>
          {line === "All" ? "All Insurance Lines" : line}
        </option>
      ))}
    </select>
  );
}

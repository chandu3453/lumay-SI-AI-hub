"use client";

import { PolicyCard } from "./PolicyCard";

type PolicySummary = {
  productName: string;
  policyNumber: string;
  status: "active" | "expiring" | "lapsed" | "pending";
  line: string;
};

type InsuranceSummaryProps = {
  policies: PolicySummary[];
  totalLabel?: string;
};

export function InsuranceSummary({ policies, totalLabel }: InsuranceSummaryProps) {
  if (policies.length === 0) {
    return (
      <div className="text-center py-6">
        <p className="text-sm text-muted-foreground">No insurance policies found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        {policies.map((p, i) => (
          <PolicyCard key={i} {...p} />
        ))}
      </div>
      {totalLabel && (
        <p className="text-xs text-muted-foreground">{totalLabel}</p>
      )}
    </div>
  );
}

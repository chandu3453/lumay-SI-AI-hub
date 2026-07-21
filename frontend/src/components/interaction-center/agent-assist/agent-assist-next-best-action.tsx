"use client";

import { ArrowRight } from "lucide-react";

import type { NextBestAction } from "@/features/agent-assist/types";

/** Recommendations only — the employee stays in control, nothing here
 * triggers any action on its own. */
export function AgentAssistNextBestAction({ actions }: { actions: NextBestAction[] }) {
  if (actions.length === 0) return null;
  return (
    <div className="space-y-1.5">
      <h3 className="text-xs font-semibold text-muted-foreground">Next Best Action</h3>
      <ul className="space-y-1">
        {actions.map((action, index) => (
          <li key={index} className="flex items-start gap-1.5 text-xs">
            <ArrowRight className="mt-0.5 h-3 w-3 shrink-0 text-primary" />
            <span>
              <span className="font-medium">{action.action}</span>
              {action.rationale ? (
                <span className="text-muted-foreground"> — {action.rationale}</span>
              ) : null}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

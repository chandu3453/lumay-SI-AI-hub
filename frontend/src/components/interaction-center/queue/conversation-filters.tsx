"use client";

import { useState } from "react";
import { Filter, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { ConversationFilters } from "@/stores/conversation-ui.store";
import type { ConversationChannel, ConversationPriority } from "@/features/conversations/types";

const CHANNELS: ConversationChannel[] = ["web_chat", "voice", "whatsapp", "email", "complaint"];
const PRIORITIES: ConversationPriority[] = ["low", "medium", "high", "critical"];

/** Channel/Priority/Assigned-Employee/Complaint/Date filters — Status is its
 * own tab strip, Conversation ID/Customer Name are covered by search.
 * Employee/Complaint are plain UUID inputs: no employee-directory or
 * complaint-picker API is in scope for this phase, so this is honest about
 * what's actually wired rather than faking a picker. */
export function ConversationFiltersPanel({
  filters,
  onChange,
}: {
  filters: ConversationFilters;
  onChange: (filters: ConversationFilters) => void;
}) {
  const [open, setOpen] = useState(false);
  const activeCount = Object.values(filters).filter(Boolean).length;

  return (
    <div className="relative">
      <Button variant="outline" size="sm" className="h-8 gap-1.5" onClick={() => setOpen((o) => !o)}>
        <Filter className="h-3.5 w-3.5" />
        Filters
        {activeCount > 0 ? (
          <span className="ml-0.5 rounded-full bg-primary px-1.5 text-[10px] text-primary-foreground">
            {activeCount}
          </span>
        ) : null}
      </Button>

      {open ? (
        <div className="absolute right-0 top-full z-20 mt-1 w-72 rounded-lg border border-border bg-popover p-3 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold">Filters</span>
            {activeCount > 0 ? (
              <button
                type="button"
                onClick={() => onChange({})}
                className="text-[11px] text-muted-foreground hover:text-foreground"
              >
                Clear all
              </button>
            ) : null}
          </div>

          <div className="mt-2 space-y-2.5">
            <label className="block text-[11px] font-medium text-muted-foreground">
              Channel
              <select
                value={filters.channel ?? ""}
                onChange={(e) =>
                  onChange({ ...filters, channel: (e.target.value || undefined) as ConversationChannel | undefined })
                }
                className="mt-1 h-8 w-full rounded-md border border-border bg-background px-2 text-xs"
              >
                <option value="">All channels</option>
                {CHANNELS.map((c) => (
                  <option key={c} value={c}>
                    {c.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
            </label>

            <label className="block text-[11px] font-medium text-muted-foreground">
              Priority
              <select
                value={filters.priority ?? ""}
                onChange={(e) =>
                  onChange({ ...filters, priority: (e.target.value || undefined) as ConversationPriority | undefined })
                }
                className="mt-1 h-8 w-full rounded-md border border-border bg-background px-2 text-xs"
              >
                <option value="">All priorities</option>
                {PRIORITIES.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </label>

            <label className="block text-[11px] font-medium text-muted-foreground">
              Assigned employee (ID)
              <input
                type="text"
                value={filters.assignedEmployeeId ?? ""}
                onChange={(e) => onChange({ ...filters, assignedEmployeeId: e.target.value || undefined })}
                placeholder="employee-uuid"
                className="mt-1 h-8 w-full rounded-md border border-border bg-background px-2 text-xs"
              />
            </label>

            <label className="block text-[11px] font-medium text-muted-foreground">
              Complaint (ID)
              <input
                type="text"
                value={filters.complaintId ?? ""}
                onChange={(e) => onChange({ ...filters, complaintId: e.target.value || undefined })}
                placeholder="complaint-uuid"
                className="mt-1 h-8 w-full rounded-md border border-border bg-background px-2 text-xs"
              />
            </label>

            <div className="grid grid-cols-2 gap-2">
              <label className="block text-[11px] font-medium text-muted-foreground">
                From
                <input
                  type="date"
                  value={filters.dateFrom ?? ""}
                  onChange={(e) => onChange({ ...filters, dateFrom: e.target.value || undefined })}
                  className="mt-1 h-8 w-full rounded-md border border-border bg-background px-2 text-xs"
                />
              </label>
              <label className="block text-[11px] font-medium text-muted-foreground">
                To
                <input
                  type="date"
                  value={filters.dateTo ?? ""}
                  onChange={(e) => onChange({ ...filters, dateTo: e.target.value || undefined })}
                  className="mt-1 h-8 w-full rounded-md border border-border bg-background px-2 text-xs"
                />
              </label>
            </div>
          </div>

          <button
            type="button"
            onClick={() => setOpen(false)}
            className="mt-3 inline-flex items-center gap-1 text-[11px] text-muted-foreground hover:text-foreground"
          >
            <X className="h-3 w-3" /> Close
          </button>
        </div>
      ) : null}
    </div>
  );
}

"use client";

import { Search, X } from "lucide-react";

import { cn } from "@/lib/cn";

/** Debounced by the caller (useDebounce) before it reaches the list query —
 * matches customer name, conversation id, complaint id/policy number, or
 * message text server-side (GET /conversations?search=). */
export function ConversationSearch({
  value,
  onChange,
  className,
}: {
  value: string;
  onChange: (value: string) => void;
  className?: string;
}) {
  return (
    <div className={cn("relative", className)}>
      <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search customer, conversation, complaint, policy, message…"
        className="h-8 w-full rounded-md border border-border bg-background pl-8 pr-7 text-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
      />
      {value ? (
        <button
          type="button"
          onClick={() => onChange("")}
          aria-label="Clear search"
          className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      ) : null}
    </div>
  );
}

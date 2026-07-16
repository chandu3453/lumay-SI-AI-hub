"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/cn";
import { useNotificationCenter } from "./use-notifications";

export function NotificationPagination() {
  const { page, setPage, totalPages, total, pageSize } = useNotificationCenter();

  if (totalPages <= 1) return null;

  const pages: number[] = [];
  const start = Math.max(1, page - 1);
  const end = Math.min(totalPages, page + 1);
  for (let i = start; i <= end; i++) pages.push(i);

  return (
    <div className="flex items-center justify-between pt-4 border-t border-border">
      <p className="text-sm text-muted-foreground">
        Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, total)} of {total}
      </p>
      <div className="flex items-center gap-1">
        <button
          onClick={() => setPage(page - 1)}
          disabled={page <= 1}
          className="p-2 rounded-lg border border-border bg-white hover:bg-accent disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        {start > 1 && (
          <>
            <button onClick={() => setPage(1)} className="px-3 py-1.5 text-sm rounded-lg border border-border bg-white hover:bg-accent transition-colors">1</button>
            {start > 2 && <span className="px-1 text-muted-foreground">...</span>}
          </>
        )}
        {pages.map((p) => (
          <button
            key={p}
            onClick={() => setPage(p)}
            className={cn(
              "px-3 py-1.5 text-sm rounded-lg border transition-colors",
              p === page
                ? "bg-primary text-primary-foreground border-primary"
                : "border-border bg-white hover:bg-accent text-[#0F172A]",
            )}
          >
            {p}
          </button>
        ))}
        {end < totalPages && (
          <>
            {end < totalPages - 1 && <span className="px-1 text-muted-foreground">...</span>}
            <button onClick={() => setPage(totalPages)} className="px-3 py-1.5 text-sm rounded-lg border border-border bg-white hover:bg-accent transition-colors">{totalPages}</button>
          </>
        )}
        <button
          onClick={() => setPage(page + 1)}
          disabled={page >= totalPages}
          className="p-2 rounded-lg border border-border bg-white hover:bg-accent disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
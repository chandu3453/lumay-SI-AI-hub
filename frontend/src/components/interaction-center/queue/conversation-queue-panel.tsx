"use client";

import { useRef, useState } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";

import { Skeleton } from "@/components/ui/skeleton";
import { useDebounce } from "@/hooks/use-debounce";
import { cn } from "@/lib/cn";
import { useConversationList } from "@/features/conversations/hooks/use-conversations";
import { CONVERSATION_STATUS_TABS, type ConversationStatus } from "@/features/conversations/types";
import { useConversationUiStore } from "@/stores/conversation-ui.store";

import { ConversationCard } from "./conversation-card";
import { ConversationFiltersPanel } from "./conversation-filters";
import { ConversationSearch } from "./conversation-search";

/** Left panel — status tabs (the 8 spec'd states) + search + filters +
 * virtualized queue. Virtualized via @tanstack/react-virtual since the old
 * ConversationList rendered its full array with a plain .map (confirmed no
 * windowing existed anywhere in this app), and this queue is meant to stay
 * fast under real (potentially long) conversation volumes. */
export function ConversationQueuePanel() {
  const search = useConversationUiStore((s) => s.search);
  const setSearch = useConversationUiStore((s) => s.setSearch);
  const filters = useConversationUiStore((s) => s.filters);
  const setFilters = useConversationUiStore((s) => s.setFilters);
  const selectedId = useConversationUiStore((s) => s.selectedConversationId);
  const selectConversation = useConversationUiStore((s) => s.selectConversation);

  const [activeTab, setActiveTab] = useState<ConversationStatus | "all">("all");
  const debouncedSearch = useDebounce(search, 300);

  const { data, isLoading } = useConversationList({
    search: debouncedSearch || undefined,
    status: activeTab === "all" ? filters.status : activeTab,
    channel: filters.channel,
    priority: filters.priority,
    assigned_employee_id: filters.assignedEmployeeId,
    complaint_id: filters.complaintId,
    date_from: filters.dateFrom,
    date_to: filters.dateTo,
    page: 1,
    page_size: 100,
  });

  const items = data?.items ?? [];

  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 140,
    overscan: 8,
  });

  return (
    <div className="flex h-full w-[320px] shrink-0 flex-col border-r border-border bg-background">
      <div className="border-b border-border p-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold">Conversations</h2>
          <span className="text-xs text-muted-foreground">{data?.total ?? 0}</span>
        </div>
        <div className="mt-2 flex items-center gap-1.5">
          <ConversationSearch value={search} onChange={setSearch} className="flex-1" />
          <ConversationFiltersPanel filters={filters} onChange={setFilters} />
        </div>
      </div>

      <div className="flex gap-1 overflow-x-auto border-b border-border px-2 py-1.5">
        {CONVERSATION_STATUS_TABS.map((tab) => (
          <button
            key={tab.value}
            type="button"
            onClick={() => setActiveTab(tab.value)}
            className={cn(
              "shrink-0 rounded-md px-2 py-1 text-[11px] font-medium transition-colors",
              activeTab === tab.value
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:bg-accent",
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div ref={parentRef} className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="space-y-2 p-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        ) : items.length === 0 ? (
          <div className="p-6 text-center text-xs text-muted-foreground">No conversations found.</div>
        ) : (
          <div style={{ height: virtualizer.getTotalSize(), position: "relative" }}>
            {virtualizer.getVirtualItems().map((virtualItem) => {
              const conversation = items[virtualItem.index];
              return (
                <div
                  key={conversation.id}
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    width: "100%",
                    transform: `translateY(${virtualItem.start}px)`,
                  }}
                >
                  <ConversationCard
                    conversation={conversation}
                    isSelected={conversation.id === selectedId}
                    onSelect={() => selectConversation(conversation.id)}
                  />
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

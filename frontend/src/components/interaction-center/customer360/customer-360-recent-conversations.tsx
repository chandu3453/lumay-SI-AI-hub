"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { formatRelative } from "@/lib/formatters";
import { useConversationList } from "@/features/conversations/hooks/use-conversations";
import { useConversationUiStore } from "@/stores/conversation-ui.store";
import {
  ChannelBadge,
  StatusBadge,
} from "@/components/interaction-center/shared/conversation-badges";

/** Recent Conversations — wires up `useConversationList({ customer_id })`,
 * which already existed (Sprint 28) but nothing in Customer 360 called it
 * with a customer_id filter until now. Clicking a row switches the active
 * conversation in the timeline, same store the queue panel already uses. */
export function Customer360RecentConversations({
  customerId,
  currentConversationId,
}: {
  customerId: string | null;
  currentConversationId?: string | null;
}) {
  const selectConversation = useConversationUiStore((s) => s.selectConversation);
  const { data, isLoading } = useConversationList(
    customerId ? { customer_id: customerId, page_size: 10 } : undefined,
  );

  if (!customerId) return null;
  if (isLoading) return <Skeleton className="h-24 w-full" />;

  const items = data?.items ?? [];
  if (items.length === 0) return null;

  return (
    <Card>
      <CardHeader className="p-3 pb-1.5">
        <CardTitle className="text-xs">Recent Conversations ({items.length})</CardTitle>
      </CardHeader>
      <CardContent className="space-y-1.5 p-3 pt-0">
        {items.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => selectConversation(c.id)}
            className={`flex w-full items-center justify-between rounded-md border p-2 text-left text-xs transition-colors hover:bg-accent ${
              c.id === currentConversationId ? "border-primary" : "border-border"
            }`}
          >
            <div className="flex items-center gap-1.5">
              <ChannelBadge channel={c.current_channel} />
              <StatusBadge status={c.current_status} />
            </div>
            <span className="text-[10px] text-muted-foreground">{formatRelative(c.updated_at)}</span>
          </button>
        ))}
      </CardContent>
    </Card>
  );
}

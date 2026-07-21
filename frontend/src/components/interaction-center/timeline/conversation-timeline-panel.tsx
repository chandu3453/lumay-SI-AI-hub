"use client";

import { useEffect, useRef } from "react";
import { Inbox } from "lucide-react";

import { Skeleton } from "@/components/ui/skeleton";
import { useConversationTimelineSSE } from "@/hooks/use-conversation-sse";
import {
  useConversation,
  useConversationParticipants,
  useConversationTimeline,
} from "@/features/conversations/hooks/use-conversations";
import { ChannelBadge, StatusBadge } from "@/components/interaction-center/shared/conversation-badges";

import { ConversationOwnerBadge } from "./conversation-owner-badge";
import { ConversationToolbar } from "./conversation-toolbar";
import { InternalNotesPanel } from "./internal-notes-panel";
import { PresenceIndicators } from "./presence-indicators";
import { TimelineComposeBar } from "./timeline-compose-bar";
import { TimelineItemRow } from "./timeline-item";

export function ConversationTimelinePanel({ conversationId }: { conversationId: string | null }) {
  const { data: conversation } = useConversation(conversationId);
  const { data: timeline, isLoading } = useConversationTimeline(conversationId);
  const { data: participants = [] } = useConversationParticipants(conversationId);
  useConversationTimelineSSE(conversationId);

  const scrollRef = useRef<HTMLDivElement>(null);
  const itemCount = timeline?.items.length ?? 0;

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [itemCount]);

  if (!conversationId) {
    return (
      <div className="flex h-full flex-1 flex-col items-center justify-center gap-2 text-muted-foreground">
        <Inbox className="h-8 w-8" />
        <p className="text-sm">Select a conversation to view its timeline.</p>
      </div>
    );
  }

  if (!conversation) {
    return (
      <div className="flex h-full flex-1 flex-col gap-2 p-4">
        <Skeleton className="h-8 w-1/2" />
        <Skeleton className="h-full w-full" />
      </div>
    );
  }

  return (
    <div className="flex h-full flex-1 flex-col">
      <div className="flex items-center justify-between border-b border-border p-3">
        <div>
          <h2 className="text-sm font-semibold">
            {conversation.customer_id ? `Customer ${conversation.customer_id.slice(0, 8)}` : "Anonymous customer"}
          </h2>
          <p className="font-mono text-[11px] text-muted-foreground">{conversation.id}</p>
        </div>
        <div className="flex flex-col items-end gap-1.5">
          <div className="flex items-center gap-1.5">
            <ChannelBadge channel={conversation.current_channel} />
            <StatusBadge status={conversation.current_status} />
          </div>
          <ConversationOwnerBadge conversation={conversation} participants={participants} />
        </div>
      </div>

      <div className="border-b border-border px-3 py-1.5">
        <PresenceIndicators conversationId={conversationId} />
      </div>

      <ConversationToolbar conversation={conversation} participants={participants} />

      <InternalNotesPanel conversationId={conversation.id} items={timeline?.items ?? []} />

      <div ref={scrollRef} className="flex-1 space-y-2.5 overflow-y-auto p-3">
        {isLoading ? (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-2/3" />
            ))}
          </div>
        ) : itemCount === 0 ? (
          <p className="p-6 text-center text-xs text-muted-foreground">No messages or events yet.</p>
        ) : (
          timeline?.items.map((item) => <TimelineItemRow key={`${item.type}-${item.id}`} item={item} />)
        )}
      </div>

      <TimelineComposeBar
        conversationId={conversation.id}
        channel={conversation.current_channel}
        disabled={conversation.current_status === "closed"}
      />
    </div>
  );
}

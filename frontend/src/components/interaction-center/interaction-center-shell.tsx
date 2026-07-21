"use client";

import { PanelRightClose, PanelRightOpen } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useConversationsQueueSSE } from "@/hooks/use-conversation-sse";
import { useConversationUiStore } from "@/stores/conversation-ui.store";

import { Customer360Panel } from "./customer360/customer-360-panel";
import { ConversationQueuePanel } from "./queue/conversation-queue-panel";
import { ConversationTimelinePanel } from "./timeline/conversation-timeline-panel";

/** Sprint 28 Phase 3 — Employee Omnichannel Interaction Center. 3-panel
 * layout (queue / timeline / customer 360) replacing the old per-channel
 * "workspace" paradigm — every channel now shares one merged timeline. */
export function InteractionCenterShell() {
  useConversationsQueueSSE();
  const selectedConversationId = useConversationUiStore((s) => s.selectedConversationId);
  const rightPanelOpen = useConversationUiStore((s) => s.rightPanelOpen);
  const toggleRightPanel = useConversationUiStore((s) => s.toggleRightPanel);

  return (
    <div className="flex h-[calc(100vh-112px)] overflow-hidden rounded-xl border border-border bg-background">
      <ConversationQueuePanel />
      <ConversationTimelinePanel conversationId={selectedConversationId} />
      <div className="relative flex">
        <Button
          variant="ghost"
          size="icon"
          className="absolute -left-9 top-2 z-10 h-7 w-7"
          onClick={toggleRightPanel}
          aria-label={rightPanelOpen ? "Hide customer panel" : "Show customer panel"}
        >
          {rightPanelOpen ? <PanelRightClose className="h-4 w-4" /> : <PanelRightOpen className="h-4 w-4" />}
        </Button>
        {rightPanelOpen ? <Customer360Panel conversationId={selectedConversationId} /> : null}
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";
import Link from "next/link";
import { ExternalLink, Sparkles, Users } from "lucide-react";

import { cn } from "@/lib/cn";
import { useConversation } from "@/features/conversations/hooks/use-conversations";
import { AgentAssistPanel } from "@/components/interaction-center/agent-assist/agent-assist-panel";

import { Customer360Complaints } from "./customer-360-complaints";
import { Customer360Identity } from "./customer-360-identity";
import { Customer360Overview } from "./customer-360-overview";
import { Customer360PlaceholderSection } from "./customer-360-placeholder-section";
import { Customer360RecentConversations } from "./customer-360-recent-conversations";
import { Customer360Status } from "./customer-360-status";

type Tab = "customer360" | "agent-assist";

/** Right panel — tabbed between Customer 360 (identity/complaints/status,
 * backed by real data where a domain exists) and Agent Assist (Sprint 28
 * Phase 5's live AI copilot). Replaces the "Current Intent"/"AI Summary"
 * placeholders Phase 4 left here — those two now live in the Agent Assist
 * tab as real, generated content. */
export function Customer360Panel({ conversationId }: { conversationId: string | null }) {
  const { data: conversation } = useConversation(conversationId);
  const [tab, setTab] = useState<Tab>("customer360");

  if (!conversationId || !conversation) {
    return (
      <div className="flex h-full w-[300px] shrink-0 flex-col items-center justify-center gap-2 border-l border-border text-muted-foreground">
        <Users className="h-6 w-6" />
        <p className="text-xs">No conversation selected.</p>
      </div>
    );
  }

  return (
    <div className="flex h-full w-[300px] shrink-0 flex-col overflow-y-auto border-l border-border bg-background">
      <div className="flex border-b border-border">
        <button
          type="button"
          onClick={() => setTab("customer360")}
          className={cn(
            "flex-1 px-3 py-2 text-xs font-medium",
            tab === "customer360"
              ? "border-b-2 border-primary text-foreground"
              : "text-muted-foreground hover:bg-accent",
          )}
        >
          Customer 360
        </button>
        <button
          type="button"
          onClick={() => setTab("agent-assist")}
          className={cn(
            "flex flex-1 items-center justify-center gap-1 px-3 py-2 text-xs font-medium",
            tab === "agent-assist"
              ? "border-b-2 border-primary text-foreground"
              : "text-muted-foreground hover:bg-accent",
          )}
        >
          <Sparkles className="h-3 w-3" /> Agent Assist
        </button>
      </div>

      {tab === "customer360" ? (
        <div className="flex flex-col gap-3 p-3">
          <Customer360Identity customerId={conversation.customer_id} />
          {conversation.customer_id ? (
            <Link
              href={`/customers/${conversation.customer_id}`}
              className="flex items-center justify-center gap-1 rounded-md border border-border py-1.5 text-[11px] font-medium text-muted-foreground hover:bg-accent"
            >
              <ExternalLink className="h-3 w-3" /> View full profile
            </Link>
          ) : null}
          <Customer360Overview customerId={conversation.customer_id} />
          <Customer360Status conversation={conversation} />
          <Customer360RecentConversations
            customerId={conversation.customer_id}
            currentConversationId={conversation.id}
          />
          <Customer360Complaints customerId={conversation.customer_id} />

          <Customer360PlaceholderSection title="Policies" />
          <Customer360PlaceholderSection title="Active Claims" />
          <Customer360PlaceholderSection title="Renewals" />
          <Customer360PlaceholderSection title="Recent Payments" />
        </div>
      ) : (
        <AgentAssistPanel conversationId={conversation.id} />
      )}
    </div>
  );
}

"use client";

import { RefreshCw, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { formatRelative } from "@/lib/formatters";
import {
  useAgentAssistInsight,
  useRegenerateAgentAssist,
} from "@/features/agent-assist/hooks/use-agent-assist";
import { isAgentAssistGenerated } from "@/features/agent-assist/types";
import { useConversationUiStore } from "@/stores/conversation-ui.store";

import { AgentAssistAlerts } from "./agent-assist-alerts";
import { AgentAssistIntent } from "./agent-assist-intent";
import { AgentAssistKnowledge } from "./agent-assist-knowledge";
import { AgentAssistNextBestAction } from "./agent-assist-next-best-action";
import { AgentAssistSentiment } from "./agent-assist-sentiment";
import { AgentAssistSuggestedReplies } from "./agent-assist-suggested-replies";
import { AgentAssistSummary } from "./agent-assist-summary";

/** The AI copilot — supports the employee, never replaces them. Every
 * section here is either read-only context or a suggestion the employee
 * must explicitly accept/edit before anything reaches the customer. */
export function AgentAssistPanel({ conversationId }: { conversationId: string }) {
  const { data, isLoading } = useAgentAssistInsight(conversationId);
  const regenerate = useRegenerateAgentAssist();
  const setDraftText = useConversationUiStore((s) => s.setDraftText);

  if (isLoading) {
    return (
      <div className="space-y-3 p-1">
        <Skeleton className="h-4 w-2/3" />
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-8 w-1/2" />
      </div>
    );
  }

  if (!isAgentAssistGenerated(data)) {
    return (
      <div className="flex flex-col items-center gap-2 p-4 text-center text-muted-foreground">
        <Sparkles className="h-6 w-6" />
        <p className="text-xs">
          {data?.message ?? "Agent Assist insights have not been generated yet."}
        </p>
        <Button
          size="sm"
          variant="outline"
          className="h-7 gap-1 text-xs"
          onClick={() => regenerate.mutate(conversationId)}
          disabled={regenerate.isPending}
        >
          <RefreshCw className="h-3 w-3" /> Generate now
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-1">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-1 text-[11px] text-muted-foreground">
          <Sparkles className="h-3 w-3" />
          Updated {formatRelative(data.updated_at)}
          {data.stalled ? " · stalled" : ""}
        </span>
        <Button
          size="sm"
          variant="outline"
          className="h-6 gap-1 px-2 text-[11px]"
          onClick={() => regenerate.mutate(conversationId)}
          disabled={regenerate.isPending}
        >
          <RefreshCw className={regenerate.isPending ? "h-3 w-3 animate-spin" : "h-3 w-3"} />
          Refresh
        </Button>
      </div>

      <AgentAssistAlerts alerts={data.alerts} />
      <AgentAssistSummary insight={data} />
      <AgentAssistIntent insight={data} />
      <AgentAssistSentiment insight={data} conversationId={conversationId} />
      <AgentAssistSuggestedReplies replies={data.suggested_replies} onUseDraft={setDraftText} />
      <AgentAssistKnowledge articles={data.knowledge_articles} />
      <AgentAssistNextBestAction actions={data.next_best_actions} />
    </div>
  );
}

"use client";

import { Minus, TrendingDown, TrendingUp } from "lucide-react";

import { Badge, type BadgeProps } from "@/components/ui/badge";
import { useAgentAssistHistory } from "@/features/agent-assist/hooks/use-agent-assist";
import type { AgentAssistInsight } from "@/features/agent-assist/types";

const SENTIMENT_VARIANT: Record<string, BadgeProps["variant"]> = {
  positive: "success",
  neutral: "neutral",
  frustrated: "warning",
  escalated: "destructive",
};

const SENTIMENT_LABEL: Record<string, string> = {
  positive: "Positive",
  neutral: "Neutral",
  frustrated: "Frustrated",
  escalated: "Escalated",
};

// Ordinal scale for a cheap trend arrow — no extra LLM calls, just compares
// the last two generations (see design decision 6 in the Phase 5 plan).
const SENTIMENT_ORDINAL: Record<string, number> = {
  positive: 2,
  neutral: 1,
  frustrated: 0,
  escalated: -1,
};

export function AgentAssistSentiment({
  insight,
  conversationId,
}: {
  insight: AgentAssistInsight;
  conversationId: string;
}) {
  const { data: history = [] } = useAgentAssistHistory(conversationId);
  if (!insight.sentiment) return null;

  let trendIcon = <Minus className="h-3 w-3 text-muted-foreground" />;
  if (history.length >= 2) {
    const prev = history[history.length - 2]?.sentiment;
    const curr = history[history.length - 1]?.sentiment;
    const prevScore = prev ? SENTIMENT_ORDINAL[prev] : undefined;
    const currScore = curr ? SENTIMENT_ORDINAL[curr] : undefined;
    if (prevScore != null && currScore != null) {
      if (currScore > prevScore) trendIcon = <TrendingUp className="h-3 w-3 text-success" />;
      else if (currScore < prevScore) trendIcon = <TrendingDown className="h-3 w-3 text-destructive" />;
    }
  }

  return (
    <div className="space-y-1">
      <h3 className="text-xs font-semibold text-muted-foreground">Customer Sentiment</h3>
      <div className="flex items-center gap-1.5">
        <Badge variant={SENTIMENT_VARIANT[insight.sentiment] ?? "neutral"}>
          {SENTIMENT_LABEL[insight.sentiment] ?? insight.sentiment}
        </Badge>
        {trendIcon}
      </div>
    </div>
  );
}

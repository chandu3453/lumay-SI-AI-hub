// Mirrors backend/domains/agent_assist/schemas/agent_assist_schemas.py exactly
// (snake_case, wire-format) — same convention as features/conversations/types.ts.

export interface NextBestAction {
  action: string;
  rationale: string;
}

export interface SuggestedReply {
  type: string;
  content: string;
}

export interface KnowledgeArticleSuggestion {
  source: string;
  id: string;
  title: string;
  snippet: string;
  score: number;
}

export interface ConversationInsights {
  repeated_questions: string[];
  missing_info: string[];
  compliance_risks: string[];
  unanswered_questions: string[];
}

export interface AgentAssistAlert {
  type: string;
  severity: "info" | "warning" | "critical";
  message: string;
}

export interface AgentAssistInsight {
  id: string;
  created_at: string;
  updated_at: string;
  conversation_id: string;
  message_count_at_generation: number;
  summary: string | null;
  intent: string | null;
  intent_confidence: number | null;
  sentiment: "positive" | "neutral" | "frustrated" | "escalated" | null;
  sentiment_polarity: number | null;
  escalation_risk_score: number | null;
  escalation_risk_level: string | null;
  next_best_actions: NextBestAction[];
  knowledge_articles: KnowledgeArticleSuggestion[];
  suggested_replies: SuggestedReply[];
  insights: ConversationInsights;
  alerts: AgentAssistAlert[];
  complaint_severity_at_generation: string | null;
  duration_minutes: number;
  minutes_since_last_message: number | null;
  stalled: boolean;
}

export interface AgentAssistEmptyState {
  conversation_id: string;
  generated: false;
  message: string;
}

export type AgentAssistInsightOrEmpty = AgentAssistInsight | AgentAssistEmptyState;

export function isAgentAssistGenerated(
  data: AgentAssistInsightOrEmpty | null | undefined,
): data is AgentAssistInsight {
  return !!data && "id" in data;
}

export interface AgentAssistHistoryItem {
  id: string;
  created_at: string;
  sentiment: string | null;
  sentiment_polarity: number | null;
  intent: string | null;
  intent_confidence: number | null;
}

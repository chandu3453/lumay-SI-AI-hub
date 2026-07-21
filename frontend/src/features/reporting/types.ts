// Mirrors backend/domains/reporting/schemas/reporting_schemas.py exactly
// (snake_case, wire-format) — same convention as every other feature's types.

import type { Conversation, ConversationSummary, TimelineItem } from "@/features/conversations/types";

export interface NotAvailableSection {
  available: false;
  message: string;
}

// ── Customer 360 ────────────────────────────────────────────────────────

export interface CustomerInfo {
  id: string;
  customer_number: string | null;
  full_name: string;
  email: string | null;
  mobile_number: string | null;
  segment: string;
  status: string;
}

export interface AssignedEmployee {
  id: string;
  full_name: string | null;
}

export interface ConversationStatistics {
  total_conversations: number;
  avg_resolution_seconds: number | null;
  escalation_count: number;
}

export interface CustomerOverview {
  open_complaints: number;
  conversation_count: number;
  avg_resolution_seconds: number | null;
  escalation_count: number;
  open_claims: NotAvailableSection;
  pending_renewals: NotAvailableSection;
  upcoming_payments: NotAvailableSection;
  policy_expiry: NotAvailableSection;
}

export interface AgentAssistSnapshot {
  summary: string | null;
  sentiment: string | null;
  intent: string | null;
  intent_confidence: number | null;
  generated_at: string | null;
}

export interface ComplaintSummaryLite {
  id: string;
  complaint_number: string | null;
  title: string;
  category: string;
  priority: string;
  severity: string;
  status: string;
  assigned_queue: string | null;
  created_at: string;
  theme: string | null;
  sentiment: string | null;
  sentiment_trend: string | null;
  escalation_risk_score: number | null;
}

export interface Customer360Response {
  customer: CustomerInfo;
  current_conversation: Conversation | null;
  assigned_employee: AssignedEmployee | null;
  recent_conversations: ConversationSummary[];
  conversation_statistics: ConversationStatistics;
  overview: CustomerOverview;
  agent_assist: AgentAssistSnapshot | null;
  complaints: ComplaintSummaryLite[];
  policies: NotAvailableSection;
  claims: NotAvailableSection;
  payments: NotAvailableSection;
  renewals: NotAvailableSection;
  documents: NotAvailableSection;
}

export interface CustomerActivityTimelineResponse {
  items: TimelineItem[];
  total: number;
  page: number;
  page_size: number;
}

// ── Enterprise Analytics ────────────────────────────────────────────────

export interface ConversationAnalyticsSummary {
  total_conversations: number;
  active_conversations: number;
  resolved_conversations: number;
  escalated_conversations: number;
  ai_handled: number;
  human_handled: number;
  ai_to_human_handoffs: number;
  avg_response_time_seconds: number | null;
  avg_resolution_time_seconds: number | null;
  avg_conversation_duration_seconds: number | null;
  customer_satisfaction: number | null;
}

export interface VoiceVsChat {
  voice: number;
  chat: number;
}

export interface ConversationDistributions {
  intent_distribution: Record<string, number>;
  sentiment_distribution: Record<string, number>;
  complaint_distribution: Record<string, number>;
  channel_distribution: Record<string, number>;
  voice_vs_chat: VoiceVsChat;
  policy_category_distribution: NotAvailableSection;
}

export interface TrendPoint {
  period: string;
  count: number;
}

export interface SentimentTrendPoint {
  period: string;
  positive: number;
  neutral: number;
  frustrated: number;
  escalated: number;
}

export interface IntentTrendPoint {
  period: string;
  counts: Record<string, number>;
}

export interface AiUtilizationTrendPoint {
  period: string;
  ai_handled: number;
  human_handled: number;
}

export interface ConversationTrends {
  granularity: string;
  conversation_trend: TrendPoint[];
  complaint_trend: TrendPoint[];
  sentiment_trend: SentimentTrendPoint[];
  intent_trend: IntentTrendPoint[];
  ai_utilization_trend: AiUtilizationTrendPoint[];
}

export interface EmployeeAnalyticsItem {
  employee_id: string;
  employee_name: string | null;
  assigned_conversations: number;
  resolved: number;
  escalated: number;
  avg_resolution_seconds: number | null;
  ai_assistance_usage: number;
  transfer_count: number;
}

export interface SupervisorDashboard {
  queue_by_status: Record<string, number>;
  live_conversations: number;
  high_priority_complaints: number;
  escalated_cases: number;
  ai_active_conversations: number;
  employees_online: number;
}

export interface ReportingQueryFilters {
  date_from?: string;
  date_to?: string;
  channel?: string;
  assigned_employee_id?: string;
  priority?: string;
}

export type ExportReport = "summary" | "distributions" | "employees";
export type ExportFormat = "csv" | "xlsx" | "pdf";

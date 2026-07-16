import type { Entity, UUID } from "./common";

export type User = Entity & {
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
};

export type Customer = Entity & {
  customer_number: string | null;
  external_ref: string;
  full_name: string;
  email: string | null;
  mobile_number: string | null;
  segment: string;
  status: string;
  city: string | null;
  state: string | null;
  risk_level?: string | null;
  complaint_count?: number;
  last_interaction?: string | null;
  customer_type?: string | null;
  customer_since?: string | null;
  whatsapp?: string | null;
  repeat_complaints?: number;
  last_complaint?: string | null;
  total_complaints?: number;
  lifetime_value?: number | null;
  churn_risk?: string | null;
  ai_recommendations?: string | null;
};

// FR-004 — Official LuMay 7-bucket theme taxonomy
export type ComplaintTheme =
  | "claims"
  | "policy_and_coverage"
  | "renewal_and_pricing"
  | "customer_service"
  | "provider_and_network"
  | "digital_experience"
  | "financial";

// FR-002 — Detection types
export type DetectionType = "definite" | "possible" | "none";

// FR-003 — Sentiment values
export type SentimentLevel =
  | "very_positive"
  | "positive"
  | "neutral"
  | "negative"
  | "very_negative";
export type SentimentTrend = "improving" | "declining" | "stable" | "volatile";

// FR-006 — Escalation risk levels
export type EscalationRiskLevel = "low" | "medium" | "high" | "critical";

// FR-007 — SLA risk status
export type SLARiskStatus = "within_sla" | "at_risk" | "breached";

// FR-016 — Root cause categories
export type RootCauseCategory =
  | "process_failure"
  | "system_technical"
  | "staff_behaviour"
  | "policy_gap"
  | "provider_failure"
  | "customer_expectation";

// AI Override log entry (FR-014 / FR-020)
export type AIOverrideLogEntry = {
  timestamp: string;
  agent_id: string;
  reason: string;
  changes: Record<string, { from: unknown; to: unknown }>;
};

// FR-008 — Related complaint summary
export type RelatedComplaintSummary = {
  id: UUID;
  complaint_number: string | null;
  title: string;
  theme: string | null;
  severity: string;
  status: string;
  created_at: string;
  days_ago: number | null;
};

export type Complaint = Entity & {
  complaint_number: string | null;
  customer_id: UUID | null;
  interaction_id: UUID | null;
  title: string;
  description: string | null;
  category: string;
  subcategory: string | null;
  priority: string;
  severity: string;
  status: string;
  source: string;
  assigned_queue: string | null;
  assigned_agent_id: UUID | null;
  customer_name?: string | null;
  // FR-001 — channel (explicit) + product
  channel?: string | null;
  product?: string | null;
  // Legacy field kept for compatibility
  assigned_agent_name?: string | null;
  received_time?: string | null;
  is_high_risk?: boolean;
  is_overdue?: boolean;

  // FR-001 / FR-009 — Policy & Claim linkage
  policy_id?: string | null;
  policy_number?: string | null;
  claim_id?: string | null;
  claim_number?: string | null;
  interaction_ids?: string[] | null;

  // FR-010 — Customer requested outcome
  customer_requested_outcome?: string | null;

  // FR-020 — Regulatory flag
  regulatory_flag?: boolean | null;

  // FR-014 — Human validation
  human_validation?: "pending" | "accepted" | "corrected" | "rejected" | null;

  // FR-007 — SLA deadlines
  acknowledged_time?: string | null;
  acknowledgment_deadline?: string | null;
  resolution_deadline?: string | null;

  // FR-002 — Complaint Detection
  complaint_detected?: boolean | null;
  detection_type?: DetectionType | null;
  detection_confidence?: number | null;
  primary_complaint_statement?: string | null;

  // FR-003 — Enhanced Sentiment
  sentiment?: SentimentLevel | null;
  sentiment_start?: SentimentLevel | null;
  sentiment_end?: SentimentLevel | null;
  sentiment_trend?: SentimentTrend | null;
  sentiment_target?: string | null;
  sentiment_polarity?: number | null;
  sentiment_intensity?: number | null;
  sentiment_emotions?: Record<string, number> | null;

  // FR-004 — Theme (7-bucket taxonomy)
  theme?: ComplaintTheme | string | null;
  theme_secondary?: string[] | null;
  theme_keywords?: string[] | null;

  // FR-005 — Severity
  severity_score?: number | null;
  auto_escalation_triggers?: string[] | null;

  // FR-006 — Escalation Risk
  escalation_risk_score?: number | null;
  escalation_risk_level?: EscalationRiskLevel | null;
  escalation_triggers?: string[] | null;

  // FR-007 — SLA
  sla_risk?: SLARiskStatus | null;
  sla_status?: string | null;
  sla_breach_probability?: number | null;
  sla_hours_remaining?: number | null;

  // FR-008 — Repeat Complaint
  is_repeat?: boolean | null;
  repeat_window_days?: number | null;
  prior_complaint_count?: number | null;
  prior_complaint_ids?: string[] | null;
  duplicate_complaint?: boolean;

  // FR-016 — Root Cause
  root_cause?: string | null;
  root_cause_category?: RootCauseCategory | null;
  contributing_factors?: string[] | null;
  process_failure_point?: string | null;

  // FR-019 — Language
  detected_language?: "ar" | "en" | "mixed" | null;
  arabic_percentage?: number | null;

  // FR-020 — AI Explainability
  ai_summary?: string | null;
  ai_explanation?: Record<string, string> | null;
  recommendation?: string | null;
  routing_rule?: string | null;
  suggested_response_template?: string | null;

  // FR-014 — Human Override Log
  ai_override_log?: AIOverrideLogEntry[] | null;

  metadata?: Record<string, unknown> | null;
};

export type Interaction = Entity & {
  customer_id: UUID | null;
  channel: string;
  direction: string;
  subject: string | null;
  transcript: string | null;
  status: string;
  priority?: string;
  assigned_to?: string | null;
  assigned_agent_name?: string | null;
  customer_name?: string | null;
  interaction_number?: string | null;
  last_message?: string | null;
  time?: string | null;
  sentiment?: string | null;
  complaint_detected?: boolean;
  escalation_risk?: string | null;
  duplicate_warning?: boolean;
};

export type Workflow = Entity & {
  workflow_number: string | null;
  complaint_id: UUID;
  assigned_team: string | null;
  assigned_agent_id: UUID | null;
  workflow_status: string;
  workflow_stage: string;
  priority: string | null;
  sla_status: string;
  started_at: string | null;
  completed_at: string | null;
  customer_name?: string | null;
  customer_id?: UUID | null;
  channel?: string | null;
  theme?: string | null;
  severity?: string | null;
  assigned_agent_name?: string | null;
  role?: string | null;
  received_time?: string | null;
  case_number?: string | null;
  external_ref?: string | null;
  ai_summary?: string | null;
  sentiment?: string | null;
  escalation_recommendation?: string | null;
  root_cause?: string | null;
  sla_prediction?: string | null;
};

export type Notification = Entity & {
  notification_number: string | null;
  workflow_id: UUID | null;
  complaint_id: UUID | null;
  notification_type: string;
  notification_channel: string;
  recipient: string;
  subject: string;
  message: string;
  notification_status: string;
  priority: string;
  retry_count: number;
  sent_at: string | null;
  delivered_at: string | null;
};

export type DashboardKPIs = {
  total_customers: number;
  total_interactions: number;
  total_complaints: number;
  total_workflows: number;
  total_notifications: number;
  open_complaints: number;
  resolved_complaints: number;
  avg_resolution_time_hours: number;
  sla_compliance_rate: number;
  active_workflows: number;
  avg_sentiment_score: number;
  critical_complaints: number;
  // Phase 2 KPIs
  escalation_risk_high_count?: number;
  repeat_complaint_rate?: number;
  arabic_complaint_percentage?: number;
};

export type TrendPoint = {
  date: string;
  value: number;
};

export type CategoryDistribution = {
  category: string;
  count: number;
  percentage: number;
};

export type ComplaintTrends = {
  daily: TrendPoint[];
  weekly: TrendPoint[];
  monthly: TrendPoint[];
  category_distribution: CategoryDistribution[];
  sentiment_distribution: CategoryDistribution[];
  severity_distribution: CategoryDistribution[];
  priority_distribution: CategoryDistribution[];
  // Phase 2 distributions
  theme_distribution?: CategoryDistribution[];
  escalation_risk_distribution?: CategoryDistribution[];
  language_distribution?: CategoryDistribution[];
};

export type SLACompliance = {
  within_sla: number;
  at_risk: number;
  breached: number;
  compliance_rate: number;
  avg_breach_probability?: number;
};

export type DepartmentWorkload = {
  department: string;
  active_cases: number;
  avg_resolution_time_hours: number;
  backlog: number;
};

export type AnalyticsReport = {
  kpis: DashboardKPIs;
  trends: ComplaintTrends;
  sla: SLACompliance;
  departments: DepartmentWorkload[];
  report_generated_at: string;
};

export type SearchResults = {
  query: string;
  complaints: unknown[];
  customers: unknown[];
  interactions: unknown[];
  workflows: unknown[];
  knowledge: unknown[];
};

export type KnowledgeSearchResult = {
  query: string;
  results: unknown[];
  total: number;
  source: string;
};

export type ScenarioResult = {
  scenario: string;
  description: string;
  [key: string]: unknown;
};

export type AuditLog = Entity & {
  actor_id: UUID;
  action: string;
  resource_type: string;
  resource_id: string;
  details: Record<string, unknown>;
};

export type KnowledgeArticle = Entity & {
  title: string;
  content: string;
  article_type: string;
  status: string;
  category_id: UUID | null;
};

// Phase 2 — AI Analysis service types (FR-010 / FR-014)
export type AIOverrideRequest = {
  category?: string;
  theme?: string;
  severity?: string;
  priority?: string;
  sentiment?: string;
  root_cause?: string;
  root_cause_category?: string;
  regulatory_flag?: boolean;
  human_validation?: "pending" | "accepted" | "corrected" | "rejected";
  override_reason: string;
};

// FR-007 — Real-time SLA status (from /complaints/{id}/sla-status)
export type SLAStatusResult = {
  sla_status: "within_sla" | "at_risk" | "breached" | "unknown";
  time_remaining_hours: number | null;
  breach_probability: number;
  deadline_iso: string;
  recommended_action: string;
  pct_elapsed: number;
};

// FR-001 — Complaint ingestion response
export type ComplaintIngestResponse = {
  complaint_id: string;
  complaint_number: string | null;
  action: "created" | "updated";
  ai_analysis_queued: boolean;
  message: string;
};
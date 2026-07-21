// Mirrors backend/domains/conversation/schemas/conversation_schemas.py exactly
// (snake_case, wire-format) rather than a reinvented camelCase UI shape — the
// old WorkspaceInteraction/CustomerProfile dual-shape + manual mapper was a
// real source of drift/mock-fallback bugs (see interactions.service.ts).

export type ConversationStatus =
  | "new"
  | "active"
  | "waiting_for_customer"
  | "waiting_for_agent"
  | "ai_handling"
  | "human_handling"
  | "escalated"
  | "resolved"
  | "closed";

export type ConversationChannel = "web_chat" | "voice" | "whatsapp" | "email" | "complaint";

export type ConversationPriority = "low" | "medium" | "high" | "critical";

export type ConversationParticipantType = "customer" | "ai" | "employee" | "supervisor" | "system";

export type ConversationMessageType =
  | "text"
  | "transcript"
  | "attachment"
  | "event"
  | "system_notification";

export interface Conversation {
  id: string;
  created_at: string;
  updated_at: string;
  customer_id: string | null;
  policy_id: string | null;
  complaint_id: string | null;
  current_status: ConversationStatus;
  current_channel: ConversationChannel;
  assigned_employee_id: string | null;
  ai_handling: boolean;
  human_handling: boolean;
  priority: ConversationPriority;
}

export interface ConversationSummary {
  id: string;
  customer_id: string | null;
  complaint_id: string | null;
  current_status: ConversationStatus;
  current_channel: ConversationChannel;
  assigned_employee_id: string | null;
  priority: ConversationPriority;
  updated_at: string;
  customer_name: string | null;
  last_message_preview: string | null;
}

export interface ConversationStatusProjection {
  id: string;
  current_status: ConversationStatus;
  ai_handling: boolean;
  human_handling: boolean;
  assigned_employee_id: string | null;
}

export interface ConversationMessage {
  id: string;
  created_at: string;
  updated_at: string;
  conversation_id: string;
  sender_type: ConversationParticipantType;
  channel: ConversationChannel;
  message_type: ConversationMessageType;
  content: string;
  message_metadata: Record<string, unknown> | null;
}

export interface ConversationParticipant {
  id: string;
  created_at: string;
  updated_at: string;
  conversation_id: string;
  participant_type: ConversationParticipantType;
  participant_ref: string | null;
  role: string | null;
  joined_at: string;
  left_at: string | null;
}

export interface ConversationChannelLink {
  id: string;
  created_at: string;
  updated_at: string;
  conversation_id: string;
  channel: ConversationChannel;
  external_ref_type: string;
  external_ref_id: string;
  is_primary: boolean;
}

export interface ConversationEvent {
  id: string;
  created_at: string;
  updated_at: string;
  conversation_id: string;
  event_type: string;
  source_domain: string;
  payload: Record<string, unknown> | null;
}

export interface TimelineItem {
  type: "message" | "event";
  id: string;
  timestamp: string;
  sender_type: ConversationParticipantType | null;
  channel: ConversationChannel | null;
  message_type: ConversationMessageType | null;
  content: string | null;
  event_type: string | null;
  source_domain: string | null;
  payload: Record<string, unknown> | null;
}

export interface ConversationListFilters {
  customer_id?: string;
  status?: ConversationStatus;
  channel?: ConversationChannel;
  assigned_employee_id?: string;
  complaint_id?: string;
  priority?: ConversationPriority;
  date_from?: string;
  date_to?: string;
  search?: string;
  page?: number;
  page_size?: number;
}

export interface AddMessageBody {
  sender_type: ConversationParticipantType;
  channel: ConversationChannel;
  message_type?: ConversationMessageType;
  content: string;
  metadata?: Record<string, unknown>;
}

export interface AddEventBody {
  event_type: string;
  source_domain?: string;
  payload?: Record<string, unknown>;
}

/** ConversationEventBus payload shape (backend/domains/conversation/event_bus.py). */
export interface RealtimeEvent {
  id: string;
  conversation_id: string;
  event_type: string;
  data: Record<string, unknown>;
  timestamp: string;
}

// ── Phase 4 — ownership, notes, presence/typing ────────────────────────────

export interface AssignEmployeeBody {
  employee_id: string;
}

export interface SupervisorActionBody {
  supervisor_id: string;
}

export interface UpdateMessageBody {
  content: string;
}

export type PresenceStatus = "online" | "offline";

/** conversation_id -> participant_type -> participant_ref -> status */
export interface PresenceSnapshot {
  presence: Record<string, Record<string, PresenceStatus>>;
  typing: Record<string, boolean>;
  ai_active: boolean;
  conversation_live: boolean;
  voice_active: boolean;
}

export interface PresenceUpdateBody {
  participant_type: ConversationParticipantType;
  participant_ref: string;
  status: PresenceStatus;
}

export interface TypingUpdateBody {
  participant_type: ConversationParticipantType;
  is_typing: boolean;
}

/** SSE "presence" event payload — a delta, not the full snapshot. */
export interface PresenceDeltaPayload {
  participant_type: ConversationParticipantType;
  participant_ref: string;
  status: PresenceStatus;
}

/** SSE "typing" event payload — a delta, not the full snapshot. */
export interface TypingDeltaPayload {
  participant_type: ConversationParticipantType;
  is_typing: boolean;
}

// Ownership/handoff event_types the timeline and assignment-history surface.
export const OWNERSHIP_EVENT_TYPES = [
  "conversation_assigned",
  "conversation_transferred",
  "conversation_released",
  "conversation_accepted",
  "ai_handed_over",
  "employee_joined",
  "employee_left",
  "supervisor_joined",
  "supervisor_left",
] as const;

export const CONVERSATION_STATUS_TABS: { value: ConversationStatus | "all"; label: string }[] = [
  { value: "all", label: "Live" },
  { value: "active", label: "Active" },
  { value: "waiting_for_agent", label: "Waiting for Agent" },
  { value: "ai_handling", label: "AI Handling" },
  { value: "human_handling", label: "Human Handling" },
  { value: "escalated", label: "Escalated" },
  { value: "resolved", label: "Resolved" },
  { value: "closed", label: "Closed" },
];

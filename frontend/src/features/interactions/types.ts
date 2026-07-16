/**
 * Interaction Workspace Types — Sprint 15
 * Enterprise Customer Interaction Workspace
 */

export type ChannelId =
  | "all"
  | "voice"
  | "smart_call"
  | "whatsapp"
  | "web_chat"
  | "email"
  | "crm"
  | "manual"
  | "survey"
  | "claims";

export type MessageSender = "customer" | "agent" | "ai" | "system";

export type MessageType =
  | "text"
  | "voice_transcript"
  | "email"
  | "system_event"
  | "ai_note"
  | "attachment"
  | "voice_note";

export interface WorkspaceMessage {
  id: string;
  sender: MessageSender;
  type: MessageType;
  text: string;
  time: string;
  timestamp?: number;
  attachments?: { name: string; size: string; type: string }[];
  isRead?: boolean;
  agentName?: string;
  metadata?: Record<string, string | number | boolean>;
}

export type SentimentValue =
  | "very_positive"
  | "positive"
  | "neutral"
  | "negative"
  | "very_negative"
  | "extremely_negative";

export type RiskLevel = "low" | "medium" | "high" | "critical";

export type InteractionStatus =
  | "high_risk"
  | "new"
  | "in_progress"
  | "processed"
  | "closed"
  | "active"
  | "pending";

export interface AIAnalysis {
  complaintDetected: boolean;
  detectionConfidence: number; // 0-100
  sentiment: SentimentValue;
  emotion: string;
  theme: string;
  severity: "low" | "medium" | "high" | "critical";
  escalationRisk: number; // 0-100
  escalationRiskLevel: RiskLevel;
  regulatoryRisk: boolean;
  slaRisk: "resolved" | "on_track" | "at_risk" | "breached";
  repeatComplaint: boolean;
  priorComplaintCount: number;
  aiSummary: string;
  rootCause: string;
  suggestedResolution: string;
  recommendedDepartment: string;
  suggestedResponse: string;
  knowledgeArticles: { title: string; relevance: number }[];
}

export interface CustomerProfile {
  id: string;
  name: string;
  phone: string;
  email: string;
  city: string;
  segment: string;
  customerSince: string;
  policyNumber: string;
  product: string;
  claimStatus: string | null;
  riskLevel: RiskLevel;
  totalComplaints: number;
  openComplaints: number;
  isRepeatCustomer: boolean;
  lastComplaint: string | null;
  lifetimeValue: number;
}

export interface WorkspaceInteraction {
  id: string;
  channel: ChannelId;
  status: InteractionStatus;
  priority: "low" | "medium" | "high" | "critical";
  time: string;
  timestamp: number;
  unreadCount: number;
  subject: string;
  lastMessage: string;
  customer: CustomerProfile;
  messages: WorkspaceMessage[];
  ai: AIAnalysis;
  assignedAgent: string | null;
  // Voice specific
  callDuration?: string;
  isLiveCall?: boolean;
  // Email specific
  emailSubject?: string;
  emailFrom?: string;
  emailRecipients?: string[];
  emailAttachments?: { name: string; size: string }[];
  // Survey specific
  surveyScore?: number;
  surveyResponses?: { question: string; answer: string; rating?: number }[];
  // Claims specific
  claimNumber?: string;
  adjusterName?: string;
}

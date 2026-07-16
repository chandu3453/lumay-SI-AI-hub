import { api } from "@/services/api-client";
import type { WorkspaceInteraction, WorkspaceMessage } from "@/features/interactions/types";

export interface ChatMessage {
  role: string;
  content: string;
  timestamp: string;
}

export interface ChatResponsePayload {
  answer: string;
  messages: ChatMessage[];
  ai_analysis: any;
  context_used: boolean;
  auto_triaged: boolean;
  complaint_id: string | null;
  workflow_id: string | null;
  provider_used: string;
}

export interface VoiceTokenResponse {
  session_id: string;
  interaction_id: string;
  room_name: string;
  participant_token: string;
  livekit_url: string;
}

export const interactionsService = {
  async list(params?: any) {
    return api.get<{ data: any[] }>("/interactions", { params });
  },

  async startWebChat(customerRef?: string, complaintId?: string) {
    return api.post<{ data: any }>("/interactions/conversations/start", {
      customer_ref: customerRef,
      channel: "web_form",
      complaint_id: complaintId,
    });
  },

  async start(customerRef?: string, channel?: string, complaintId?: string) {
    // Translate web_chat UI to web_form backend value
    const targetChannel = channel === "web_chat" ? "web_form" : (channel || "whatsapp");
    return api.post<{ data: any }>("/interactions/conversations/start", {
      customer_ref: customerRef,
      channel: targetChannel,
      complaint_id: complaintId,
    });
  },

  async sendMessage(interactionId: string, message: string) {
    return api.post<{ data: ChatResponsePayload }>("/interactions/conversations/message", {
      interaction_id: interactionId,
      message,
    });
  },

  async startVoiceSession(customerRef?: string) {
    return api.post<{ data: VoiceTokenResponse }>("/voice/start", {
      customer_ref: customerRef,
    });
  },

  async endVoiceSession(sessionId: string) {
    return api.post("/voice/end", {
      session_id: sessionId,
    });
  },

  async getHistory() {
    return api.get<{ data: any[] }>("/interactions/conversations");
  },

  async getConversation(id: string) {
    return api.get<{ data: ChatMessage[] }>(`/interactions/conversations/${id}`);
  },

  async endSession(interactionId: string) {
    return api.post<{ data: any }>("/interactions/conversations/end", {
      interaction_id: interactionId,
      message: "End Session",
    });
  },
};

export function mapInteractionToWorkspace(dbInt: any, detailMessages: ChatMessage[] = []): WorkspaceInteraction {
  if (dbInt.customer && dbInt.ai && dbInt.messages) {
    return dbInt;
  }
  
  const mappedMessages: WorkspaceMessage[] = detailMessages.map((msg: any, idx: number) => ({
    id: `msg-${idx}-${Date.now()}`,
    sender: msg.role === "user" ? "customer" : "agent",
    type: "text",
    text: msg.content,
    time: msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: true }) : "",
    timestamp: msg.timestamp ? new Date(msg.timestamp).getTime() : Date.now(),
  }));

  // Default fallback profile for Fatima Al Lawati
  const defaultCustomer = {
    id: dbInt.customer_ref || "cust-102",
    name: "Fatima Al Lawati",
    phone: "+968 9912 3456",
    email: "fatima.lawati@email.com",
    city: "Muscat",
    segment: "VIP",
    customerSince: "2022-04-12",
    policyNumber: "POL-99281-22",
    product: "Motor Comprehensive",
    claimStatus: "Under Review",
    riskLevel: "medium" as const,
    totalComplaints: 3,
    openComplaints: 1,
    isRepeatCustomer: true,
    lastComplaint: "2024-05-10",
    lifetimeValue: 4800,
  };

  return {
    id: dbInt.id,
    channel: dbInt.channel === "web_form" ? "web_chat" : dbInt.channel,
    status: dbInt.status === "completed" ? "processed" : "new",
    priority: "medium",
    time: dbInt.created_at ? new Date(dbInt.created_at).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }) : "",
    timestamp: dbInt.created_at ? new Date(dbInt.created_at).getTime() : Date.now(),
    unreadCount: 0,
    subject: dbInt.subject || "AI Chat Session",
    lastMessage: mappedMessages.length > 0 ? mappedMessages[mappedMessages.length - 1].text : "",
    customer: defaultCustomer,
    messages: mappedMessages,
    ai: {
      complaintDetected: false,
      detectionConfidence: 0,
      sentiment: "neutral",
      emotion: "neutral",
      theme: "General Enquiry",
      severity: "low",
      escalationRisk: 10,
      escalationRiskLevel: "low",
      regulatoryRisk: false,
      slaRisk: "on_track",
      repeatComplaint: false,
      priorComplaintCount: 0,
      aiSummary: "Customer initiated a standard inquiry session.",
      rootCause: "Inquiry",
      suggestedResolution: "Provide standard response.",
      recommendedDepartment: "Customer Service",
      suggestedResponse: "Thank you for contacting LuMay Insurance. How can I help you today?",
      knowledgeArticles: [],
    },
    assignedAgent: "Ahmed Al Badi",
  };
}

export function updateInteractionAI(interaction: WorkspaceInteraction, payload: ChatResponsePayload): WorkspaceInteraction {
  if (!payload.ai_analysis) return interaction;

  const analysis = payload.ai_analysis;
  const isComplaint = analysis.detection?.is_complaint ?? false;
  const confidence = Math.round((analysis.detection?.confidence ?? 0) * 100);
  const rawSentiment = analysis.sentiment?.sentiment ?? "neutral";
  const rawSeverity = analysis.severity?.severity ?? "low";
  
  // Map severity string to RiskLevel
  let mappedSeverity: "low" | "medium" | "high" | "critical" = "low";
  if (rawSeverity === "major" || rawSeverity === "high") mappedSeverity = "high";
  if (rawSeverity === "critical") mappedSeverity = "critical";
  if (rawSeverity === "moderate" || rawSeverity === "medium") mappedSeverity = "medium";

  const mappedMessages: WorkspaceMessage[] = payload.messages.map((msg: any, idx: number) => ({
    id: `msg-${idx}-${Date.now()}`,
    sender: msg.role === "user" ? "customer" : "agent",
    type: "text",
    text: msg.content,
    time: msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: true }) : "",
    timestamp: msg.timestamp ? new Date(msg.timestamp).getTime() : Date.now(),
  }));

  return {
    ...interaction,
    messages: mappedMessages,
    lastMessage: mappedMessages.length > 0 ? mappedMessages[mappedMessages.length - 1].text : interaction.lastMessage,
    status: isComplaint ? "high_risk" : "in_progress",
    ai: {
      complaintDetected: isComplaint,
      detectionConfidence: confidence,
      sentiment: rawSentiment,
      emotion: Object.keys(analysis.sentiment?.emotions || {}).join(", ") || "neutral",
      theme: analysis.themes?.primary_theme || "General Enquiry",
      severity: mappedSeverity,
      escalationRisk: Math.round((analysis.escalation?.escalation_risk_score ?? 0) * 10) / 10,
      escalationRiskLevel: (analysis.escalation?.escalation_risk_score ?? 0) >= 75 ? "critical" : (analysis.escalation?.escalation_risk_score ?? 0) >= 50 ? "high" : "low",
      regulatoryRisk: analysis.regulatory_flag ?? false,
      slaRisk: analysis.priority?.sla_risk || "on_track",
      repeatComplaint: analysis.is_repeat ?? false,
      priorComplaintCount: analysis.prior_complaint_count ?? 0,
      aiSummary: analysis.summary?.summary || "AI Summary pending...",
      rootCause: analysis.root_cause?.root_cause || "Inquiry",
      suggestedResolution: analysis.resolution?.recommended_action || "Provide standard response.",
      recommendedDepartment: analysis.resolution?.department || "Customer Service",
      suggestedResponse: analysis.resolution?.suggested_response_template || "",
      knowledgeArticles: (analysis.knowledge_articles || []).map((art: any) => ({
        title: art.title,
        relevance: Math.round(art.relevance * 100),
      })),
    },
  };
}

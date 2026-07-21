import { api } from "@/services/api-client";
import { API_BASE_URL, API_PREFIX } from "@/lib/constants";
import type {
  AddEventBody,
  AddMessageBody,
  AssignEmployeeBody,
  Conversation,
  ConversationChannelLink,
  ConversationEvent,
  ConversationListFilters,
  ConversationMessage,
  ConversationParticipant,
  ConversationPriority,
  ConversationStatus,
  ConversationStatusProjection,
  ConversationSummary,
  PresenceSnapshot,
  PresenceUpdateBody,
  SupervisorActionBody,
  TimelineItem,
  TypingUpdateBody,
  UpdateMessageBody,
} from "@/features/conversations/types";

interface SuccessResponse<T> {
  success: boolean;
  data: T;
}

interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const conversationsService = {
  async list(filters?: ConversationListFilters) {
    return api.get<PaginatedResponse<ConversationSummary>>("/conversations", { params: filters });
  },

  async getById(id: string) {
    return api.get<SuccessResponse<Conversation>>(`/conversations/${id}`);
  },

  /** Reverse lookup — lets a channel UI that only knows its own
   * interaction/session id (not the conversation id) reach conversation-level
   * endpoints, e.g. the customer webchat page resolving its conversation_id
   * to post typing pings. */
  async getByExternalRef(refType: string, refId: string) {
    return api.get<SuccessResponse<Conversation>>("/conversations/by-external-ref", {
      params: { ref_type: refType, ref_id: refId },
    });
  },

  async getStatus(id: string) {
    return api.get<SuccessResponse<ConversationStatusProjection>>(`/conversations/${id}/status`);
  },

  async getTimeline(id: string, page = 1, pageSize = 200) {
    return api.get<PaginatedResponse<TimelineItem>>(`/conversations/${id}/timeline`, {
      params: { page, page_size: pageSize },
    });
  },

  async getMessages(id: string, page = 1, pageSize = 50) {
    return api.get<PaginatedResponse<ConversationMessage>>(`/conversations/${id}/messages`, {
      params: { page, page_size: pageSize },
    });
  },

  async getParticipants(id: string) {
    return api.get<SuccessResponse<ConversationParticipant[]>>(`/conversations/${id}/participants`);
  },

  async getEvents(id: string, page = 1, pageSize = 50) {
    return api.get<PaginatedResponse<ConversationEvent>>(`/conversations/${id}/events`, {
      params: { page, page_size: pageSize },
    });
  },

  async getChannels(id: string) {
    return api.get<SuccessResponse<ConversationChannelLink[]>>(`/conversations/${id}/channels`);
  },

  async assign(id: string, employeeId: string) {
    return api.post<SuccessResponse<Conversation>>(`/conversations/${id}/assign`, {
      employee_id: employeeId,
    });
  },

  async updateStatus(id: string, status: ConversationStatus) {
    return api.patch<SuccessResponse<Conversation>>(`/conversations/${id}/status`, { status });
  },

  async close(id: string) {
    return api.post<SuccessResponse<Conversation>>(`/conversations/${id}/close`);
  },

  async setPriority(id: string, priority: ConversationPriority) {
    return api.patch<SuccessResponse<Conversation>>(`/conversations/${id}/priority`, { priority });
  },

  async addMessage(id: string, body: AddMessageBody) {
    return api.post<SuccessResponse<ConversationMessage>>(`/conversations/${id}/messages`, body);
  },

  async addEvent(id: string, body: AddEventBody) {
    return api.post<SuccessResponse<ConversationEvent>>(`/conversations/${id}/events`, body);
  },

  // ── Phase 4 — ownership, notes, presence/typing ─────────────────────────

  async takeOver(id: string, body: AssignEmployeeBody) {
    return api.post<SuccessResponse<Conversation>>(`/conversations/${id}/take-over`, body);
  },

  async release(id: string) {
    return api.post<SuccessResponse<Conversation>>(`/conversations/${id}/release`);
  },

  async transfer(id: string, body: AssignEmployeeBody) {
    return api.post<SuccessResponse<Conversation>>(`/conversations/${id}/transfer`, body);
  },

  async accept(id: string, body: AssignEmployeeBody) {
    return api.post<SuccessResponse<Conversation>>(`/conversations/${id}/accept`, body);
  },

  async supervisorJoin(id: string, body: SupervisorActionBody) {
    return api.post<SuccessResponse<ConversationParticipant>>(
      `/conversations/${id}/supervisor/join`,
      body,
    );
  },

  async supervisorLeave(id: string, body: SupervisorActionBody) {
    return api.post<SuccessResponse<Conversation>>(`/conversations/${id}/supervisor/leave`, body);
  },

  async getAssignmentHistory(id: string) {
    return api.get<SuccessResponse<ConversationEvent[]>>(`/conversations/${id}/assignment-history`);
  },

  async updateMessage(id: string, messageId: string, body: UpdateMessageBody) {
    return api.patch<SuccessResponse<ConversationMessage>>(
      `/conversations/${id}/messages/${messageId}`,
      body,
    );
  },

  async deleteMessage(id: string, messageId: string) {
    return api.delete<SuccessResponse<ConversationMessage>>(
      `/conversations/${id}/messages/${messageId}`,
    );
  },

  async getPresence(id: string) {
    return api.get<SuccessResponse<PresenceSnapshot>>(`/conversations/${id}/presence`);
  },

  async postPresence(id: string, body: PresenceUpdateBody) {
    return api.post<SuccessResponse<PresenceSnapshot>>(`/conversations/${id}/presence`, body);
  },

  async postTyping(id: string, body: TypingUpdateBody) {
    return api.post<SuccessResponse<PresenceSnapshot>>(`/conversations/${id}/typing`, body);
  },

  /** Absolute URLs (not relative) — EventSource needs the real backend origin;
   * this app has no dev-server rewrite proxying /api/v1 to the backend. */
  streamUrl(): string {
    return `${API_BASE_URL}${API_PREFIX}/conversations/stream`;
  },

  conversationStreamUrl(id: string): string {
    return `${API_BASE_URL}${API_PREFIX}/conversations/${id}/stream`;
  },
};

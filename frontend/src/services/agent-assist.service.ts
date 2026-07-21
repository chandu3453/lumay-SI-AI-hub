import { api } from "@/services/api-client";
import type {
  AgentAssistHistoryItem,
  AgentAssistInsightOrEmpty,
} from "@/features/agent-assist/types";

interface SuccessResponse<T> {
  success: boolean;
  data: T;
}

export const agentAssistService = {
  async getLatest(conversationId: string) {
    return api.get<SuccessResponse<AgentAssistInsightOrEmpty>>(
      `/conversations/${conversationId}/agent-assist`,
    );
  },

  async getHistory(conversationId: string, limit = 20) {
    return api.get<SuccessResponse<AgentAssistHistoryItem[]>>(
      `/conversations/${conversationId}/agent-assist/history`,
      { params: { limit } },
    );
  },

  async regenerate(conversationId: string) {
    return api.post<SuccessResponse<AgentAssistInsightOrEmpty>>(
      `/conversations/${conversationId}/agent-assist/regenerate`,
    );
  },
};

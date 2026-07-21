"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { agentAssistService } from "@/services/agent-assist.service";

export const agentAssistKeys = {
  all: ["agent-assist"] as const,
  insight: (id: string) => ["agent-assist", "insight", id] as const,
  history: (id: string) => ["agent-assist", "history", id] as const,
};

export function useAgentAssistInsight(conversationId: string | null) {
  return useQuery({
    queryKey: agentAssistKeys.insight(conversationId ?? ""),
    queryFn: async () => {
      if (!conversationId) return null;
      const res = await agentAssistService.getLatest(conversationId);
      return res.data.data;
    },
    enabled: !!conversationId,
    retry: 1,
  });
}

export function useAgentAssistHistory(conversationId: string | null, limit = 20) {
  return useQuery({
    queryKey: agentAssistKeys.history(conversationId ?? ""),
    queryFn: async () => {
      if (!conversationId) return [];
      const res = await agentAssistService.getHistory(conversationId, limit);
      return res.data.data;
    },
    enabled: !!conversationId,
    retry: 1,
  });
}

export function useRegenerateAgentAssist() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (conversationId: string) => agentAssistService.regenerate(conversationId),
    onSuccess: (_res, conversationId) => {
      qc.invalidateQueries({ queryKey: agentAssistKeys.insight(conversationId) });
      qc.invalidateQueries({ queryKey: agentAssistKeys.history(conversationId) });
    },
  });
}

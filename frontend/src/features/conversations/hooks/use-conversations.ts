"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { conversationsService } from "@/services/conversations.service";
import type {
  AddMessageBody,
  AssignEmployeeBody,
  ConversationListFilters,
  ConversationPriority,
  ConversationStatus,
  SupervisorActionBody,
  UpdateMessageBody,
} from "@/features/conversations/types";

export const conversationKeys = {
  all: ["conversations"] as const,
  list: (filters?: ConversationListFilters) => ["conversations", "list", filters] as const,
  detail: (id: string) => ["conversations", "detail", id] as const,
  status: (id: string) => ["conversations", "status", id] as const,
  timeline: (id: string) => ["conversations", "timeline", id] as const,
  participants: (id: string) => ["conversations", "participants", id] as const,
  channels: (id: string) => ["conversations", "channels", id] as const,
  assignmentHistory: (id: string) => ["conversations", "assignment-history", id] as const,
};

export function useConversationList(filters?: ConversationListFilters) {
  return useQuery({
    queryKey: conversationKeys.list(filters),
    queryFn: async () => {
      const res = await conversationsService.list(filters);
      return { items: res.data.data, total: res.data.total };
    },
    // Fallback poll in case an SSE connection silently drops — belt and
    // suspenders on top of the live stream, not the primary sync mechanism.
    refetchInterval: 30_000,
    retry: 1,
  });
}

export function useConversation(id: string | null) {
  return useQuery({
    queryKey: conversationKeys.detail(id ?? ""),
    queryFn: async () => {
      if (!id) return null;
      const res = await conversationsService.getById(id);
      return res.data.data;
    },
    enabled: !!id,
    retry: 1,
  });
}

export function useConversationTimeline(id: string | null) {
  return useQuery({
    queryKey: conversationKeys.timeline(id ?? ""),
    queryFn: async () => {
      if (!id) return { items: [], total: 0 };
      const res = await conversationsService.getTimeline(id);
      return { items: res.data.data, total: res.data.total };
    },
    enabled: !!id,
    retry: 1,
  });
}

export function useConversationParticipants(id: string | null) {
  return useQuery({
    queryKey: conversationKeys.participants(id ?? ""),
    queryFn: async () => {
      if (!id) return [];
      const res = await conversationsService.getParticipants(id);
      return res.data.data;
    },
    enabled: !!id,
    retry: 1,
  });
}

export function useConversationChannels(id: string | null) {
  return useQuery({
    queryKey: conversationKeys.channels(id ?? ""),
    queryFn: async () => {
      if (!id) return [];
      const res = await conversationsService.getChannels(id);
      return res.data.data;
    },
    enabled: !!id,
    retry: 1,
  });
}

export function useAssignConversation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, employeeId }: { id: string; employeeId: string }) =>
      conversationsService.assign(id, employeeId),
    onSuccess: (_res, { id }) => {
      qc.invalidateQueries({ queryKey: conversationKeys.detail(id) });
      qc.invalidateQueries({ queryKey: conversationKeys.participants(id) });
      qc.invalidateQueries({ queryKey: conversationKeys.all });
    },
  });
}

export function useUpdateConversationStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: ConversationStatus }) =>
      conversationsService.updateStatus(id, status),
    onSuccess: (_res, { id }) => {
      qc.invalidateQueries({ queryKey: conversationKeys.detail(id) });
      qc.invalidateQueries({ queryKey: conversationKeys.all });
    },
  });
}

export function useCloseConversation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => conversationsService.close(id),
    onSuccess: (_res, id) => {
      qc.invalidateQueries({ queryKey: conversationKeys.detail(id) });
      qc.invalidateQueries({ queryKey: conversationKeys.all });
    },
  });
}

export function useSetConversationPriority() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, priority }: { id: string; priority: ConversationPriority }) =>
      conversationsService.setPriority(id, priority),
    onSuccess: (_res, { id }) => {
      qc.invalidateQueries({ queryKey: conversationKeys.detail(id) });
      qc.invalidateQueries({ queryKey: conversationKeys.all });
    },
  });
}

export function useAddConversationMessage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: AddMessageBody }) =>
      conversationsService.addMessage(id, body),
    onSuccess: (_res, { id }) => {
      qc.invalidateQueries({ queryKey: conversationKeys.timeline(id) });
      qc.invalidateQueries({ queryKey: conversationKeys.all });
    },
  });
}

// ── Phase 4 — ownership, notes, presence/typing ──────────────────────────

function invalidateOwnership(qc: ReturnType<typeof useQueryClient>, id: string) {
  qc.invalidateQueries({ queryKey: conversationKeys.detail(id) });
  qc.invalidateQueries({ queryKey: conversationKeys.timeline(id) });
  qc.invalidateQueries({ queryKey: conversationKeys.participants(id) });
  qc.invalidateQueries({ queryKey: conversationKeys.assignmentHistory(id) });
  qc.invalidateQueries({ queryKey: conversationKeys.all });
}

export function useAssignmentHistory(id: string | null) {
  return useQuery({
    queryKey: conversationKeys.assignmentHistory(id ?? ""),
    queryFn: async () => {
      if (!id) return [];
      const res = await conversationsService.getAssignmentHistory(id);
      return res.data.data;
    },
    enabled: !!id,
    retry: 1,
  });
}

export function useTakeOverConversation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: AssignEmployeeBody }) =>
      conversationsService.takeOver(id, body),
    onSuccess: (_res, { id }) => invalidateOwnership(qc, id),
  });
}

export function useReleaseConversation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => conversationsService.release(id),
    onSuccess: (_res, id) => invalidateOwnership(qc, id),
  });
}

export function useTransferConversation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: AssignEmployeeBody }) =>
      conversationsService.transfer(id, body),
    onSuccess: (_res, { id }) => invalidateOwnership(qc, id),
  });
}

export function useAcceptConversation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: AssignEmployeeBody }) =>
      conversationsService.accept(id, body),
    onSuccess: (_res, { id }) => invalidateOwnership(qc, id),
  });
}

export function useSupervisorJoin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: SupervisorActionBody }) =>
      conversationsService.supervisorJoin(id, body),
    onSuccess: (_res, { id }) => invalidateOwnership(qc, id),
  });
}

export function useSupervisorLeave() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: SupervisorActionBody }) =>
      conversationsService.supervisorLeave(id, body),
    onSuccess: (_res, { id }) => invalidateOwnership(qc, id),
  });
}

export function useUpdateConversationMessage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      messageId,
      body,
    }: {
      id: string;
      messageId: string;
      body: UpdateMessageBody;
    }) => conversationsService.updateMessage(id, messageId, body),
    onSuccess: (_res, { id }) => {
      qc.invalidateQueries({ queryKey: conversationKeys.timeline(id) });
    },
  });
}

export function useDeleteConversationMessage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, messageId }: { id: string; messageId: string }) =>
      conversationsService.deleteMessage(id, messageId),
    onSuccess: (_res, { id }) => {
      qc.invalidateQueries({ queryKey: conversationKeys.timeline(id) });
    },
  });
}

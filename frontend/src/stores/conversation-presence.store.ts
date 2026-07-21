import { create } from "zustand";

import type {
  PresenceDeltaPayload,
  PresenceSnapshot,
  TypingDeltaPayload,
} from "@/features/conversations/types";

// High-frequency, non-cacheable push state (presence pings, typing on every
// keystroke) — deliberately kept out of react-query so it never triggers a
// query invalidation/refetch storm. Written to by the SSE hook, read by UI.

const EMPTY_SNAPSHOT: PresenceSnapshot = {
  presence: {},
  typing: {},
  ai_active: false,
  conversation_live: false,
  voice_active: false,
};

type ConversationPresenceState = {
  snapshots: Record<string, PresenceSnapshot>;
};

type ConversationPresenceActions = {
  setSnapshot: (conversationId: string, snapshot: PresenceSnapshot) => void;
  applyPresenceDelta: (conversationId: string, delta: PresenceDeltaPayload) => void;
  applyTypingDelta: (conversationId: string, delta: TypingDeltaPayload) => void;
  clearConversation: (conversationId: string) => void;
};

export const useConversationPresenceStore = create<
  ConversationPresenceState & ConversationPresenceActions
>()((set) => ({
  snapshots: {},

  setSnapshot: (conversationId, snapshot) =>
    set((s) => ({ snapshots: { ...s.snapshots, [conversationId]: snapshot } })),

  applyPresenceDelta: (conversationId, delta) =>
    set((s) => {
      const current = s.snapshots[conversationId] ?? EMPTY_SNAPSHOT;
      return {
        snapshots: {
          ...s.snapshots,
          [conversationId]: {
            ...current,
            presence: {
              ...current.presence,
              [delta.participant_type]: {
                ...current.presence[delta.participant_type],
                [delta.participant_ref]: delta.status,
              },
            },
          },
        },
      };
    }),

  applyTypingDelta: (conversationId, delta) =>
    set((s) => {
      const current = s.snapshots[conversationId] ?? EMPTY_SNAPSHOT;
      return {
        snapshots: {
          ...s.snapshots,
          [conversationId]: {
            ...current,
            typing: { ...current.typing, [delta.participant_type]: delta.is_typing },
          },
        },
      };
    }),

  clearConversation: (conversationId) =>
    set((s) => {
      const { [conversationId]: _removed, ...rest } = s.snapshots;
      return { snapshots: rest };
    }),
}));

export function useConversationPresence(conversationId: string | null): PresenceSnapshot {
  return useConversationPresenceStore((s) =>
    conversationId ? (s.snapshots[conversationId] ?? EMPTY_SNAPSHOT) : EMPTY_SNAPSHOT,
  );
}

import { create } from "zustand";

import type {
  ConversationChannel,
  ConversationPriority,
  ConversationStatus,
} from "@/features/conversations/types";

export type ConversationFilters = {
  status?: ConversationStatus;
  channel?: ConversationChannel;
  priority?: ConversationPriority;
  assignedEmployeeId?: string;
  complaintId?: string;
  dateFrom?: string;
  dateTo?: string;
};

type ConversationUiState = {
  selectedConversationId: string | null;
  rightPanelOpen: boolean;
  search: string;
  filters: ConversationFilters;
  // One-shot signal: Agent Assist "Accept"/"Edit" writes a suggested reply
  // here, TimelineComposeBar consumes it into its local input and clears
  // it — these two live in sibling panels, so a prop chain through the
  // shell would be more indirection than reusing the store both already
  // read from (selectedConversationId).
  draftText: string;
};

type ConversationUiActions = {
  selectConversation: (id: string | null) => void;
  toggleRightPanel: () => void;
  setSearch: (search: string) => void;
  setFilters: (filters: ConversationFilters) => void;
  clearFilters: () => void;
  setDraftText: (text: string) => void;
  clearDraftText: () => void;
};

export const useConversationUiStore = create<ConversationUiState & ConversationUiActions>()(
  (set) => ({
    selectedConversationId: null,
    rightPanelOpen: true,
    search: "",
    filters: {},
    draftText: "",
    selectConversation: (id) => set({ selectedConversationId: id }),
    toggleRightPanel: () => set((s) => ({ rightPanelOpen: !s.rightPanelOpen })),
    setSearch: (search) => set({ search }),
    setFilters: (filters) => set({ filters }),
    clearFilters: () => set({ filters: {} }),
    setDraftText: (draftText) => set({ draftText }),
    clearDraftText: () => set({ draftText: "" }),
  }),
);

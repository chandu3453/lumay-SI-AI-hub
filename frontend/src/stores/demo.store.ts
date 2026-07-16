import { create } from "zustand";

export type DemoEvent = {
  id: string;
  event_type: string;
  data: Record<string, unknown>;
  channel: string;
  customer_name: string | null;
  timestamp: string;
};

type DemoState = {
  enabled: boolean;
  events: DemoEvent[];
  autoSimulate: boolean;
  simulateInterval: number;
};

type DemoActions = {
  setEnabled: (v: boolean) => void;
  addEvent: (e: DemoEvent) => void;
  clearEvents: () => void;
  setAutoSimulate: (v: boolean) => void;
  setSimulateInterval: (ms: number) => void;
};

const initialState: DemoState = {
  enabled: false,
  events: [],
  autoSimulate: false,
  simulateInterval: 15_000,
};

export const useDemoStore = create<DemoState & DemoActions>()((set) => ({
  ...initialState,
  setEnabled: (enabled) => set({ enabled }),
  addEvent: (event) =>
    set((s) => ({
      events: [...s.events.slice(-199), event],
    })),
  clearEvents: () => set({ events: [] }),
  setAutoSimulate: (autoSimulate) => set({ autoSimulate }),
  setSimulateInterval: (simulateInterval) => set({ simulateInterval }),
}));

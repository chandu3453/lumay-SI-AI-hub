import { create } from "zustand";

type InsuranceStore = {
  selectedLine: string;
  setSelectedLine: (line: string) => void;
};

export const useInsuranceStore = create<InsuranceStore>((set) => ({
  selectedLine: "All",
  setSelectedLine: (line) => set({ selectedLine: line }),
}));

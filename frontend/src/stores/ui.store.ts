import { create } from "zustand";

type SidebarState = "expanded" | "collapsed";

type UiState = {
  sidebar: SidebarState;
  isMobileMenuOpen: boolean;
};

type UiActions = {
  toggleSidebar: () => void;
  setSidebar: (state: SidebarState) => void;
  setMobileMenuOpen: (open: boolean) => void;
};

export const useUiStore = create<UiState & UiActions>()((set) => ({
  sidebar: "expanded",
  isMobileMenuOpen: false,
  toggleSidebar: () =>
    set((state) => ({
      sidebar: state.sidebar === "expanded" ? "collapsed" : "expanded",
    })),
  setSidebar: (sidebar) => set({ sidebar }),
  setMobileMenuOpen: (isMobileMenuOpen) => set({ isMobileMenuOpen }),
}));

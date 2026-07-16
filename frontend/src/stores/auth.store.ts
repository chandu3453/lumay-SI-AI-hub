import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { User } from "@/types/domain";

type AuthState = {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
};

type AuthActions = {
  setUser: (user: User | null) => void;
  setTokens: (access: string, refresh: string) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
};

const initialState: AuthState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: true,
};

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set) => ({
      ...initialState,
      isLoading: false,
      setUser: (user) =>
        set({ user, isAuthenticated: user !== null }),
      setTokens: (access, refresh) =>
        set({ token: access, refreshToken: refresh, isAuthenticated: true }),
      setLoading: (isLoading) => set({ isLoading }),
      logout: () => set(initialState),
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
);

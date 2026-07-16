"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";

import { setApiToken } from "@/lib/http";
import { authService } from "@/services/auth.service";
import { useAuthStore } from "@/stores/auth.store";
import { ROUTES } from "@/lib/constants";

export function useAuth() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, setUser, setTokens, setLoading, logout } =
    useAuthStore();

  const login = useCallback(
    async (email: string, password: string) => {
      setLoading(true);
      try {
        const { data } = await authService.login({ email, password });
        setTokens(data.data.access_token, data.data.refresh_token);
        setApiToken(data.data.access_token);
        const { data: userData } = await authService.me();
        setUser(userData.data);
        router.push(ROUTES.DASHBOARD);
      } finally {
        setLoading(false);
      }
    },
    [router, setTokens, setUser, setLoading],
  );

  const logoutUser = useCallback(() => {
    authService.logout().catch(() => {});
    setApiToken(null);
    logout();
    localStorage.removeItem("demo-role");
    router.push("/");
  }, [router, logout]);

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout: logoutUser,
  };
}

import { api } from "@/services/api-client";
import type { ApiResponse } from "@/types/api";
import type { User } from "@/types/domain";

type LoginRequest = {
  email: string;
  password: string;
};

type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};

export const authService = {
  async login(data: LoginRequest) {
    return api.post<ApiResponse<TokenPair>>("/auth/login", data);
  },

  async logout() {
    return api.post("/auth/logout");
  },

  async refreshToken(refreshToken: string) {
    return api.post<ApiResponse<TokenPair>>("/auth/refresh", {
      refresh_token: refreshToken,
    });
  },

  async me() {
    return api.get<ApiResponse<User>>("/auth/me");
  },
};

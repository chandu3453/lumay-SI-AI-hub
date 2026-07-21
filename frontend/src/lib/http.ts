import axios, { type AxiosError, type AxiosInstance, type CreateAxiosDefaults } from "axios";

import { API_BASE_URL, API_PREFIX } from "@/lib/constants";

let TOKEN: string | null = null;

export function setApiToken(token: string | null) {
  TOKEN = token;
}

export function getApiToken() {
  return TOKEN;
}

const defaults: CreateAxiosDefaults = {
  baseURL: `${API_BASE_URL}${API_PREFIX}`,
  timeout: 30_000,
  headers: { "Content-Type": "application/json" },
};

export const api: AxiosInstance = axios.create(defaults);

api.interceptors.request.use((config) => {
  let activeToken = TOKEN;
  if (!activeToken) {
    try {
      const storage = typeof window !== "undefined" ? window.localStorage.getItem("auth-storage") : null;
      if (storage) {
        const parsed = JSON.parse(storage);
        if (parsed?.state?.token) {
          activeToken = parsed.state.token;
        }
      }
    } catch (e) {
      console.warn("Failed to parse auth token from storage", e);
    }
  }

  const isCustomerRoute = typeof window !== "undefined" && window.location.pathname.startsWith("/customer");
  if (activeToken && !isCustomerRoute) {
    config.headers.Authorization = `Bearer ${activeToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      setApiToken(null);
      try {
        if (typeof window !== "undefined") {
          const storage = window.localStorage.getItem("auth-storage");
          if (storage) {
            const parsed = JSON.parse(storage);
            if (parsed?.state) {
              parsed.state.token = null;
              parsed.state.isAuthenticated = false;
              window.localStorage.setItem("auth-storage", JSON.stringify(parsed));
            }
          }
        }
      } catch (e) {
        console.warn("Failed to clear auth token from localStorage", e);
      }
    }
    return Promise.reject(error);
  },
);

import { api, setApiToken } from "@/lib/http";
import type { ApiError } from "@/types/api";

export { api, setApiToken };

export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === "object" &&
    error !== null &&
    "error_code" in error &&
    "message" in error
  );
}

export function extractApiError(error: unknown): ApiError {
  if (isApiError(error)) return error;
  if (error && typeof error === "object" && "response" in error) {
    const axiosError = error as { response?: { data?: unknown } };
    if (axiosError.response?.data && isApiError(axiosError.response.data)) {
      return axiosError.response.data as ApiError;
    }
  }
  return {
    success: false,
    error_code: "UNKNOWN_ERROR",
    message: "An unexpected error occurred.",
  };
}

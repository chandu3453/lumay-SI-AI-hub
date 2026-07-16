export type ApiResponse<T> = {
  success: boolean;
  data: T;
};

export type ApiListResponse<T> = {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  };
};

export type ApiError = {
  success: boolean;
  error_code: string;
  message: string;
  context?: Record<string, unknown>;
};

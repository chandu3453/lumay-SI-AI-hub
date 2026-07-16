export type UUID = string;

export type Timestamps = {
  created_at: string;
  updated_at: string;
};

export type Entity = Timestamps & {
  id: UUID;
};

export type PaginationParams = {
  page: number;
  page_size: number;
};

export type PaginationMeta = {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
};

export type PaginatedResponse<T> = {
  success: boolean;
  data: T[];
  pagination: PaginationMeta;
};

export type SuccessResponse<T> = {
  success: boolean;
  data: T;
};

export type ErrorResponse = {
  success: boolean;
  error_code: string;
  message: string;
  context?: Record<string, unknown>;
};

export type SortDirection = "asc" | "desc";

export type SortParams = {
  sort_by: string;
  sort_dir: SortDirection;
};

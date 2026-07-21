import { api } from "@/services/api-client";
import type { User } from "@/types/domain";

interface SuccessResponse<T> {
  success: boolean;
  data: T;
}

export const usersService = {
  /** Batch-resolves employee_id UUIDs to names — see GET /users?ids=. */
  async listByIds(ids: string[]) {
    if (ids.length === 0) {
      return { data: { success: true, data: [] as User[] } };
    }
    return api.get<SuccessResponse<User[]>>("/users", { params: { ids: ids.join(",") } });
  },
};

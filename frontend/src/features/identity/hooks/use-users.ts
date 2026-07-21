"use client";

import { useQuery } from "@tanstack/react-query";

import { usersService } from "@/services/users.service";

export const userKeys = {
  byIds: (ids: string[]) => ["users", "by-ids", [...ids].sort()] as const,
};

/** Resolves employee_id UUIDs to display names — used anywhere a raw
 * `assigned_employee_id` needs a human-readable label (Customer 360,
 * Employee Analytics). Returns a map for O(1) lookup by id. */
export function useEmployeeNames(ids: (string | null | undefined)[]) {
  const uniqueIds = Array.from(new Set(ids.filter((id): id is string => !!id))).sort();
  const query = useQuery({
    queryKey: userKeys.byIds(uniqueIds),
    queryFn: async () => {
      const res = await usersService.listByIds(uniqueIds);
      return res.data.data;
    },
    enabled: uniqueIds.length > 0,
    retry: 1,
    staleTime: 5 * 60_000,
  });

  const nameById = new Map<string, string>();
  for (const user of query.data ?? []) {
    nameById.set(user.id, user.full_name);
  }
  return { nameById, isLoading: query.isLoading };
}

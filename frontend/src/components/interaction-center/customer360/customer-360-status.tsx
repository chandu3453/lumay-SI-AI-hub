import { Card, CardContent } from "@/components/ui/card";
import { PriorityBadge, StatusBadge } from "@/components/interaction-center/shared/conversation-badges";
import { useEmployeeNames } from "@/features/identity/hooks/use-users";
import type { Conversation } from "@/features/conversations/types";

/** Real fields only — current status, priority, and assigned employee
 * (Sprint 29 — name-resolved via GET /users?ids=, falls back to the raw
 * UUID prefix if the id doesn't resolve to a real user). */
export function Customer360Status({ conversation }: { conversation: Conversation }) {
  const { nameById } = useEmployeeNames([conversation.assigned_employee_id]);
  const employeeId = conversation.assigned_employee_id;
  const employeeLabel = employeeId ? (nameById.get(employeeId) ?? employeeId.slice(0, 8)) : null;

  return (
    <Card>
      <CardContent className="space-y-2 p-3">
        <p className="text-xs font-semibold">Conversation</p>
        <div className="flex flex-wrap items-center gap-1.5">
          <StatusBadge status={conversation.current_status} />
          <PriorityBadge priority={conversation.priority} />
        </div>
        <p className="text-[11px] text-muted-foreground">
          {employeeLabel ? `Assigned to ${employeeLabel}` : "Unassigned"}
        </p>
      </CardContent>
    </Card>
  );
}

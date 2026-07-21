"use client";

import { useState } from "react";
import { Eye, EyeOff, LogOut, RotateCcw, UserCheck, UserPlus, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth.store";
import {
  useAcceptConversation,
  useCloseConversation,
  useReleaseConversation,
  useSetConversationPriority,
  useSupervisorJoin,
  useSupervisorLeave,
  useTakeOverConversation,
  useTransferConversation,
  useUpdateConversationStatus,
} from "@/features/conversations/hooks/use-conversations";
import {
  CONVERSATION_STATUS_TABS,
  type Conversation,
  type ConversationParticipant,
} from "@/features/conversations/types";

/** Take Over / Release / Transfer / Accept / Supervisor Monitor / Change
 * Status / Close / Priority / Reopen — take-over and release drive the
 * AI<->Human handoff (Phase 4); an "Assign / Transfer" input still exists
 * for handing to a specific employee, now routed to the dedicated
 * take-over (unassigned) or transfer (reassign) endpoint instead of the
 * bare /assign call. */
export function ConversationToolbar({
  conversation,
  participants = [],
}: {
  conversation: Conversation;
  participants?: ConversationParticipant[];
}) {
  const currentUser = useAuthStore((s) => s.user);
  const takeOver = useTakeOverConversation();
  const release = useReleaseConversation();
  const transfer = useTransferConversation();
  const accept = useAcceptConversation();
  const supervisorJoin = useSupervisorJoin();
  const supervisorLeave = useSupervisorLeave();
  const updateStatus = useUpdateConversationStatus();
  const close = useCloseConversation();
  const setPriority = useSetConversationPriority();

  const [assigneeInput, setAssigneeInput] = useState("");
  const [showAssignInput, setShowAssignInput] = useState(false);

  const isClosed = conversation.current_status === "closed";
  const isResolved = conversation.current_status === "resolved";
  const isMonitoring = currentUser
    ? participants.some(
        (p) =>
          p.participant_type === "supervisor" && p.participant_ref === currentUser.id && !p.left_at,
      )
    : false;

  function handleAssign(employeeId: string) {
    if (!employeeId) return;
    if (conversation.assigned_employee_id) {
      transfer.mutate({ id: conversation.id, body: { employee_id: employeeId } });
    } else {
      takeOver.mutate({ id: conversation.id, body: { employee_id: employeeId } });
    }
    setShowAssignInput(false);
    setAssigneeInput("");
  }

  return (
    <div className="flex flex-wrap items-center gap-1.5 border-b border-border bg-muted/30 px-3 py-2">
      {currentUser ? (
        conversation.human_handling && conversation.assigned_employee_id === currentUser.id ? (
          <Button
            size="sm"
            variant="outline"
            className="h-7 gap-1 text-xs"
            onClick={() => release.mutate(conversation.id)}
            disabled={release.isPending}
          >
            <LogOut className="h-3 w-3" /> Release to AI
          </Button>
        ) : (
          <Button
            size="sm"
            variant="outline"
            className="h-7 gap-1 text-xs"
            onClick={() => takeOver.mutate({ id: conversation.id, body: { employee_id: currentUser.id } })}
            disabled={takeOver.isPending}
          >
            <UserPlus className="h-3 w-3" /> Take Over
          </Button>
        )
      ) : null}

      {currentUser && conversation.assigned_employee_id === currentUser.id ? (
        <Button
          size="sm"
          variant="outline"
          className="h-7 gap-1 text-xs"
          onClick={() => accept.mutate({ id: conversation.id, body: { employee_id: currentUser.id } })}
          disabled={accept.isPending}
        >
          <UserCheck className="h-3 w-3" /> Accept
        </Button>
      ) : null}

      {currentUser ? (
        <Button
          size="sm"
          variant="outline"
          className="h-7 gap-1 text-xs"
          onClick={() =>
            isMonitoring
              ? supervisorLeave.mutate({ id: conversation.id, body: { supervisor_id: currentUser.id } })
              : supervisorJoin.mutate({ id: conversation.id, body: { supervisor_id: currentUser.id } })
          }
          disabled={supervisorJoin.isPending || supervisorLeave.isPending}
        >
          {isMonitoring ? (
            <>
              <EyeOff className="h-3 w-3" /> Stop Monitoring
            </>
          ) : (
            <>
              <Eye className="h-3 w-3" /> Monitor
            </>
          )}
        </Button>
      ) : null}

      <div className="relative">
        <Button
          size="sm"
          variant="outline"
          className="h-7 text-xs"
          onClick={() => setShowAssignInput((s) => !s)}
        >
          Assign / Transfer
        </Button>
        {showAssignInput ? (
          <div className="absolute left-0 top-full z-20 mt-1 flex w-56 items-center gap-1 rounded-md border border-border bg-popover p-1.5 shadow-lg">
            <input
              autoFocus
              value={assigneeInput}
              onChange={(e) => setAssigneeInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAssign(assigneeInput.trim())}
              placeholder="employee-uuid"
              className="h-7 flex-1 rounded border border-border bg-background px-1.5 text-xs"
            />
            <Button size="sm" className="h-7 px-2 text-xs" onClick={() => handleAssign(assigneeInput.trim())}>
              Go
            </Button>
            <button type="button" onClick={() => setShowAssignInput(false)} className="text-muted-foreground">
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        ) : null}
      </div>

      <select
        value={conversation.current_status}
        onChange={(e) => updateStatus.mutate({ id: conversation.id, status: e.target.value as Conversation["current_status"] })}
        className="h-7 rounded-md border border-border bg-background px-1.5 text-xs"
        disabled={updateStatus.isPending}
      >
        {CONVERSATION_STATUS_TABS.filter((t) => t.value !== "all").map((t) => (
          <option key={t.value} value={t.value}>
            {t.label}
          </option>
        ))}
      </select>

      <select
        value={conversation.priority}
        onChange={(e) => setPriority.mutate({ id: conversation.id, priority: e.target.value as Conversation["priority"] })}
        className="h-7 rounded-md border border-border bg-background px-1.5 text-xs"
        disabled={setPriority.isPending}
      >
        {(["low", "medium", "high", "critical"] as const).map((p) => (
          <option key={p} value={p}>
            Priority: {p}
          </option>
        ))}
      </select>

      {isClosed || isResolved ? (
        <Button
          size="sm"
          variant="outline"
          className="h-7 gap-1 text-xs"
          onClick={() => updateStatus.mutate({ id: conversation.id, status: "active" })}
          disabled={updateStatus.isPending}
        >
          <RotateCcw className="h-3 w-3" /> Reopen
        </Button>
      ) : (
        <Button
          size="sm"
          variant="outline"
          className="h-7 text-xs"
          onClick={() => close.mutate(conversation.id)}
          disabled={close.isPending}
        >
          Close
        </Button>
      )}
    </div>
  );
}

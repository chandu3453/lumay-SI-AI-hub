"use client";

import { Bot, Eye, User } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import type { Conversation, ConversationParticipant } from "@/features/conversations/types";

/** Current Owner + active Supervisor badges — derived from existing fields
 * (ai_handling/human_handling/assigned_employee_id) and the participant list
 * (a participant with participant_type=supervisor and no left_at is actively
 * monitoring). No new columns needed. */
export function ConversationOwnerBadge({
  conversation,
  participants = [],
}: {
  conversation: Conversation;
  participants?: ConversationParticipant[];
}) {
  const activeSupervisors = participants.filter(
    (p) => p.participant_type === "supervisor" && !p.left_at,
  );

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {conversation.human_handling && conversation.assigned_employee_id ? (
        <Badge variant="success" className="gap-1">
          <User className="h-3 w-3" />
          Employee {conversation.assigned_employee_id.slice(0, 8)}
        </Badge>
      ) : conversation.ai_handling ? (
        <Badge variant="default" className="gap-1">
          <Bot className="h-3 w-3" />
          AI Handling
        </Badge>
      ) : (
        <Badge variant="neutral" className="gap-1">
          Unassigned
        </Badge>
      )}

      {activeSupervisors.map((s) => (
        <Badge key={s.id} variant="outline" className="gap-1 text-muted-foreground">
          <Eye className="h-3 w-3" />
          Supervisor {s.participant_ref?.slice(0, 8) ?? s.id.slice(0, 8)}
        </Badge>
      ))}
    </div>
  );
}

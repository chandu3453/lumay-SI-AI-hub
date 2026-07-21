"use client";

import { cn } from "@/lib/cn";
import { useConversationPresence } from "@/stores/conversation-presence.store";

const PARTICIPANT_LABEL: Record<string, string> = {
  customer: "Customer",
  employee: "Employee",
  ai: "AI",
  supervisor: "Supervisor",
};

function isAnyOnline(byRef: Record<string, string> | undefined): boolean {
  return Object.values(byRef ?? {}).some((status) => status === "online");
}

/** Online dots for customer/employee + "X is typing…" text — reads straight
 * from the ephemeral Zustand presence store (never react-query), so a
 * keystroke never triggers a network refetch. */
export function PresenceIndicators({ conversationId }: { conversationId: string | null }) {
  const snapshot = useConversationPresence(conversationId);

  const typingParticipants = Object.entries(snapshot.typing)
    .filter(([, isTyping]) => isTyping)
    .map(([participantType]) => PARTICIPANT_LABEL[participantType] ?? participantType);

  const onlineDots = (["customer", "employee"] as const).map((type) => ({
    type,
    online: isAnyOnline(snapshot.presence[type]),
  }));

  return (
    <div className="flex items-center gap-3 text-[11px] text-muted-foreground">
      {onlineDots.map(({ type, online }) => (
        <span key={type} className="inline-flex items-center gap-1">
          <span
            className={cn(
              "inline-block h-1.5 w-1.5 rounded-full",
              online ? "bg-success" : "bg-muted-foreground/30",
            )}
          />
          {PARTICIPANT_LABEL[type]} {online ? "online" : "offline"}
        </span>
      ))}
      {snapshot.voice_active ? (
        <span className="inline-flex items-center gap-1">
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-destructive" />
          Voice session active
        </span>
      ) : null}
      {typingParticipants.length > 0 ? (
        <span className="italic">
          {typingParticipants.join(", ")} {typingParticipants.length === 1 ? "is" : "are"} typing…
        </span>
      ) : null}
    </div>
  );
}

"use client";

import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { agentAssistKeys } from "@/features/agent-assist/hooks/use-agent-assist";
import { conversationKeys } from "@/features/conversations/hooks/use-conversations";
import { conversationsService } from "@/services/conversations.service";
import { useConversationPresenceStore } from "@/stores/conversation-presence.store";
import type {
  PresenceDeltaPayload,
  RealtimeEvent,
  TimelineItem,
  TypingDeltaPayload,
} from "@/features/conversations/types";

// Ownership/handoff event_types (Phase 4) — any of these means the current
// owner, participant list, or assignment history may have changed.
const OWNERSHIP_SSE_EVENT_TYPES = [
  "conversation_assigned",
  "conversation_transferred",
  "conversation_released",
  "conversation_accepted",
  "ai_handed_over",
  "employee_joined",
  "employee_left",
  "supervisor_joined",
  "supervisor_left",
];

/** Modeled on use-demo-sse.ts's exact connect/reconnect/cleanup shape —
 * ConversationEventBus's real-time backend counterpart. Subscribes to every
 * conversation update (queue-wide) and invalidates the list query, so the
 * left panel updates without a manual refresh. */
export function useConversationsQueueSSE() {
  const qc = useQueryClient();
  const esRef = useRef<EventSource | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    function connect() {
      esRef.current?.close();
      const es = new EventSource(conversationsService.streamUrl());
      esRef.current = es;

      const invalidate = () => qc.invalidateQueries({ queryKey: conversationKeys.all });
      for (const type of [
        "message",
        "event",
        "conversation.created",
        "status_changed",
        "assigned",
        "priority_changed",
        ...OWNERSHIP_SSE_EVENT_TYPES,
      ]) {
        es.addEventListener(type, invalidate);
      }

      es.onerror = () => {
        es.close();
        reconnectRef.current = setTimeout(connect, 3000);
      };
    }

    connect();
    return () => {
      clearTimeout(reconnectRef.current);
      esRef.current?.close();
    };
  }, [qc]);
}

/** Subscribes to one conversation's stream — only mounted while that
 * conversation is open in the center panel. Appends new messages/events
 * directly into the timeline query cache for a smooth live-append feel
 * instead of a full refetch flicker on every event. */
export function useConversationTimelineSSE(conversationId: string | null) {
  const qc = useQueryClient();
  const esRef = useRef<EventSource | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const setSnapshot = useConversationPresenceStore((s) => s.setSnapshot);
  const applyPresenceDelta = useConversationPresenceStore((s) => s.applyPresenceDelta);
  const applyTypingDelta = useConversationPresenceStore((s) => s.applyTypingDelta);
  const clearConversation = useConversationPresenceStore((s) => s.clearConversation);

  useEffect(() => {
    if (!conversationId) return;
    const id = conversationId;

    // Prime the presence store before the SSE connection catches up.
    conversationsService
      .getPresence(id)
      .then((res) => setSnapshot(id, res.data.data))
      .catch(() => {
        /* presence is best-effort — SSE deltas will still arrive */
      });

    function appendTimelineItem(item: TimelineItem) {
      qc.setQueryData(
        conversationKeys.timeline(id),
        (old: { items: TimelineItem[]; total: number } | undefined) => {
          if (!old) return old;
          if (old.items.some((existing) => existing.id === item.id)) return old;
          return { items: [...old.items, item], total: old.total + 1 };
        },
      );
    }

    function connect() {
      esRef.current?.close();
      const es = new EventSource(conversationsService.conversationStreamUrl(id));
      esRef.current = es;

      es.addEventListener("message", (msg) => {
        try {
          const evt = JSON.parse(msg.data) as RealtimeEvent;
          const d = evt.data as Record<string, string | null>;
          appendTimelineItem({
            type: "message",
            id: (d.id as string) ?? evt.id,
            timestamp: evt.timestamp,
            sender_type: (d.sender_type as TimelineItem["sender_type"]) ?? null,
            channel: (d.channel as TimelineItem["channel"]) ?? null,
            message_type: (d.message_type as TimelineItem["message_type"]) ?? null,
            content: d.content ?? null,
            event_type: null,
            source_domain: null,
            payload: null,
          });
        } catch {
          /* ignore parse errors */
        }
      });

      es.addEventListener("event", (msg) => {
        try {
          const evt = JSON.parse(msg.data) as RealtimeEvent;
          const d = evt.data as Record<string, unknown>;
          appendTimelineItem({
            type: "event",
            id: (d.id as string) ?? evt.id,
            timestamp: evt.timestamp,
            sender_type: null,
            channel: null,
            message_type: null,
            content: null,
            event_type: (d.event_type as string) ?? null,
            source_domain: (d.source_domain as string) ?? null,
            payload: (d.payload as Record<string, unknown>) ?? null,
          });
        } catch {
          /* ignore parse errors */
        }
      });

      const invalidateDetail = () => qc.invalidateQueries({ queryKey: conversationKeys.detail(id) });
      es.addEventListener("status_changed", invalidateDetail);
      es.addEventListener("priority_changed", invalidateDetail);
      es.addEventListener("assigned", () => {
        invalidateDetail();
        qc.invalidateQueries({ queryKey: conversationKeys.participants(id) });
      });

      // Ownership/handoff — refetch owner, participant list, and history
      // rather than trying to hand-patch every shape of these payloads.
      const invalidateOwnership = () => {
        invalidateDetail();
        qc.invalidateQueries({ queryKey: conversationKeys.participants(id) });
        qc.invalidateQueries({ queryKey: conversationKeys.assignmentHistory(id) });
      };
      for (const type of OWNERSHIP_SSE_EVENT_TYPES) {
        es.addEventListener(type, invalidateOwnership);
      }

      // Internal note edit/delete — the message row changed in place, not a
      // new item, so a full timeline refetch is simpler than patching.
      const invalidateTimeline = () => qc.invalidateQueries({ queryKey: conversationKeys.timeline(id) });
      es.addEventListener("internal_note_updated", invalidateTimeline);
      es.addEventListener("internal_note_deleted", invalidateTimeline);

      // Agent Assist (Phase 5) — the SSE payload is just a signal, not the
      // content itself (matches every other event here); refetch via REST.
      es.addEventListener("agent_assist_updated", () => {
        qc.invalidateQueries({ queryKey: agentAssistKeys.insight(id) });
        qc.invalidateQueries({ queryKey: agentAssistKeys.history(id) });
      });

      // Presence/typing — ephemeral, goes straight to the Zustand store,
      // never through react-query (would refetch on every keystroke).
      es.addEventListener("presence", (msg) => {
        try {
          const evt = JSON.parse(msg.data) as RealtimeEvent;
          applyPresenceDelta(id, evt.data as unknown as PresenceDeltaPayload);
        } catch {
          /* ignore parse errors */
        }
      });
      es.addEventListener("typing", (msg) => {
        try {
          const evt = JSON.parse(msg.data) as RealtimeEvent;
          applyTypingDelta(id, evt.data as unknown as TypingDeltaPayload);
        } catch {
          /* ignore parse errors */
        }
      });

      es.onerror = () => {
        es.close();
        reconnectRef.current = setTimeout(connect, 3000);
      };
    }

    connect();
    return () => {
      clearTimeout(reconnectRef.current);
      esRef.current?.close();
      clearConversation(id);
    };
  }, [conversationId, qc, setSnapshot, applyPresenceDelta, applyTypingDelta, clearConversation]);
}

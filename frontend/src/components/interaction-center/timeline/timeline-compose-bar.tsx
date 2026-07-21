"use client";

import { useEffect, useRef, useState } from "react";
import { Lock, MessageSquare, Send } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";
import { conversationsService } from "@/services/conversations.service";
import { useAddConversationMessage } from "@/features/conversations/hooks/use-conversations";
import { useConversationUiStore } from "@/stores/conversation-ui.store";
import type { ConversationChannel } from "@/features/conversations/types";

const TYPING_DEBOUNCE_MS = 500;

/** Reply (customer-visible) vs Internal Note tabs — both go through the same
 * POST /conversations/{id}/messages endpoint; an internal note is just
 * `metadata: { internal: true }`, no new backend endpoint needed. */
export function TimelineComposeBar({
  conversationId,
  channel,
  disabled,
}: {
  conversationId: string;
  channel: ConversationChannel;
  disabled?: boolean;
}) {
  const [tab, setTab] = useState<"reply" | "note">("reply");
  const [text, setText] = useState("");
  const addMessage = useAddConversationMessage();
  const typingTimeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const isTypingRef = useRef(false);
  const draftText = useConversationUiStore((s) => s.draftText);
  const clearDraftText = useConversationUiStore((s) => s.clearDraftText);

  // Agent Assist "Accept"/"Edit" writes here (see conversation-ui.store) —
  // consume it into the reply tab and clear the one-shot signal. Never
  // auto-sent: the employee still has to review and hit Send.
  useEffect(() => {
    if (!draftText) return;
    setTab("reply");
    setText(draftText);
    clearDraftText();
  }, [draftText, clearDraftText]);

  function stopTyping() {
    clearTimeout(typingTimeoutRef.current);
    if (isTypingRef.current) {
      isTypingRef.current = false;
      void conversationsService.postTyping(conversationId, {
        participant_type: "employee",
        is_typing: false,
      });
    }
  }

  function handleTextChange(value: string) {
    setText(value);
    if (!isTypingRef.current) {
      isTypingRef.current = true;
      void conversationsService.postTyping(conversationId, {
        participant_type: "employee",
        is_typing: true,
      });
    }
    clearTimeout(typingTimeoutRef.current);
    typingTimeoutRef.current = setTimeout(stopTyping, TYPING_DEBOUNCE_MS);
  }

  useEffect(() => () => stopTyping(), []); // eslint-disable-line react-hooks/exhaustive-deps

  function handleSend() {
    const content = text.trim();
    if (!content) return;
    stopTyping();
    addMessage.mutate({
      id: conversationId,
      body: {
        sender_type: "employee",
        channel,
        content,
        metadata: tab === "note" ? { internal: true } : undefined,
      },
    });
    setText("");
  }

  return (
    <div className="border-t border-border p-3">
      <div className="mb-2 flex gap-1">
        <button
          type="button"
          onClick={() => setTab("reply")}
          className={cn(
            "flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium",
            tab === "reply" ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent",
          )}
        >
          <MessageSquare className="h-3.5 w-3.5" /> Reply
        </button>
        <button
          type="button"
          onClick={() => setTab("note")}
          className={cn(
            "flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium",
            tab === "note" ? "bg-warning text-warning-foreground" : "text-muted-foreground hover:bg-accent",
          )}
        >
          <Lock className="h-3.5 w-3.5" /> Internal Note
        </button>
      </div>
      <div className="flex items-end gap-2">
        <textarea
          value={text}
          onChange={(e) => handleTextChange(e.target.value)}
          onBlur={stopTyping}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          disabled={disabled}
          rows={2}
          placeholder={tab === "reply" ? "Type a reply to the customer…" : "Add an internal note (not visible to the customer)…"}
          className="flex-1 resize-none rounded-md border border-border bg-background p-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50"
        />
        <Button size="sm" onClick={handleSend} disabled={disabled || !text.trim() || addMessage.isPending}>
          <Send className="h-3.5 w-3.5" />
        </Button>
      </div>
    </div>
  );
}

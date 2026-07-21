"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, Lock, Pencil, Trash2, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";
import { formatDate } from "@/lib/formatters";
import {
  useDeleteConversationMessage,
  useUpdateConversationMessage,
} from "@/features/conversations/hooks/use-conversations";
import type { TimelineItem } from "@/features/conversations/types";

/** Collapsible panel filtering the existing timeline to internal notes
 * (payload.internal===true) — no separate fetch, same data the main
 * timeline already loaded. Inline edit/delete via the Phase 4
 * PATCH/DELETE /messages/{message_id} endpoints (internal-only, 422 on any
 * customer-visible message — enforced server-side, not re-checked here). */
export function InternalNotesPanel({
  conversationId,
  items,
}: {
  conversationId: string;
  items: TimelineItem[];
}) {
  const [expanded, setExpanded] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const updateMessage = useUpdateConversationMessage();
  const deleteMessage = useDeleteConversationMessage();

  const notes = items.filter((item) => {
    if (item.type !== "message") return false;
    const meta = item.payload as { internal?: boolean; deleted?: boolean } | null;
    return Boolean(meta?.internal) && !meta?.deleted;
  });

  function startEdit(item: TimelineItem) {
    setEditingId(item.id);
    setDraft(item.content ?? "");
  }

  function saveEdit(messageId: string) {
    const content = draft.trim();
    if (!content) return;
    updateMessage.mutate(
      { id: conversationId, messageId, body: { content } },
      { onSuccess: () => setEditingId(null) },
    );
  }

  function remove(messageId: string) {
    deleteMessage.mutate({ id: conversationId, messageId });
  }

  return (
    <div className="border-b border-border">
      <button
        type="button"
        onClick={() => setExpanded((e) => !e)}
        className="flex w-full items-center gap-1.5 px-3 py-2 text-xs font-medium text-muted-foreground hover:bg-accent"
      >
        {expanded ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
        <Lock className="h-3.5 w-3.5" />
        Internal Notes ({notes.length})
      </button>

      {expanded ? (
        <div className="max-h-56 space-y-2 overflow-y-auto px-3 pb-3">
          {notes.length === 0 ? (
            <p className="text-xs text-muted-foreground">No internal notes yet.</p>
          ) : (
            notes.map((note) => (
              <div
                key={note.id}
                className="rounded-md border border-warning/30 bg-warning/10 p-2 text-xs"
              >
                {editingId === note.id ? (
                  <div className="space-y-1.5">
                    <textarea
                      autoFocus
                      value={draft}
                      onChange={(e) => setDraft(e.target.value)}
                      rows={2}
                      className="w-full resize-none rounded border border-border bg-background p-1.5 text-xs outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    />
                    <div className="flex justify-end gap-1">
                      <Button
                        size="sm"
                        variant="outline"
                        className="h-6 px-2 text-[11px]"
                        onClick={() => setEditingId(null)}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                      <Button
                        size="sm"
                        className="h-6 px-2 text-[11px]"
                        disabled={!draft.trim() || updateMessage.isPending}
                        onClick={() => saveEdit(note.id)}
                      >
                        Save
                      </Button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="mb-1 flex items-center justify-between gap-2">
                      <span className="text-[10px] text-muted-foreground">
                        {formatDate(note.timestamp, "p")}
                      </span>
                      <div className={cn("flex gap-1")}>
                        <button
                          type="button"
                          onClick={() => startEdit(note)}
                          className="text-muted-foreground hover:text-foreground"
                          aria-label="Edit note"
                        >
                          <Pencil className="h-3 w-3" />
                        </button>
                        <button
                          type="button"
                          onClick={() => remove(note.id)}
                          disabled={deleteMessage.isPending}
                          className="text-muted-foreground hover:text-destructive"
                          aria-label="Delete note"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </div>
                    </div>
                    <p>{note.content}</p>
                  </>
                )}
              </div>
            ))
          )}
        </div>
      ) : null}
    </div>
  );
}

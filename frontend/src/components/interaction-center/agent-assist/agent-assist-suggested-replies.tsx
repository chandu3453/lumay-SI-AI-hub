"use client";

import { useState } from "react";
import { Pencil, ThumbsUp, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { SuggestedReply } from "@/features/agent-assist/types";

const TYPE_LABEL: Record<string, string> = {
  greeting: "Greeting",
  clarification: "Clarification",
  policy_explanation: "Policy Explanation",
  complaint_acknowledgment: "Complaint Acknowledgment",
  claim_guidance: "Claim Guidance",
  closing: "Closing",
};

/** Draft replies — Accept/Edit both populate the existing compose bar (never
 * auto-sent, per spec); Ignore just dismisses the suggestion locally. */
export function AgentAssistSuggestedReplies({
  replies,
  onUseDraft,
}: {
  replies: SuggestedReply[];
  onUseDraft: (text: string) => void;
}) {
  const [ignoredIndexes, setIgnoredIndexes] = useState<Set<number>>(new Set());
  const visible = replies.filter((_, i) => !ignoredIndexes.has(i));

  if (visible.length === 0) {
    return (
      <div className="space-y-1">
        <h3 className="text-xs font-semibold text-muted-foreground">Suggested Reply</h3>
        <p className="text-xs text-muted-foreground">No suggestions right now.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <h3 className="text-xs font-semibold text-muted-foreground">Suggested Replies</h3>
      {replies.map((reply, index) =>
        ignoredIndexes.has(index) ? null : (
          <div key={index} className="rounded-md border border-border bg-muted/30 p-2 text-xs">
            <div className="mb-1 text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
              {TYPE_LABEL[reply.type] ?? reply.type}
            </div>
            <p className="mb-1.5">{reply.content}</p>
            <div className="flex justify-end gap-1">
              <Button
                size="sm"
                variant="outline"
                className="h-6 gap-1 px-2 text-[11px]"
                onClick={() => onUseDraft(reply.content)}
              >
                <Pencil className="h-3 w-3" /> Edit
              </Button>
              <Button
                size="sm"
                className="h-6 gap-1 px-2 text-[11px]"
                onClick={() => onUseDraft(reply.content)}
              >
                <ThumbsUp className="h-3 w-3" /> Accept
              </Button>
              <button
                type="button"
                onClick={() => setIgnoredIndexes((prev) => new Set(prev).add(index))}
                className="text-muted-foreground hover:text-destructive"
                aria-label="Ignore suggestion"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        ),
      )}
    </div>
  );
}

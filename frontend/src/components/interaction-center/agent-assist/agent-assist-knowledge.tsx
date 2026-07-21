"use client";

import { BookOpen } from "lucide-react";

import type { KnowledgeArticleSuggestion } from "@/features/agent-assist/types";

const SOURCE_LABEL: Record<string, string> = {
  policy: "Policy",
  faq: "FAQ",
  product: "Product",
};

/** Grounded in the existing RAG pipeline (KnowledgeService.search) — these
 * are the same snippets the suggested replies were told to draw from, never
 * generic LLM knowledge. */
export function AgentAssistKnowledge({ articles }: { articles: KnowledgeArticleSuggestion[] }) {
  return (
    <div className="space-y-1.5">
      <h3 className="text-xs font-semibold text-muted-foreground">Knowledge Articles</h3>
      {articles.length === 0 ? (
        <p className="text-xs text-muted-foreground">No matching articles found.</p>
      ) : (
        articles.map((article, index) => (
          <div key={index} className="flex items-start gap-1.5 rounded-md border border-border p-2 text-xs">
            <BookOpen className="mt-0.5 h-3 w-3 shrink-0 text-muted-foreground" />
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-medium">{article.title}</span>
                <span className="rounded bg-muted px-1 py-0.5 text-[10px] text-muted-foreground">
                  {SOURCE_LABEL[article.source] ?? article.source}
                </span>
              </div>
              <p className="mt-0.5 text-muted-foreground">{article.snippet}</p>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

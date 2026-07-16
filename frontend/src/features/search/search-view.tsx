"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useSearch } from "@/features/dashboard/use-dashboard";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, FileText, Users, MessageSquare, GitBranch, BookOpen, X, Clock, LayoutGrid } from "lucide-react";

const STORAGE_KEY = "recent-searches";

function loadRecentSearches(): string[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function saveRecentSearches(searches: string[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(searches));
}

const sourceIcons: Record<string, React.ReactNode> = {
  complaint: <FileText className="h-4 w-4 text-blue-500" />,
  customer: <Users className="h-4 w-4 text-emerald-500" />,
  interaction: <MessageSquare className="h-4 w-4 text-purple-500" />,
  workflow: <GitBranch className="h-4 w-4 text-orange-500" />,
  knowledge: <BookOpen className="h-4 w-4 text-pink-500" />,
};

const sourceBadge: Record<string, string> = {
  complaint: "default", customer: "success", interaction: "neutral", workflow: "warning", knowledge: "neutral",
};

function highlightMatch(text: string, query: string): React.ReactNode {
  if (!query.trim()) return text;
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const parts = text.split(new RegExp(`(${escaped})`, "gi"));
  return parts.map((part, i) =>
    part.toLowerCase() === query.toLowerCase()
      ? <mark key={i} className="bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-200 rounded px-0.5">{part}</mark>
      : part
  );
}

const quickFilters = [
  { label: "Complaints", value: "complaint" },
  { label: "Customers", value: "customer" },
  { label: "Workflows", value: "workflow" },
  { label: "Knowledge", value: "knowledge" },
];

export function SearchView() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [recentSearches, setRecentSearches] = useState<string[]>(loadRecentSearches);
  const { data: results, isLoading } = useSearch(query);

  const handleSearch = useCallback((term: string) => {
    const trimmed = term.trim();
    if (!trimmed) return;
    const updated = [trimmed, ...recentSearches.filter((s) => s !== trimmed)].slice(0, 5);
    setRecentSearches(updated);
    saveRecentSearches(updated);
    setQuery(trimmed);
  }, [recentSearches]);

  const clearSearch = useCallback(() => {
    setQuery("");
  }, []);

  const allResults = [
    ...(results?.complaints?.map((r: any) => ({ ...r, sourceType: "complaint" })) ?? []),
    ...(results?.customers?.map((r: any) => ({ ...r, sourceType: "customer" })) ?? []),
    ...(results?.interactions?.map((r: any) => ({ ...r, sourceType: "interaction" })) ?? []),
    ...(results?.workflows?.map((r: any) => ({ ...r, sourceType: "workflow" })) ?? []),
    ...(results?.knowledge?.map((r: any) => ({ ...r, sourceType: "knowledge" })) ?? []),
  ];

  return (
    <div className="space-y-4 animate-fade-in">
      <div className="relative max-w-2xl">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
        <Input
          placeholder="Search across complaints, customers, workflows, knowledge..."
          className="pl-12 h-12 text-base rounded-xl pr-12"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSearch(query);
          }}
          autoFocus
        />
        {query && (
          <button
            onClick={clearSearch}
            className="absolute right-12 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground/50 hover:text-muted-foreground transition-colors"
          >
            <X className="h-full w-full" />
          </button>
        )}
        <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[10px] text-muted-foreground/30 select-none pointer-events-none hidden sm:inline">
          Ctrl+K
        </span>
      </div>

      {!query && recentSearches.length > 0 && (
        <div className="max-w-2xl">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Recent Searches</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {recentSearches.map((term) => (
              <button
                key={term}
                onClick={() => handleSearch(term)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-muted text-muted-foreground hover:bg-muted/80 transition-colors"
              >
                <Clock className="h-3 w-3" />
                {term}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="max-w-2xl">
        <div className="flex items-center gap-2 mb-1">
          <LayoutGrid className="h-4 w-4 text-muted-foreground" />
          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Quick Filters</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {quickFilters.map((f) => (
            <button
              key={f.value}
              onClick={() => handleSearch(f.value)}
              className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium border border-border bg-background text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            >
              {sourceIcons[f.value]}
              <span className="ml-1.5">{f.label}</span>
            </button>
          ))}
        </div>
      </div>

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-16 rounded-xl bg-muted/50 animate-pulse" />
          ))}
        </div>
      )}
      {results && !isLoading && query && (
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">{allResults.length} results for &ldquo;{query}&rdquo;</p>
          <div className="space-y-2">
            {allResults.slice(0, 20).map((r: any, i: number) => {
              const title = r.title ?? r.name ?? r.subject ?? r.source ?? "—";
              const subtitle = r.status ?? r.category ?? "";
              return (
                <div key={i} className="flex items-center gap-4 bg-white dark:bg-card rounded-xl border border-border p-4 hover:shadow-md hover:border-blue-200 transition-all duration-150 animate-fade-up cursor-pointer" style={{ animationDelay: `${i * 30}ms` }} onClick={() => {
                  if (r.sourceType === "complaint" && r.id) router.push(`/complaint-cases/${r.id}`);
                  if (r.sourceType === "customer" && r.id) router.push(`/customers/${r.id}`);
                  if (r.sourceType === "interaction" && r.id) router.push(`/interactions/${r.id}`);
                  if (r.sourceType === "workflow" && r.id) router.push(`/workflow/${r.id}`);
                }}>
                  <div className="h-9 w-9 rounded-lg bg-muted flex items-center justify-center shrink-0">
                    {sourceIcons[r.sourceType] ?? <Search className="h-4 w-4" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate capitalize">{highlightMatch(title, query)}</p>
                    {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{highlightMatch(subtitle, query)}</p>}
                  </div>
                  <Badge variant={sourceBadge[r.sourceType] as any} className="capitalize shrink-0">{r.sourceType}</Badge>
                </div>
              );
            })}
            {allResults.length === 0 && (
              <div className="text-center py-16">
                <Search className="h-8 w-8 mx-auto mb-3 text-muted-foreground/40" />
                <p className="text-sm text-muted-foreground">No results found for &ldquo;{query}&rdquo;</p>
              </div>
            )}
          </div>
        </div>
      )}
      {!query && (
        <div className="text-center py-20">
          <Search className="h-12 w-12 mx-auto mb-4 text-muted-foreground/20" />
          <p className="text-base text-muted-foreground">Start typing to search across all entities</p>
          <p className="text-sm text-muted-foreground/60 mt-1">Search complaints, customers, workflows, and knowledge base</p>
        </div>
      )}
    </div>
  );
}
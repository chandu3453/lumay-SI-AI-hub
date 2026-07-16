"use client";

import { useState } from "react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useKnowledgeSearch } from "@/features/dashboard/use-dashboard";
import { Search, BookOpen, MessageSquare, FileText } from "lucide-react";

const sourceIcons: Record<string, React.ReactNode> = {
  faq: <MessageSquare className="h-4 w-4 text-blue-500" />,
  policy: <FileText className="h-4 w-4 text-emerald-500" />,
  product: <BookOpen className="h-4 w-4 text-purple-500" />,
};

export default function KnowledgePage() {
  const [query, setQuery] = useState("");
  const [source, setSource] = useState<string | undefined>(undefined);
  const { data, isLoading } = useKnowledgeSearch(query, source);

  return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in">
        <div className="page-header">
          <h1>Knowledge Base</h1>
          <p>Search policies, FAQ, and product information</p>
        </div>

        <div className="flex gap-3 items-start">
          <div className="relative flex-1 max-w-xl">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search knowledge base..."
              className="pl-9 h-10"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <select
            value={source ?? ""}
            onChange={(e) => setSource(e.target.value || undefined)}
            className="h-10 rounded-lg border border-border bg-background px-3 text-sm"
          >
            <option value="">All Sources</option>
            <option value="faq">FAQ</option>
            <option value="policy">Policies</option>
            <option value="product">Products</option>
          </select>
        </div>

        {isLoading && (
          <div className="space-y-3">
            {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-20 rounded-xl" />)}
          </div>
        )}

        {data && !isLoading && (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">{data.total} results for &ldquo;{query}&rdquo; in {data.source}</p>
            {data.results?.map((item: any, i: number) => (
              <Card key={i} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      {sourceIcons[item.source] ?? <BookOpen className="h-4 w-4 text-muted-foreground" />}
                      <CardTitle className="text-sm">{item.title ?? item.question ?? item.name}</CardTitle>
                    </div>
                    <Badge variant="outline" className="capitalize text-xs">{item.source}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{item.answer ?? item.summary ?? item.description}</p>
                  {item.coverage_details && (
                    <p className="text-xs text-muted-foreground mt-2"><span className="font-medium">Coverage:</span> {item.coverage_details}</p>
                  )}
                </CardContent>
              </Card>
            ))}
            {data.results?.length === 0 && (
              <div className="text-center py-16">
                <BookOpen className="h-8 w-8 mx-auto mb-3 text-muted-foreground/40" />
                <p className="text-sm text-muted-foreground">No results found</p>
              </div>
            )}
          </div>
        )}

        {!query && (
          <div className="text-center py-20">
            <BookOpen className="h-12 w-12 mx-auto mb-4 text-muted-foreground/20" />
            <p className="text-base text-muted-foreground">Search policies, FAQ, and product information</p>
            <p className="text-sm text-muted-foreground/60 mt-1">Type a query above to search the knowledge base</p>
          </div>
        )}
      </div>
      <AICopilot />
    </DashboardShell>
  );
}
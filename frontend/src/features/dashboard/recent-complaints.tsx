"use client";

import { useComplaints } from "@/features/dashboard/use-dashboard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { formatRelative } from "@/lib/formatters";
import { DataTable, type Column } from "@/components/ui/data-table";

const statusVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  submitted: "warning", under_review: "neutral", investigating: "default",
  escalated: "destructive", resolved: "success", closed: "neutral", archived: "neutral",
};

export function RecentComplaints() {
  const { data, isLoading } = useComplaints({ page: 1, page_size: 5 });

  if (isLoading) return <Card><CardHeader><CardTitle className="text-sm">Recent Complaints</CardTitle></CardHeader><CardContent className="space-y-3">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-12 w-full rounded-lg" />)}</CardContent></Card>;
  if (!data) return null;

  return (
    <Card>
      <CardHeader><CardTitle className="text-sm">Recent Complaints</CardTitle></CardHeader>
      <CardContent className="p-0">
        <div className="divide-y divide-border">
          {data.items.slice(0, 5).map((c: any) => (
            <div key={c.id} className="flex items-center justify-between px-5 py-3 hover:bg-muted/20 transition-colors">
              <div className="space-y-0.5 min-w-0">
                <p className="text-sm font-medium truncate max-w-[240px]">{c.title}</p>
                <p className="text-xs text-muted-foreground">
                  <span className="capitalize">{c.category}</span>
                  <span className="mx-1">·</span>
                  {c.created_at && formatRelative(c.created_at)}
                </p>
              </div>
              <Badge variant={statusVariant[c.status] ?? "neutral"} className="capitalize shrink-0 ml-3">{c.status}</Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
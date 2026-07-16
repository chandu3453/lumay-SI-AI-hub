"use client";

import { useDemoHealth } from "@/features/dashboard/use-dashboard";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function DemoStatus() {
  const { data: health, isLoading } = useDemoHealth();

  if (isLoading) return <Card><CardHeader><Skeleton className="h-4 w-24" /></CardHeader><CardContent><Skeleton className="h-32 w-full" /></CardContent></Card>;
  if (!health) return null;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm">System Status</CardTitle>
          <Badge variant={health.data_loaded ? "success" : "destructive"}>
            {health.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {health.data_loaded && health.entity_counts && Object.entries(health.entity_counts).map(([key, val]) => (
            <div key={key} className="flex items-center justify-between py-1">
              <span className="text-sm capitalize text-muted-foreground">{key}</span>
              <span className="text-sm font-medium">{val as number}</span>
            </div>
          ))}
          {health.data_loaded && (
            <div className="flex items-center justify-between pt-2 border-t border-border">
              <span className="text-sm font-medium">Total Entities</span>
              <span className="text-sm font-semibold">{health.total_entities}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
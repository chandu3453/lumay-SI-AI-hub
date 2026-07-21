"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDate, formatEnum } from "@/lib/formatters";
import { useCustomerComplaints } from "@/features/customers/hooks/use-customers";
import { Customer360PlaceholderSection } from "./customer-360-placeholder-section";

/** Reuses the same client-filtered-fetch pattern `useCustomerComplaints`
 * already uses elsewhere in the app (`features/customers/hooks/use-customers.ts`)
 * — real data, no new backend endpoint. */
export function Customer360Complaints({ customerId }: { customerId: string | null }) {
  const { data, isLoading } = useCustomerComplaints(customerId);

  if (!customerId) return null;
  if (isLoading) return <Skeleton className="h-20 w-full" />;

  const complaints = data?.items ?? [];
  if (complaints.length === 0) {
    return <Customer360PlaceholderSection title="Complaints" message="No complaints on record for this customer." />;
  }

  return (
    <Card>
      <CardHeader className="p-3 pb-1.5">
        <CardTitle className="text-xs">Complaints ({complaints.length})</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 p-3 pt-0">
        {complaints.slice(0, 5).map((c: any) => (
          <div key={c.id} className="rounded-md border border-border p-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-medium">{c.complaint_number}</span>
              <span className="text-[10px] text-muted-foreground">{formatEnum(c.status)}</span>
            </div>
            <p className="mt-0.5 truncate text-muted-foreground">{c.title}</p>
            {c.created_at ? (
              <p className="mt-0.5 text-[10px] text-muted-foreground">{formatDate(c.created_at, "PP")}</p>
            ) : null}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

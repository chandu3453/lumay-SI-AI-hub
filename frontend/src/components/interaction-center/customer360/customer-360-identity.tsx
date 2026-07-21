"use client";

import { Mail, Phone } from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCustomerProfile } from "@/features/customers/hooks/use-customers";
import { Customer360PlaceholderSection } from "./customer-360-placeholder-section";

export function Customer360Identity({ customerId }: { customerId: string | null }) {
  const { data: customer, isLoading } = useCustomerProfile(customerId);

  if (!customerId) {
    return <Customer360PlaceholderSection title="Customer" message="This conversation has no linked customer." />;
  }
  if (isLoading) {
    return <Skeleton className="h-24 w-full" />;
  }
  if (!customer) {
    return <Customer360PlaceholderSection title="Customer" message="Customer record not found." />;
  }

  const initials = customer.full_name
    .split(/\s+/)
    .slice(0, 2)
    .map((p: string) => p[0])
    .join("")
    .toUpperCase();

  return (
    <Card>
      <CardContent className="flex items-center gap-3 p-3">
        <Avatar className="h-11 w-11">
          <AvatarFallback>{initials}</AvatarFallback>
        </Avatar>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold">{customer.full_name}</p>
          {customer.email ? (
            <p className="flex items-center gap-1 truncate text-[11px] text-muted-foreground">
              <Mail className="h-3 w-3" /> {customer.email}
            </p>
          ) : null}
          {customer.mobile_number ? (
            <p className="flex items-center gap-1 truncate text-[11px] text-muted-foreground">
              <Phone className="h-3 w-3" /> {customer.mobile_number}
            </p>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}

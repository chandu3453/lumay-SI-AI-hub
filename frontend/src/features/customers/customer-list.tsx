"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useCustomers } from "@/features/dashboard/use-dashboard";
import { Search, Users } from "lucide-react";
import { DataTable, type Column } from "@/components/ui/data-table";

const segmentVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  individual: "default", corporate: "neutral", sme: "warning", vip: "success",
};

export function CustomerList() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const { data, isLoading } = useCustomers({ page, page_size: 10 });

  const filtered = data?.items?.filter((c: any) =>
    !search || c.full_name?.toLowerCase().includes(search.toLowerCase()) || c.email?.toLowerCase().includes(search.toLowerCase())
  ) ?? [];

  const columns: Column<any>[] = [
    {
      key: "name",
      header: "Customer",
      render: (c: any) => (
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-muted flex items-center justify-center shrink-0">
            <Users className="h-4 w-4 text-muted-foreground" />
          </div>
          <div>
            <p className="font-medium">{c.full_name}</p>
            <p className="text-xs text-muted-foreground">{c.email ?? "—"}</p>
          </div>
        </div>
      ),
    },
    { key: "segment", header: "Segment", render: (c: any) => <Badge variant={segmentVariant[c.segment] ?? "neutral"} className="capitalize">{c.segment}</Badge> },
    {
      key: "location",
      header: "Location",
      render: (c: any) => <span className="text-muted-foreground">{c.city ?? "—"}{c.state ? `, ${c.state}` : ""}</span>,
    },
    {
      key: "status",
      header: "Status",
      render: (c: any) => <Badge variant="neutral" className="capitalize">{c.status}</Badge>,
    },
  ];

  return (
    <div className="space-y-4">
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input placeholder="Search customers..." className="pl-9" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>
      <DataTable columns={columns} data={filtered.map((c: any) => ({ ...c, id: c.id }))} isLoading={isLoading} emptyMessage="No customers found" page={page} pageSize={10} total={data?.total} onPageChange={setPage} />
    </div>
  );
}
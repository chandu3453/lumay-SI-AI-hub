"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { useComplaints } from "@/features/dashboard/use-dashboard";
import { Search } from "lucide-react";
import { DataTable, type Column } from "@/components/ui/data-table";
import { formatRelative } from "@/lib/formatters";

const statusVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  submitted: "warning", under_review: "neutral", investigating: "default",
  escalated: "destructive", resolved: "success", closed: "neutral", archived: "neutral",
};

const priorityVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  low: "neutral", medium: "default", high: "warning", critical: "destructive",
};

export function ComplaintList() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const { data, isLoading } = useComplaints({ page, page_size: 10 });

  const filtered = data?.items?.filter((c: any) =>
    !search || c.title?.toLowerCase().includes(search.toLowerCase()) || c.category?.toLowerCase().includes(search.toLowerCase())
  ) ?? [];

  const columns: Column<any>[] = [
    {
      key: "title",
      header: "Title",
      sortable: true,
      render: (c: any) => (
        <div>
          <p className="font-medium truncate max-w-[300px]">{c.title}</p>
          <p className="text-xs text-muted-foreground mt-0.5">
            <span className="capitalize">{c.category}</span>
            <span className="mx-1">·</span>
            {c.created_at && formatRelative(c.created_at)}
          </p>
        </div>
      ),
    },
    {
      key: "priority",
      header: "Priority",
      render: (c: any) => <Badge variant={priorityVariant[c.priority] ?? "neutral"} className="capitalize">{c.priority}</Badge>,
    },
    {
      key: "status",
      header: "Status",
      render: (c: any) => <Badge variant={statusVariant[c.status] ?? "neutral"} className="capitalize">{c.status}</Badge>,
    },
  ];

  return (
    <div className="space-y-4">
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input placeholder="Search complaints..." className="pl-9" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>
      <DataTable
        columns={columns}
        data={filtered.map((c: any) => ({ ...c, id: c.id }))}
        isLoading={isLoading}
        emptyMessage="No complaints match your search"
        page={page}
        pageSize={10}
        total={data?.total}
        onPageChange={setPage}
      />
    </div>
  );
}
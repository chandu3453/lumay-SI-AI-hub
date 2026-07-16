"use client";

import { useRouter } from "next/navigation";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { DataTable, type Column } from "@/components/ui/data-table";
import { SeverityBadge } from "./SeverityBadge";
import { SentimentBadge } from "./SentimentBadge";
import { SLAStatusBadge } from "./SLAStatusBadge";
import { ComplaintActions } from "./ComplaintActions";
import type { Complaint } from "@/types/domain";
import { format } from "date-fns";
import { Phone, Bot, MessageSquare, MessageCircle, Mail, FolderOpen, FileText, HelpCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";


const channelConfig: Record<string, { icon: React.ReactNode; bg: string }> = {
  voice: { icon: <Phone className="h-3.5 w-3.5 text-[#10B981]" />, bg: "bg-emerald-50 border border-emerald-100" },
  smart_call: { icon: <Bot className="h-3.5 w-3.5 text-[#8B5CF6]" />, bg: "bg-purple-50 border border-purple-100" },
  whatsapp: { icon: <MessageSquare className="h-3.5 w-3.5 text-[#10B981]" />, bg: "bg-emerald-50 border border-emerald-100" },
  web_chat: { icon: <MessageCircle className="h-3.5 w-3.5 text-[#8B5CF6]" />, bg: "bg-purple-50 border border-purple-100" },
  email: { icon: <Mail className="h-3.5 w-3.5 text-[#2563EB]" />, bg: "bg-blue-50 border border-blue-100" },
  crm: { icon: <FolderOpen className="h-3.5 w-3.5 text-[#0EA5E9]" />, bg: "bg-sky-50 border border-sky-100" },
  manual: { icon: <FileText className="h-3.5 w-3.5 text-[#F59E0B]" />, bg: "bg-amber-50 border border-amber-100" },
};

function getChannelDisplay(channel: string | null | undefined): React.ReactNode {
  if (!channel) return null;
  const config = channelConfig[channel];
  const icon = config ? config.icon : <HelpCircle className="h-3.5 w-3.5 text-muted-foreground" />;
  const bg = config ? config.bg : "bg-slate-50 border border-slate-100";
  return (
    <div className={`flex h-8 w-8 items-center justify-center rounded-xl ${bg}`}>
      {icon}
    </div>
  );
}

function getInitials(name: string | null | undefined): string {
  if (!name) return "?";
  return name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);
}

function formatReceivedTime(dateStr: string | null | undefined): string {
  if (!dateStr) return "—";
  try { return format(new Date(dateStr), "MMM d, yyyy h:mm a"); }
  catch { return "—"; }
}

const statusVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  open: "warning",
  submitted: "warning",
  under_review: "neutral",
  investigating: "default",
  pending_review: "neutral",
  escalated: "destructive",
  resolved: "success",
  closed: "neutral",
  archived: "neutral",
};

const statusLabel: Record<string, string> = {
  open: "Open",
  submitted: "Open",
  under_review: "Pending Review",
  investigating: "Pending Review",
  pending_review: "Pending Review",
  escalated: "Escalated",
  resolved: "Resolved",
  closed: "Closed",
  archived: "Closed",
};

type ComplaintTableProps = {
  data: Complaint[];
  isLoading: boolean;
  total?: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  sortKey?: string;
  sortDir?: "asc" | "desc";
  onSort?: (key: string) => void;
  selectedIds: Set<string>;
  onSelectionChange: (ids: Set<string>) => void;
  onOpen?: (item: Complaint) => void;
  onAssign?: (item: Complaint) => void;
  onTransfer?: (item: Complaint) => void;
  onEscalate?: (item: Complaint) => void;
  onCreateWorkflow?: (item: Complaint) => void;
  onViewCustomer?: (item: Complaint) => void;
  onArchive?: (item: Complaint) => void;
  onDelete?: (item: Complaint) => void;
};

export function ComplaintTable({
  data, isLoading, total, page, pageSize, onPageChange, sortKey, sortDir, onSort, selectedIds, onSelectionChange,
  onOpen, onAssign, onTransfer, onEscalate, onCreateWorkflow, onViewCustomer, onArchive, onDelete,
}: ComplaintTableProps) {
  const router = useRouter();

  const toggleAll = () => {
    if (selectedIds.size === data.length) {
      onSelectionChange(new Set());
    } else {
      onSelectionChange(new Set(data.map((d) => d.id)));
    }
  };

  const toggleOne = (id: string) => {
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    onSelectionChange(next);
  };

  const columns: Column<Complaint>[] = [
    {
      key: "checkbox",
      header: "",
      render: (item) => (
        <input
          type="checkbox"
          checked={selectedIds.has(item.id)}
          onChange={() => toggleOne(item.id)}
          className="rounded border-border h-4 w-4 cursor-pointer"
        />
      ),
      className: "w-[40px]",
      headerClassName: "w-[40px]",
    },
    {
      key: "complaint_number",
      header: "Complaint ID",
      sortable: true,
      render: (item) => (
        <button
          onClick={() => router.push(`/complaint-cases/${item.id}`)}
          className="text-sm font-medium text-primary hover:underline text-left"
        >
          {item.complaint_number ?? `#${item.id.slice(0, 8)}`}
        </button>
      ),
      className: "w-[120px]",
    },
    {
      key: "customer",
      header: "Customer",
      render: (item) => (
        <div className="flex items-center gap-2">
          <Avatar className="h-7 w-7">
            <AvatarFallback className="text-[10px] bg-primary/10 text-primary">
              {getInitials(item.customer_name)}
            </AvatarFallback>
          </Avatar>
          <div className="min-w-0">
            <p className="text-sm truncate max-w-[120px]">{item.customer_name ?? "Unknown"}</p>
          </div>
        </div>
      ),
      className: "w-[150px]",
    },
    {
      key: "channel",
      header: "Channel",
      render: (item) => (
        <div className="flex items-center justify-center">
          {getChannelDisplay(item.channel)}
        </div>
      ),
      className: "w-[60px] text-center",
    },
    {
      key: "theme",
      header: "Theme",
      render: (item) => (
        <span className="text-sm capitalize truncate max-w-[130px] block">
          {item.theme ? item.theme.replace(/_/g, " ") : item.category ? item.category.replace(/_/g, " ") : "—"}
        </span>
      ),
      className: "w-[140px]",
    },
    {
      key: "sentiment",
      header: "Sentiment",
      render: (item) => <SentimentBadge sentiment={item.sentiment} />,
      className: "w-[80px]",
    },
    {
      key: "severity",
      header: "Severity",
      render: (item) => <SeverityBadge severity={item.severity} />,
      className: "w-[90px]",
    },
    {
      key: "sla_status",
      header: "SLA Status",
      render: (item) => <SLAStatusBadge status={item.sla_status} />,
      className: "w-[100px]",
    },
    {
      key: "assigned_to",
      header: "Assigned To",
      sortable: true,
      render: (item) => (
        <span className="text-sm text-muted-foreground truncate max-w-[110px] block">
          {item.assigned_agent_name ?? item.assigned_queue ?? "—"}
        </span>
      ),
      className: "w-[130px]",
    },
    {
      key: "received_time",
      header: "Received Time",
      sortable: true,
      render: (item) => (
        <span className="text-sm text-muted-foreground whitespace-nowrap">
          {formatReceivedTime(item.received_time ?? item.created_at)}
        </span>
      ),
      className: "w-[150px]",
    },
    {
      key: "status",
      header: "Status",
      sortable: true,
      render: (item) => (
        <Badge variant={statusVariant[item.status] ?? "neutral"} className="capitalize">
          {statusLabel[item.status] ?? item.status}
        </Badge>
      ),
      className: "w-[110px]",
    },
    {
      key: "actions",
      header: "Actions",
      render: (item) => (
        <ComplaintActions
          onOpen={() => { router.push(`/complaint-cases/${item.id}`); }}
          onAssign={() => onAssign?.(item)}
          onTransfer={() => onTransfer?.(item)}
          onEscalate={() => onEscalate?.(item)}
          onCreateWorkflow={() => onCreateWorkflow?.(item)}
          onViewCustomer={() => onViewCustomer?.(item)}
          onArchive={() => onArchive?.(item)}
          onDelete={() => onDelete?.(item)}
        />
      ),
      className: "w-[60px]",
    },
  ];

  return (
    <div>
      <DataTable
        columns={columns}
        data={data}
        isLoading={isLoading}
        emptyMessage="No complaints found"
        page={page}
        pageSize={pageSize}
        total={total}
        onPageChange={onPageChange}
        sortKey={sortKey}
        sortDir={sortDir}
        onSort={onSort}
        onRowClick={(item) => router.push(`/complaint-cases/${item.id}`)}
      />
    </div>
  );
}
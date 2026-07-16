"use client";

import { useRouter } from "next/navigation";
import { DataTable, type Column } from "@/components/ui/data-table";
import type { Interaction } from "@/types/domain";
import { format } from "date-fns";
import {
  Phone, Bot, MessageSquare, MessageCircle, Mail, Database, FileText, HelpCircle
} from "lucide-react";
import { InteractionActions } from "./InteractionActions";

const channelConfig: Record<string, { icon: React.ReactNode; bg: string }> = {
  voice: { icon: <Phone className="h-4 w-4 text-[#10B981]" />, bg: "bg-emerald-50 border border-emerald-100" },
  smart_call: { icon: <Bot className="h-4 w-4 text-[#2563EB]" />, bg: "bg-blue-50 border border-blue-100" },
  whatsapp: { icon: <MessageSquare className="h-4 w-4 text-[#10B981]" />, bg: "bg-emerald-50 border border-emerald-100" },
  web_chat: { icon: <MessageCircle className="h-4 w-4 text-[#8B5CF6]" />, bg: "bg-purple-50 border border-purple-100" },
  email: { icon: <Mail className="h-4 w-4 text-[#2563EB]" />, bg: "bg-blue-50 border border-blue-100" },
  crm: { icon: <Database className="h-4 w-4 text-[#6366F1]" />, bg: "bg-indigo-50 border border-indigo-100" },
  manual: { icon: <FileText className="h-4 w-4 text-[#64748B]" />, bg: "bg-slate-50 border border-slate-100" },
};

function getChannelDisplay(channel: string | null | undefined): React.ReactNode {
  if (!channel) return null;
  const config = channelConfig[channel];
  const icon = config ? config.icon : <HelpCircle className="h-4 w-4 text-muted-foreground" />;
  const bg = config ? config.bg : "bg-slate-50 border border-slate-100";
  return (
    <div className={`flex h-9 w-9 items-center justify-center rounded-full shrink-0 ${bg}`}>
      {icon}
    </div>
  );
}

function formatTime(dateStr: string | null | undefined): string {
  if (!dateStr) return "—";
  try { return format(new Date(dateStr), "hh:mm a"); }
  catch { return "—"; }
}

type InteractionTableProps = {
  data: Interaction[];
  isLoading: boolean;
  total?: number;
  page: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onOpen?: (item: Interaction) => void;
  onAssign?: (item: Interaction) => void;
  onCreateComplaint?: (item: Interaction) => void;
  onEscalate?: (item: Interaction) => void;
  onArchive?: (item: Interaction) => void;
};

export function InteractionTable({
  data,
  isLoading,
  total,
  page,
  pageSize,
  onPageChange,
  onOpen,
  onAssign,
  onCreateComplaint,
  onEscalate,
  onArchive,
}: InteractionTableProps) {
  const router = useRouter();

  const columns: Column<Interaction>[] = [
    {
      key: "customer",
      header: "Customer / Channel",
      render: (item) => (
        <div className="flex items-center gap-3">
          {getChannelDisplay(item.channel)}
          <div className="min-w-0 text-left">
            <p className="font-bold text-xs text-[#0F172A] truncate max-w-[145px]">
              {item.customer_name ?? "Unknown Customer"}
            </p>
            <p className="text-[10px] font-bold text-slate-400 truncate max-w-[145px] mt-0.5">
              {item.interaction_number ?? `#${item.id.slice(0, 8)}`}
            </p>
          </div>
        </div>
      ),
      className: "w-[200px]",
    },
    {
      key: "message",
      header: "Last Message / Subject",
      render: (item) => (
        <div className="max-w-md text-left">
          <p className="text-xs font-bold text-[#334155] truncate">{item.subject ?? "No subject"}</p>
          {item.last_message && (
            <p className="text-[11px] font-semibold text-slate-400 line-clamp-1 mt-0.5">{item.last_message}</p>
          )}
        </div>
      ),
      className: "min-w-[250px]",
    },
    {
      key: "time",
      header: "Time",
      render: (item) => (
        <span className="text-xs font-bold text-slate-500 whitespace-nowrap">{formatTime(item.created_at)}</span>
      ),
      className: "w-[100px]",
    },
    {
      key: "status",
      header: "Status",
      render: (item) => {
        const s = (item.status ?? "new").toLowerCase();
        if (s === "new") {
          return <span className="rounded-lg bg-blue-50 border border-blue-100 px-2.5 py-1 text-[11px] font-bold text-[#0052FF]">New</span>;
        } else if (s === "in_progress" || s === "processing") {
          return <span className="rounded-lg bg-amber-50 border border-amber-100 px-2.5 py-1 text-[11px] font-bold text-amber-600">In Progress</span>;
        } else {
          return <span className="rounded-lg bg-slate-50 border border-slate-100 px-2.5 py-1 text-[11px] font-bold text-slate-400">Closed</span>;
        }
      },
      className: "w-[110px]",
    },
    {
      key: "priority",
      header: "Priority",
      render: (item) => {
        const p = (item.priority ?? "medium").toLowerCase();
        if (p === "high" || p === "critical") {
          return <span className="rounded-lg bg-red-50 border border-red-100 px-2.5 py-1 text-[11px] font-bold text-red-600">High</span>;
        } else if (p === "medium") {
          return <span className="rounded-lg bg-amber-50 border border-amber-100 px-2.5 py-1 text-[11px] font-bold text-amber-600">Medium</span>;
        } else {
          return <span className="rounded-lg bg-green-50 border border-green-100 px-2.5 py-1 text-[11px] font-bold text-green-600">Low</span>;
        }
      },
      className: "w-[100px]",
    },
    {
      key: "assigned_to",
      header: "Assigned To",
      render: (item) => (
        <span className="text-xs font-bold text-slate-500">{item.assigned_agent_name ?? item.assigned_to ?? "—"}</span>
      ),
      className: "w-[140px]",
    },
    {
      key: "actions",
      header: "Actions",
      render: (item) => (
        <InteractionActions
          onOpen={() => onOpen?.(item)}
          onAssign={() => onAssign?.(item)}
          onCreateComplaint={() => onCreateComplaint?.(item)}
          onEscalate={() => onEscalate?.(item)}
          onArchive={() => onArchive?.(item)}
        />
      ),
      className: "w-[70px]",
    },
  ];

  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-white shadow-sm overflow-hidden flex flex-col">
      <div className="overflow-x-auto">
        <DataTable
          columns={columns}
          data={data}
          isLoading={isLoading}
          emptyMessage="No interactions found"
          page={page}
          pageSize={pageSize}
          total={total}
          onPageChange={onPageChange}
          onRowClick={(item) => onOpen?.(item)}
        />
      </div>
    </div>
  );
}
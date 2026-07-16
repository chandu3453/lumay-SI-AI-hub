"use client";

import { useRouter } from "next/navigation";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { SeverityBadge } from "./SeverityBadge";
import { SentimentBadge } from "./SentimentBadge";
import { SLAStatusBadge } from "./SLAStatusBadge";
import { ComplaintActions } from "./ComplaintActions";
import type { Complaint } from "@/types/domain";
import { format } from "date-fns";
import { Badge } from "@/components/ui/badge";
import { Phone, Bot, MessageSquare, MessageCircle, Mail, FolderOpen, FileText, HelpCircle } from "lucide-react";

const channelIcons: Record<string, React.ReactNode> = {
  voice: <Phone className="h-3.5 w-3.5 text-blue-500" />,
  smart_call: <Bot className="h-3.5 w-3.5 text-purple-500" />,
  whatsapp: <MessageSquare className="h-3.5 w-3.5 text-emerald-500" />,
  web_chat: <MessageCircle className="h-3.5 w-3.5 text-orange-500" />,
  email: <Mail className="h-3.5 w-3.5 text-violet-500" />,
  crm: <FolderOpen className="h-3.5 w-3.5 text-cyan-500" />,
  manual: <FileText className="h-3.5 w-3.5 text-amber-500" />,
};

function getChannelIcon(channel: string | null | undefined): React.ReactNode {
  if (!channel) return null;
  return channelIcons[channel] ?? <HelpCircle className="h-3.5 w-3.5 text-muted-foreground" />;
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
  open: "warning", submitted: "warning", under_review: "neutral", investigating: "default",
  pending_review: "neutral", escalated: "destructive", resolved: "success", closed: "neutral", archived: "neutral",
};

const statusLabel: Record<string, string> = {
  open: "Open", submitted: "Open", under_review: "Pending Review", investigating: "Pending Review",
  pending_review: "Pending Review", escalated: "Escalated", resolved: "Resolved", closed: "Closed", archived: "Closed",
};

type ComplaintRowProps = {
  item: Complaint;
  isSelected: boolean;
  onToggle: (id: string) => void;
  onOpen?: (item: Complaint) => void;
  onAssign?: (item: Complaint) => void;
  onTransfer?: (item: Complaint) => void;
  onEscalate?: (item: Complaint) => void;
  onCreateWorkflow?: (item: Complaint) => void;
  onViewCustomer?: (item: Complaint) => void;
  onArchive?: (item: Complaint) => void;
  onDelete?: (item: Complaint) => void;
};

export function ComplaintRow({
  item, isSelected, onToggle,
  onOpen, onAssign, onTransfer, onEscalate, onCreateWorkflow, onViewCustomer, onArchive, onDelete,
}: ComplaintRowProps) {
  const router = useRouter();

  return (
    <tr className="transition-colors hover:bg-muted/20 animate-fade-up">
      <td className="px-4 py-3 w-[40px]">
        <input
          type="checkbox"
          checked={isSelected}
          onChange={() => onToggle(item.id)}
          className="rounded border-border h-4 w-4 cursor-pointer"
        />
      </td>
      <td className="px-4 py-3 text-sm w-[120px]">
        <button
          onClick={() => router.push(`/complaint-cases/${item.id}`)}
          className="text-sm font-medium text-primary hover:underline"
        >
          {item.complaint_number ?? `#${item.id.slice(0, 8)}`}
        </button>
      </td>
      <td className="px-4 py-3 text-sm w-[140px]">
        <div className="flex items-center gap-2">
          <Avatar className="h-7 w-7">
            <AvatarFallback className="text-[10px] bg-primary/10 text-primary">
              {getInitials(item.customer_name)}
            </AvatarFallback>
          </Avatar>
          <span className="text-sm truncate max-w-[120px]">{item.customer_name ?? "Unknown"}</span>
        </div>
      </td>
      <td className="px-4 py-3 text-sm w-[50px] text-center">
        {getChannelIcon(item.channel)}
      </td>
      <td className="px-4 py-3 text-sm w-[140px]">
        <span className="text-sm capitalize truncate max-w-[130px] block">
          {item.theme ? item.theme.replace(/_/g, " ") : item.category ? item.category.replace(/_/g, " ") : "—"}
        </span>
      </td>
      <td className="px-4 py-3 text-sm w-[80px]">
        <SentimentBadge sentiment={item.sentiment} />
      </td>
      <td className="px-4 py-3 text-sm w-[90px]">
        <SeverityBadge severity={item.severity} />
      </td>
      <td className="px-4 py-3 text-sm w-[100px]">
        <SLAStatusBadge status={item.sla_status} />
      </td>
      <td className="px-4 py-3 text-sm w-[120px]">
        <span className="text-sm text-muted-foreground truncate max-w-[110px] block">
          {item.assigned_agent_name ?? item.assigned_queue ?? "—"}
        </span>
      </td>
      <td className="px-4 py-3 text-sm w-[150px]">
        <span className="text-sm text-muted-foreground whitespace-nowrap">
          {formatReceivedTime(item.received_time ?? item.created_at)}
        </span>
      </td>
      <td className="px-4 py-3 text-sm w-[100px]">
        <Badge variant={statusVariant[item.status] ?? "neutral"} className="capitalize">
          {statusLabel[item.status] ?? item.status}
        </Badge>
      </td>
      <td className="px-4 py-3 text-sm w-[50px]">
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
      </td>
    </tr>
  );
}
"use client";

import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ComplaintCaseActions } from "./ComplaintCaseActions";
import type { CaseItem } from "@/features/complaint-cases/use-complaint-cases";
import { format } from "date-fns";
import { Phone, Bot, MessageSquare, MessageCircle, Mail, FolderOpen, FileText, HelpCircle } from "lucide-react";

const channelIcons: Record<string, React.ReactNode> = {
  voice: <Phone className="h-3.5 w-3.5 text-blue-500" />, smart_call: <Bot className="h-3.5 w-3.5 text-purple-500" />,
  whatsapp: <MessageSquare className="h-3.5 w-3.5 text-emerald-500" />, web_chat: <MessageCircle className="h-3.5 w-3.5 text-orange-500" />,
  email: <Mail className="h-3.5 w-3.5 text-violet-500" />, crm: <FolderOpen className="h-3.5 w-3.5 text-cyan-500" />,
  manual: <FileText className="h-3.5 w-3.5 text-amber-500" />,
};
function getChannelIcon(ch: string | null | undefined): React.ReactNode {
  if (!ch) return null; return channelIcons[ch] ?? <HelpCircle className="h-3.5 w-3.5 text-muted-foreground" />;
}
function getInitials(name: string | null | undefined): string {
  if (!name) return "?"; return name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);
}
function formatTime(d: string | null | undefined): string {
  if (!d) return "—"; try { return format(new Date(d), "MMM d, yyyy h:mm a"); } catch { return "—"; }
}

const severityVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  low: "neutral", medium: "default", high: "warning", critical: "destructive",
};
const slaVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  on_track: "success", at_risk: "warning", overdue: "destructive", breached: "destructive",
};
const statusVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  new: "destructive", submitted: "warning", acknowledged: "warning", in_progress: "default",
  investigating: "default", pending_review: "neutral", resolved: "success", closed: "neutral",
  escalated: "destructive", archived: "neutral",
};
const statusLabel: Record<string, string> = {
  new: "New", submitted: "New", acknowledged: "Acknowledged", in_progress: "In Progress",
  investigating: "In Progress", pending_review: "Pending Review", resolved: "Resolved",
  closed: "Closed", escalated: "Escalated", archived: "Closed",
};
const slaLabel: Record<string, string> = { on_track: "On Track", at_risk: "At Risk", overdue: "Overdue", breached: "Breached" };

type ComplaintCaseRowProps = {
  item: CaseItem;
  isSelected: boolean;
  onToggle: (id: string) => void;
  onAssign?: (item: CaseItem) => void;
  onTransfer?: (item: CaseItem) => void;
  onEscalate?: (item: CaseItem) => void;
  onArchive?: (item: CaseItem) => void;
};

export function ComplaintCaseRow({ item, isSelected, onToggle, onAssign, onTransfer, onEscalate, onArchive }: ComplaintCaseRowProps) {
  const router = useRouter();
  return (
    <tr className="transition-colors hover:bg-muted/20 animate-fade-up">
      <td className="px-4 py-3 w-[40px]"><input type="checkbox" checked={isSelected} onChange={() => onToggle(item.id)} className="rounded border-border h-4 w-4 cursor-pointer" /></td>
      <td className="px-4 py-3 text-sm w-[130px]">
        <button onClick={() => router.push(`/complaint-cases/${item.id}`)} className="text-sm font-medium text-primary hover:underline text-left">
          {item.case_number ?? item.workflow_number ?? `#${item.id.slice(0, 8)}`}
          {item.external_ref && <span className="text-xs text-muted-foreground block">{item.external_ref}</span>}
        </button>
      </td>
      <td className="px-4 py-3 text-sm w-[140px]">
        <div className="flex items-center gap-2">
          <Avatar className="h-7 w-7"><AvatarFallback className="text-[10px] bg-primary/10 text-primary">{getInitials(item.customer_name)}</AvatarFallback></Avatar>
          <span className="text-sm truncate max-w-[120px]">{item.customer_name ?? "Unknown"}</span>
        </div>
      </td>
      <td className="px-4 py-3 text-sm w-[50px] text-center">{getChannelIcon(item.channel)}</td>
      <td className="px-4 py-3 text-sm w-[140px]"><span className="text-sm capitalize truncate max-w-[130px] block">{item.theme ? item.theme.replace(/_/g, " ") : "—"}</span></td>
      <td className="px-4 py-3 text-sm w-[90px]"><Badge variant={severityVariant[item.severity ?? ""] ?? "neutral"} className="capitalize">{item.severity ?? "—"}</Badge></td>
      <td className="px-4 py-3 text-sm w-[100px]"><Badge variant={slaVariant[item.sla_status] ?? "neutral"} className="capitalize">{slaLabel[item.sla_status] ?? item.sla_status}</Badge></td>
      <td className="px-4 py-3 text-sm w-[120px]">
        <p className="text-sm truncate max-w-[110px]">{item.assigned_agent_name ?? "—"}</p>
        {item.role && <p className="text-[10px] text-muted-foreground truncate max-w-[110px]">{item.role}</p>}
      </td>
      <td className="px-4 py-3 text-sm w-[150px]"><span className="text-sm text-muted-foreground whitespace-nowrap">{formatTime(item.received_time ?? item.created_at)}</span></td>
      <td className="px-4 py-3 text-sm w-[100px]"><Badge variant={statusVariant[item.workflow_status] ?? "neutral"} className="capitalize">{statusLabel[item.workflow_status] ?? item.workflow_status}</Badge></td>
      <td className="px-4 py-3 text-sm w-[50px]">
        <ComplaintCaseActions
          onViewCase={() => router.push(`/complaint-cases/${item.id}`)}
          onAssign={() => onAssign?.(item)}
          onTransfer={() => onTransfer?.(item)}
          onEscalate={() => onEscalate?.(item)}
          onViewWorkflow={() => router.push(`/workflow/${item.id}`)}
          onArchive={() => onArchive?.(item)}
        />
      </td>
    </tr>
  );
}
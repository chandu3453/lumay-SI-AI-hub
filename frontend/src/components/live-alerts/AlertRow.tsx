"use client";

import { useRouter } from "next/navigation";
import { AlertSeverityBadge } from "./AlertSeverityBadge";
import { SLARiskBadge } from "./SLARiskBadge";
import { AlertStatusBadge } from "./AlertStatusBadge";
import { AlertActions } from "./AlertActions";
import type { AlertItem } from "@/features/live-alerts/use-live-alerts";
import { formatDistanceToNow, format } from "date-fns";
import { Phone, Bot, MessageSquare, MessageCircle, Mail, FolderOpen, FileText, HelpCircle } from "lucide-react";
import { cn } from "@/lib/cn";

const channelIcons: Record<string, React.ReactNode> = {
  voice: <Phone className="h-3.5 w-3.5 text-blue-500" />,
  smart_call: <Bot className="h-3.5 w-3.5 text-purple-500" />,
  whatsapp: <MessageSquare className="h-3.5 w-3.5 text-emerald-500" />,
  web_chat: <MessageCircle className="h-3.5 w-3.5 text-orange-500" />,
  email: <Mail className="h-3.5 w-3.5 text-violet-500" />,
  crm: <FolderOpen className="h-3.5 w-3.5 text-cyan-500" />,
  manual: <FileText className="h-3.5 w-3.5 text-amber-500" />,
  in_app: <MessageCircle className="h-3.5 w-3.5 text-orange-500" />,
};

function getChannelIcon(channel: string | null | undefined): React.ReactNode {
  if (!channel) return null;
  return channelIcons[channel] ?? <HelpCircle className="h-3.5 w-3.5 text-muted-foreground" />;
}

function formatTime(dateStr: string | null | undefined): string {
  if (!dateStr) return "—";
  try {
    const d = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    if (diffMs < 3600000) return formatDistanceToNow(d, { addSuffix: true });
    return format(d, "hh:mm a");
  } catch { return "—"; }
}

const severityColors: Record<string, string> = {
  high: "bg-destructive",
  medium: "bg-warning",
  low: "bg-yellow-400",
};

type AlertRowProps = {
  item: AlertItem;
  onOpenComplaint?: (item: AlertItem) => void;
  onViewCustomer?: (item: AlertItem) => void;
  onViewWorkflow?: (item: AlertItem) => void;
  onAssignOfficer?: (item: AlertItem) => void;
  onAcknowledge?: (item: AlertItem) => void;
  onEscalate?: (item: AlertItem) => void;
  onArchive?: (item: AlertItem) => void;
};

export function AlertRow({
  item, onOpenComplaint, onViewCustomer, onViewWorkflow, onAssignOfficer, onAcknowledge, onEscalate, onArchive,
}: AlertRowProps) {
  const router = useRouter();
  const indicatorColor = severityColors[item.severity ?? ""] || "bg-border";

  return (
    <tr className="transition-colors hover:bg-muted/20 animate-fade-up">
      <td className="px-4 py-3 text-sm w-[100px]">
        <div className="flex items-center gap-2">
          <div className={cn("h-8 w-1 rounded-full shrink-0", indicatorColor)} />
          <span className="text-sm text-muted-foreground whitespace-nowrap">{formatTime(item.created_at)}</span>
        </div>
      </td>
      <td className="px-4 py-3 text-sm w-[50px] text-center">
        {getChannelIcon(item.channel)}
      </td>
      <td className="px-4 py-3 text-sm w-[160px]">
        <p className="text-sm font-medium truncate max-w-[130px]">{item.customer_name ?? "Unknown"}</p>
        {item.policy_number && (
          <p className="text-xs text-muted-foreground truncate max-w-[140px]">
            {item.policy_number}{item.product ? ` | ${item.product}` : ""}
          </p>
        )}
      </td>
      <td className="px-4 py-3 text-sm w-[160px]">
        <span className="text-sm truncate max-w-[150px] block">{item.alert_type ?? "—"}</span>
      </td>
      <td className="px-4 py-3 text-sm min-w-[200px]">
        <p className="text-sm text-muted-foreground line-clamp-2 max-w-[280px]">{item.ai_summary || "—"}</p>
      </td>
      <td className="px-4 py-3 text-sm w-[90px]">
        <AlertSeverityBadge severity={item.severity} />
      </td>
      <td className="px-4 py-3 text-sm w-[100px]">
        <SLARiskBadge risk={item.sla_risk} />
      </td>
      <td className="px-4 py-3 text-sm w-[100px]">
        <AlertStatusBadge status={item.status} />
      </td>
      <td className="px-4 py-3 text-sm w-[50px]">
        <AlertActions
          onOpenComplaint={() => { if (item.complaint_id) router.push(`/complaint-cases/${item.complaint_id}`); else onOpenComplaint?.(item); }}
          onViewCustomer={() => onViewCustomer?.(item)}
          onViewWorkflow={() => onViewWorkflow?.(item)}
          onAssignOfficer={() => onAssignOfficer?.(item)}
          onAcknowledge={() => onAcknowledge?.(item)}
          onEscalate={() => onEscalate?.(item)}
          onArchive={() => onArchive?.(item)}
        />
      </td>
    </tr>
  );
}
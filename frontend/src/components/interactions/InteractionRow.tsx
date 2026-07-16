"use client";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { InteractionStatusBadge } from "./InteractionStatusBadge";
import { PriorityBadge } from "./PriorityBadge";
import { InteractionActions } from "./InteractionActions";
import type { Interaction } from "@/types/domain";
import { format } from "date-fns";
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

function getChannelIcon(channel: string): React.ReactNode {
  return channelIcons[channel] ?? <HelpCircle className="h-3.5 w-3.5 text-muted-foreground" />;
}

function getInitials(name: string | null | undefined): string {
  if (!name) return "?";
  return name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);
}

function formatTime(dateStr: string | null | undefined): string {
  if (!dateStr) return "—";
  try { return format(new Date(dateStr), "hh:mm a"); }
  catch { return "—"; }
}

type InteractionRowProps = {
  item: Interaction;
  onOpen?: (item: Interaction) => void;
  onAssign?: (item: Interaction) => void;
  onCreateComplaint?: (item: Interaction) => void;
  onEscalate?: (item: Interaction) => void;
  onArchive?: (item: Interaction) => void;
};

export function InteractionRow({ item, onOpen, onAssign, onCreateComplaint, onEscalate, onArchive }: InteractionRowProps) {
  return (
    <tr className="transition-colors hover:bg-muted/20 animate-fade-up">
      <td className="px-4 py-3 text-sm w-[220px]">
        <div className="flex items-center gap-3">
          <Avatar className="h-8 w-8">
            <AvatarFallback className="text-xs bg-primary/10 text-primary">
              {getInitials(item.customer_name)}
            </AvatarFallback>
          </Avatar>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5">
              <p className="font-medium text-sm truncate max-w-[140px]">
                {item.customer_name ?? "Unknown Customer"}
              </p>
              {getChannelIcon(item.channel)}
            </div>
            <p className="text-xs text-muted-foreground truncate max-w-[160px]">
              {item.interaction_number ?? `#${item.id.slice(0, 8)}`}
            </p>
          </div>
        </div>
      </td>
      <td className="px-4 py-3 text-sm min-w-[200px]">
        <div className="max-w-[280px]">
          <p className="text-sm font-medium truncate">{item.subject ?? "No subject"}</p>
          {item.last_message && (
            <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">{item.last_message}</p>
          )}
        </div>
      </td>
      <td className="px-4 py-3 text-sm w-[90px]">
        <span className="text-sm text-muted-foreground whitespace-nowrap">{formatTime(item.created_at)}</span>
      </td>
      <td className="px-4 py-3 text-sm w-[100px]">
        <InteractionStatusBadge status={item.status} />
      </td>
      <td className="px-4 py-3 text-sm w-[90px]">
        {item.priority ? <PriorityBadge priority={item.priority} /> : <span className="text-sm text-muted-foreground">—</span>}
      </td>
      <td className="px-4 py-3 text-sm w-[120px]">
        <span className="text-sm text-muted-foreground">{item.assigned_agent_name ?? item.assigned_to ?? "—"}</span>
      </td>
      <td className="px-4 py-3 text-sm w-[60px]">
        <InteractionActions
          onOpen={() => onOpen?.(item)}
          onAssign={() => onAssign?.(item)}
          onCreateComplaint={() => onCreateComplaint?.(item)}
          onEscalate={() => onEscalate?.(item)}
          onArchive={() => onArchive?.(item)}
        />
      </td>
    </tr>
  );
}
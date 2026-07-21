"use client";

import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  Clock,
  User,
  CheckCircle2,
  ShieldAlert,
  MessageSquare,
  Shield,
  Settings,
  Phone,
  Mail,
  MessageCircle,
  Globe,
  Radio,
  ClipboardList,
} from "lucide-react";
import { cn } from "@/lib/cn";
import { formatRelative } from "@/lib/formatters";
import type { NotificationItem } from "./use-notifications";
import { InsuranceBadge } from "@/components/insurance/InsuranceBadge";

const typeIcons: Record<string, React.ReactNode> = {
  "High Risk Complaint": <AlertTriangle className="h-5 w-5" />,
  "SLA Breach": <Clock className="h-5 w-5" />,
  "Case Assigned": <User className="h-5 w-5" />,
  "Complaint Resolved": <CheckCircle2 className="h-5 w-5" />,
  "Investigation Overdue": <ShieldAlert className="h-5 w-5" />,
  "Customer Feedback": <MessageSquare className="h-5 w-5" />,
  "Regulatory Alert": <Shield className="h-5 w-5" />,
  "System Update": <Settings className="h-5 w-5" />,
};

const channelIcons: Record<string, React.ReactNode> = {
  voice: <Phone className="h-3 w-3" />,
  whatsapp: <MessageCircle className="h-3 w-3" />,
  email: <Mail className="h-3 w-3" />,
  web_chat: <Globe className="h-3 w-3" />,
  smart_call: <Radio className="h-3 w-3" />,
  crm: <ClipboardList className="h-3 w-3" />,
  manual: <ClipboardList className="h-3 w-3" />,
  survey: <ClipboardList className="h-3 w-3" />,
};

const priorityColors: Record<string, string> = {
  critical: "#DC2626",
  high: "#F59E0B",
  medium: "#2563EB",
  low: "#64748B",
  success: "#16A34A",
  info: "#8B5CF6",
};

const typeBgColors: Record<string, string> = {
  "High Risk Complaint": "bg-[#FEF2F2] text-[#DC2626]",
  "SLA Breach": "bg-[#FFFBEB] text-[#F59E0B]",
  "Case Assigned": "bg-[#EFF6FF] text-[#2563EB]",
  "Complaint Resolved": "bg-[#F0FDF4] text-[#16A34A]",
  "Investigation Overdue": "bg-[#FFF7ED] text-[#F97316]",
  "Customer Feedback": "bg-[#F5F3FF] text-[#8B5CF6]",
  "Regulatory Alert": "bg-[#FEF2F2] text-[#DC2626]",
  "System Update": "bg-[#F8FAFC] text-[#64748B]",
};

type NotificationCardProps = {
  notification: NotificationItem;
  onMarkRead?: (id: string) => void;
};

export function NotificationCard({ notification: n, onMarkRead }: NotificationCardProps) {
  const router = useRouter();
  return (
    <div
      className={cn(
        "flex gap-4 p-4 rounded-xl border transition-all cursor-pointer hover:shadow-sm hover:border-border",
        n.read ? "bg-white border-border" : "bg-[#F8FAFC] border-[#E2E8F0]",
      )}
      onClick={() => {
        if (n.complaint_case) router.push(`/complaint-cases/${n.complaint_case}`);
        else if (n.workflow) router.push(`/workflow/${n.workflow}`);
      }}
    >
      <div className="flex flex-col items-center gap-2 pt-0.5">
        <div
          className="w-1 h-full min-h-[80px] rounded-full shrink-0"
          style={{ backgroundColor: priorityColors[n.priority] ?? "#94A3B8" }}
        />
      </div>

      <div className="flex items-start gap-3 flex-1 min-w-0">
        <div
          className={cn(
            "h-10 w-10 rounded-lg flex items-center justify-center shrink-0",
            typeBgColors[n.type] ?? "bg-muted text-muted-foreground",
          )}
        >
          {typeIcons[n.type] ?? <Settings className="h-5 w-5" />}
        </div>

        <div className="flex-1 min-w-0 space-y-1">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-[#0F172A] truncate">{n.title}</h3>
                {!n.read && <span className="h-2 w-2 rounded-full bg-[#2563EB] shrink-0" />}
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">{n.type}</p>
            </div>
            <span className="text-[11px] text-muted-foreground whitespace-nowrap shrink-0">
              {formatRelative(n.created_at)}
            </span>
          </div>

          <p className="text-xs text-[#475569] leading-relaxed line-clamp-2">{n.description}</p>

          <div className="flex items-center flex-wrap gap-x-3 gap-y-1 pt-1">
            {n.channel && (
              <span className="inline-flex items-center gap-1 text-[11px] text-muted-foreground capitalize">
                {channelIcons[n.channel] ?? null}
                {n.channel.replace(/_/g, " ")}
              </span>
            )}
            {n.customer && (
              <span className="text-[11px] text-muted-foreground">{n.customer}</span>
            )}
            {n.complaint_case && (
              <span className="text-[11px] font-medium text-[#2563EB]">{n.complaint_case}</span>
            )}
            {n.workflow && (
              <span className="text-[11px] font-medium text-[#8B5CF6]">{n.workflow}</span>
            )}
            {n.assigned_officer && (
              <span className="text-[11px] text-muted-foreground">→ {n.assigned_officer}</span>
            )}
            {n.sla && (
              <span className="text-[11px] text-[#F59E0B] font-medium">SLA: {n.sla}</span>
            )}
            {n.type && (
              <InsuranceBadge line={n.type === "High Risk Complaint" ? "Motor" : n.type === "SLA Breach" ? "Medical & Health" : n.type === "Customer Feedback" ? "Travel" : n.type === "Regulatory Alert" ? "Business Insurance" : n.type === "Case Assigned" ? "Home" : "Policy Servicing"} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
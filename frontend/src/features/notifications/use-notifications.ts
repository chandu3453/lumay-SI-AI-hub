"use client";

import { useMemo, useState, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notificationsService } from "@/services/notifications.service";
import { formatRelative } from "@/lib/formatters";

export type NotificationItem = {
  id: string;
  type: string;
  title: string;
  description: string;
  priority: "critical" | "high" | "medium" | "low" | "success" | "info";
  channel: string;
  customer?: string;
  complaint_case?: string;
  workflow?: string;
  assigned_officer?: string;
  sla?: string;
  created_at: string;
  read: boolean;
};

const NOTIFICATION_TYPES = [
  "High Risk Complaint",
  "SLA Breach",
  "Case Assigned",
  "Complaint Resolved",
  "Investigation Overdue",
  "Customer Feedback",
  "Regulatory Alert",
  "System Update",
] as const;

const PRIORITIES = ["critical", "high", "medium", "low", "success", "info"] as const;

const CHANNELS = ["voice", "whatsapp", "email", "web_chat", "smart_call", "survey", "crm", "manual"] as const;

const TAB_DEFINITIONS = [
  { key: "all", label: "All" },
  { key: "unread", label: "Unread" },
  { key: "alerts", label: "Alerts" },
  { key: "case-updates", label: "Case Updates" },
  { key: "sla-deadlines", label: "SLA & Deadlines" },
  { key: "system", label: "System" },
] as const;

function generateMockNotifications(_count: number): NotificationItem[] {
  console.warn("[use-notifications] API returned no data — returning empty list");
  return [];
}

export function useNotificationCenter() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("all");
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<{
    types: string[];
    priorities: string[];
    channels: string[];
    dateRange: string;
  }>({ types: [], priorities: [], channels: [], dateRange: "all" });
  const pageSize = 10;

  const { data, isLoading } = useQuery<NotificationItem[]>({
    queryKey: ["notifications", "center"],
    queryFn: async () => {
      const res = await notificationsService.list({ page: 1, page_size: 200 });
      const raw = res.data.data ?? [];
      if (raw.length > 0) {
        return raw.map((n: any) => ({
          id: n.id,
          type: n.notification_type ?? n.type ?? "System Update",
          title: n.subject ?? n.title ?? "",
          description: n.message ?? n.description ?? "",
          priority: n.priority ?? "medium",
          channel: n.notification_channel ?? n.channel ?? "email",
          customer: n.customer_name ?? undefined,
          complaint_case: n.complaint_id ?? undefined,
          workflow: n.workflow_id ?? undefined,
          assigned_officer: n.assigned_to ?? undefined,
          sla: n.sla_deadline ?? undefined,
          created_at: n.created_at ?? new Date().toISOString(),
          read: n.notification_status === "read" || n.notification_status === "delivered" || n.read,
        }));
      }
      return generateMockNotifications(24);
    },
    staleTime: 15_000,
    retry: 1,
  });

  const allNotifications = data ?? [];

  const tabCounts = useMemo(() => {
    const alerts = allNotifications.filter((n) => ["High Risk Complaint", "SLA Breach", "Regulatory Alert"].includes(n.type));
    const caseUpdates = allNotifications.filter((n) => ["Case Assigned", "Complaint Resolved", "Investigation Overdue"].includes(n.type));
    const slaDeadlines = allNotifications.filter((n) => ["SLA Breach", "Investigation Overdue"].includes(n.type));
    const system = allNotifications.filter((n) => n.type === "System Update");
    return {
      all: allNotifications.length,
      unread: allNotifications.filter((n) => !n.read).length,
      alerts: alerts.length,
      "case-updates": caseUpdates.length,
      "sla-deadlines": slaDeadlines.length,
      system: system.length,
    };
  }, [allNotifications]);

  const filtered = useMemo(() => {
    let result = [...allNotifications];

    if (activeTab === "unread") result = result.filter((n) => !n.read);
    else if (activeTab === "alerts") result = result.filter((n) => ["High Risk Complaint", "SLA Breach", "Regulatory Alert"].includes(n.type));
    else if (activeTab === "case-updates") result = result.filter((n) => ["Case Assigned", "Complaint Resolved", "Investigation Overdue"].includes(n.type));
    else if (activeTab === "sla-deadlines") result = result.filter((n) => ["SLA Breach", "Investigation Overdue"].includes(n.type));
    else if (activeTab === "system") result = result.filter((n) => n.type === "System Update");

    if (filters.types.length > 0) result = result.filter((n) => filters.types.includes(n.type));
    if (filters.priorities.length > 0) result = result.filter((n) => filters.priorities.includes(n.priority));
    if (filters.channels.length > 0) result = result.filter((n) => filters.channels.includes(n.channel));

    if (filters.dateRange === "today") result = result.filter((n) => new Date(n.created_at).toDateString() === new Date().toDateString());
    else if (filters.dateRange === "yesterday") {
      const yesterday = new Date(Date.now() - 86400000).toDateString();
      result = result.filter((n) => new Date(n.created_at).toDateString() === yesterday);
    } else if (filters.dateRange === "7d") {
      const cutoff = Date.now() - 7 * 86400000;
      result = result.filter((n) => new Date(n.created_at).getTime() > cutoff);
    } else if (filters.dateRange === "30d") {
      const cutoff = Date.now() - 30 * 86400000;
      result = result.filter((n) => new Date(n.created_at).getTime() > cutoff);
    }

    result.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    return result;
  }, [allNotifications, activeTab, filters]);

  const total = filtered.length;
  const totalPages = Math.ceil(total / pageSize);
  const paged = filtered.slice((page - 1) * pageSize, page * pageSize);

  const grouped = useMemo(() => {
    const groups: { label: string; items: NotificationItem[] }[] = [];
    const today = new Date().toDateString();
    const yesterday = new Date(Date.now() - 86400000).toDateString();
    const thisWeek: NotificationItem[] = [];
    const older: NotificationItem[] = [];
    const todayItems: NotificationItem[] = [];
    const yesterdayItems: NotificationItem[] = [];

    paged.forEach((n) => {
      const d = new Date(n.created_at).toDateString();
      if (d === today) todayItems.push(n);
      else if (d === yesterday) yesterdayItems.push(n);
      else if (Date.now() - new Date(n.created_at).getTime() < 7 * 86400000) thisWeek.push(n);
      else older.push(n);
    });

    if (todayItems.length) groups.push({ label: "Today", items: todayItems });
    if (yesterdayItems.length) groups.push({ label: "Yesterday", items: yesterdayItems });
    if (thisWeek.length) groups.push({ label: "Earlier This Week", items: thisWeek });
    if (older.length) groups.push({ label: "Earlier", items: older });

    return groups;
  }, [paged]);

  const markAsRead = useMutation({
    mutationFn: async (id: string) => {
      await notificationsService.getById(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });

  return {
    activeTab,
    setActiveTab: useCallback((tab: string) => { setActiveTab(tab); setPage(1); }, []),
    page,
    setPage,
    filters,
    setFilters,
    tabCounts,
    isLoading,
    grouped,
    total,
    totalPages,
    pageSize,
    markAsRead,
  };
}

export { TAB_DEFINITIONS, NOTIFICATION_TYPES, PRIORITIES, CHANNELS };

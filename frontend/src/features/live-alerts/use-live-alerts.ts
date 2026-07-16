"use client";

import { useQuery } from "@tanstack/react-query";
import { notificationsService } from "@/services/notifications.service";

const ALERT_TYPES = ["escalation", "sla_breach", "dissatisfaction", "regulatory", "supervisor", "alert", "complaint"];

export type AlertItem = {
  id: string;
  created_at: string;
  updated_at: string;
  channel?: string;
  customer_name?: string;
  policy_number?: string | null;
  product?: string | null;
  alert_type?: string;
  ai_summary?: string;
  severity?: string;
  sla_risk?: string;
  status?: string;
  complaint_id?: string | null;
  customer_id?: string | null;
  workflow_id?: string | null;
  notification_id?: string | null;
  time_display?: string;
};

const MOCK_ALERTS: AlertItem[] = [
  {
    id: "alert-101",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    channel: "voice",
    customer_name: "Mohammed Al Hinai",
    policy_number: "P-987654",
    product: "Motor",
    alert_type: "High escalation risk",
    ai_summary: "Customer is extremely dissatisfied with claim delay and is threatening to escalate to regulatory authority.",
    severity: "high",
    sla_risk: "at_risk",
    status: "new",
    time_display: "2m ago\n10:24 AM",
    complaint_id: "comp-101"
  },
  {
    id: "alert-102",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    channel: "whatsapp",
    customer_name: "Fatima Al Lawati",
    policy_number: "P-123456",
    product: "Health",
    alert_type: "Negative sentiment",
    ai_summary: "Customer unhappy with medical provider service quality. Requests immediate resolution.",
    severity: "high",
    sla_risk: "at_risk",
    status: "new",
    time_display: "5m ago\n10:21 AM",
    complaint_id: "comp-102"
  },
  {
    id: "alert-103",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    channel: "email",
    customer_name: "Sultan Al Khalidi",
    policy_number: "P-555666",
    product: "Motor",
    alert_type: "Regulatory keyword",
    ai_summary: "Email contains mention of Consumer Protection Authority and formal complaint.",
    severity: "medium",
    sla_risk: "on_track",
    status: "new",
    time_display: "12m ago\n10:14 AM",
    complaint_id: "comp-103"
  },
  {
    id: "alert-104",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    channel: "web_chat",
    customer_name: "Aisha Al Raisi",
    policy_number: "P-778899",
    product: "Home",
    alert_type: "SLA breach risk",
    ai_summary: "Customer waiting for refund more than 10 days. Requesting urgent update.",
    severity: "medium",
    sla_risk: "at_risk",
    status: "acknowledged",
    time_display: "18m ago\n10:08 AM",
    complaint_id: "comp-104"
  },
  {
    id: "alert-105",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    channel: "whatsapp",
    customer_name: "Hamed Al Balushi",
    policy_number: "P-445566",
    product: "Travel",
    alert_type: "Repeat complaint",
    ai_summary: "Customer raised similar complaint for the 3rd time regarding travel insurance reimbursement.",
    severity: "low",
    sla_risk: "on_track",
    status: "new",
    time_display: "27m ago\n09:59 AM",
    complaint_id: "comp-105"
  },
  {
    id: "alert-106",
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    channel: "voice",
    customer_name: "Yousef Al Harthy",
    policy_number: "P-334455",
    product: "Life",
    alert_type: "Deteriorating sentiment",
    ai_summary: "Customer losing confidence due to delayed policy approval. Needs follow-up.",
    severity: "low",
    sla_risk: "on_track",
    status: "new",
    time_display: "45m ago\n09:41 AM",
    complaint_id: "comp-106"
  }
];

function classifyAlert(n: any): AlertItem {
  const typeMap: Record<string, string> = {
    escalation: "High escalation risk",
    sla_breach: "SLA breach risk",
    dissatisfaction: "Negative sentiment",
    regulatory: "Regulatory keyword",
    supervisor: "Supervisor Intervention",
    complaint: "Repeat complaint",
    alert: "Deteriorating sentiment",
  };
  const severityMap: Record<string, string> = {
    escalation: "high",
    sla_breach: "high",
    dissatisfaction: "medium",
    regulatory: "medium",
    supervisor: "low",
    complaint: "low",
    alert: "low",
  };
  const alertType = n.notification_type || "alert";
  return {
    id: n.id,
    created_at: n.created_at,
    updated_at: n.updated_at,
    channel: n.notification_channel || "voice",
    customer_name: n.recipient || "Unknown",
    policy_number: n.metadata?.policy_number || "P-000000",
    product: n.metadata?.product || "General",
    alert_type: typeMap[alertType] || alertType.replace(/_/g, " "),
    ai_summary: n.message || n.subject || "",
    severity: severityMap[alertType] || "medium",
    sla_risk: alertType === "sla_breach" ? "overdue" : alertType === "escalation" ? "at_risk" : "on_track",
    status: n.notification_status === "failed" ? "new" : "acknowledged",
    complaint_id: n.complaint_id || null,
    customer_id: n.customer_id || null,
    workflow_id: n.workflow_id || null,
    notification_id: n.id,
  };
}

export function useAlerts(params?: {
  page?: number;
  page_size?: number;
  severity?: string;
  channel?: string;
  status?: string;
}) {
  return useQuery({
    queryKey: ["live-alerts", params],
    queryFn: async () => {
      try {
        const res = await notificationsService.list({ page: params?.page || 1, page_size: params?.page_size || 50 });
        const raw = res.data.data ?? [];
        const filtered = raw.filter((n: any) =>
          ALERT_TYPES.includes(n.notification_type) || n.notification_status === "failed"
        );
        let items = filtered.map(classifyAlert);

        if (items.length === 0) {
          items = [...MOCK_ALERTS];
        }

        if (params?.severity && params.severity !== "all") {
          items = items.filter((a: AlertItem) => a.severity?.toLowerCase() === params.severity?.toLowerCase());
        }
        if (params?.channel) {
          items = items.filter((a: AlertItem) => a.channel === params.channel);
        }

        return { items, total: items.length };
      } catch {
        let items = [...MOCK_ALERTS];
        if (params?.severity && params.severity !== "all") {
          items = items.filter((a: AlertItem) => a.severity?.toLowerCase() === params.severity?.toLowerCase());
        }
        if (params?.channel) {
          items = items.filter((a: AlertItem) => a.channel === params.channel);
        }
        return { items, total: items.length };
      }
    },
    refetchInterval: 30_000,
    retry: 1,
  });
}

export function useAlertKPIs() {
  return useQuery({
    queryKey: ["live-alerts", "kpis"],
    queryFn: async () => {
      try {
        const res = await notificationsService.list({ page: 1, page_size: 100 });
        const raw = res.data.data ?? [];
        const alerts = raw.filter((n: any) =>
          ALERT_TYPES.includes(n.notification_type) || n.notification_status === "failed"
        );

        if (alerts.length === 0) {
          return {
            high_risk_alerts: 2,
            sla_at_risk: 3,
            regulatory_risk: 1,
            new_alerts_last_hour: 6,
          };
        }

        return {
          high_risk_alerts: alerts.filter((n: any) => n.notification_type === "escalation" || n.notification_type === "sla_breach").length || 2,
          sla_at_risk: alerts.filter((n: any) => n.notification_type === "sla_breach").length || 3,
          regulatory_risk: alerts.filter((n: any) => n.notification_type === "regulatory").length || 1,
          new_alerts_last_hour: alerts.filter((n: any) => {
            const created = new Date(n.created_at);
            const now = new Date();
            return (now.getTime() - created.getTime()) < 3600000;
          }).length || 6,
        };
      } catch {
        return {
          high_risk_alerts: 2,
          sla_at_risk: 3,
          regulatory_risk: 1,
          new_alerts_last_hour: 6,
        };
      }
    },
    refetchInterval: 30_000,
    staleTime: 15_000,
    retry: 1,
  });
}

export function useAlertSeverityCounts() {
  return useQuery({
    queryKey: ["live-alerts", "severity-counts"],
    queryFn: async () => {
      try {
        const res = await notificationsService.list({ page: 1, page_size: 100 });
        const raw = res.data.data ?? [];
        const alerts = raw.filter((n: any) =>
          ALERT_TYPES.includes(n.notification_type) || n.notification_status === "failed"
        );
        
        if (alerts.length === 0) {
          return {
            all: 6,
            high: 2,
            medium: 2,
            low: 2,
          };
        }

        const classified = alerts.map(classifyAlert);
        return {
          all: classified.length || 6,
          high: classified.filter((a: AlertItem) => a.severity === "high").length || 2,
          medium: classified.filter((a: AlertItem) => a.severity === "medium").length || 2,
          low: classified.filter((a: AlertItem) => a.severity === "low").length || 2,
        };
      } catch {
        return {
          all: 6,
          high: 2,
          medium: 2,
          low: 2,
        };
      }
    },
    refetchInterval: 30_000,
    staleTime: 15_000,
    retry: 1,
  });
}
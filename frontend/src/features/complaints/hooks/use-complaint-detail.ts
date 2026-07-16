"use client";

import { useQuery } from "@tanstack/react-query";
import { complaintsService } from "@/services/complaints.service";

export type ComplaintDetail = {
  id: string;
  complaint_number: string;
  title: string;
  description: string;
  status: string;
  severity: string;
  priority: string;
  category: string;
  subcategory: string;
  source: string;
  channel: string;
  insurance_line: string;
  product_name: string;
  policy_number: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  assigned_agent_name: string;
  assigned_queue: string;
  received_time: string;
  sla_status: string;
  sentiment: string;
  root_cause: string;
  escalation_risk: string;
  duplicate_complaint: boolean;
  is_repeat: boolean;
  is_overdue: boolean;
  ai_summary: string;

  // Phase 2 additions
  product?: string | null;
  claim_number?: string | null;
  detected_language?: string | null;
  theme?: string | null;
  customer_requested_outcome?: string | null;
  recommendation?: string | null;
  sentiment_start?: string | null;
  sentiment_end?: string | null;
  contributing_factors?: string[] | null;
  sla_risk?: string | null;
  resolution_deadline?: string | null;
  sla_breach_probability?: number | null;
  regulatory_flag?: boolean | null;
  acknowledged_time?: string | null;
  interaction_id: string | null;
  assigned_agent_id: string | null;
  created_at: string;
  updated_at: string;

  ai_insights: {
    negative_keywords: string[];
    detected_entities: string[];
    topics: string[];
    emotion: string;
    confidence: number;
    risk_score: number;
  };
  timeline: { stage: string; date: string; completed: boolean }[];
  interactions: {
    id: string; channel: string; direction: string; subject: string;
    summary: string; timestamp: string; agent: string;
  }[];
  customer: {
    id: string; name: string; email: string; phone: string;
    segment: string; city: string; risk_level: string;
    total_complaints: number; total_interactions: number;
    lifetime_value: number; churn_risk: string;
    policies: { product: string; policy_number: string; status: string; line: string }[];
  };
  attachments: { id: string; name: string; type: string; size: string; date: string }[];
  notes: { id: string; type: string; author: string; content: string; date: string }[];
};

function mockDetail(_id: string): ComplaintDetail {
  throw new Error("Unable to load complaint detail from the API. Please try again later.");
}

export function useComplaintDetail(id: string) {
  return useQuery({
    queryKey: ["complaints", "detail", id],
    queryFn: async () => {
      try {
        const res = await complaintsService.getById(id);
        const data = res.data.data ?? res.data;
        if (data && data.title) {
          const detail: ComplaintDetail = {
            id: data.id, complaint_number: data.complaint_number ?? `C-${id.slice(0, 8)}`,
            title: data.title, description: data.description ?? "",
            status: data.status, severity: data.severity, priority: data.priority,
            category: data.category, subcategory: data.subcategory ?? "",
            source: data.source, channel: data.channel ?? data.source,
            insurance_line: (data as any).insurance_line ?? "Motor",
            product_name: (data as any).product_name ?? "Motor Comprehensive Plus",
            policy_number: data.policy_number ?? `POL-${new Date().getFullYear()}-001245`,
            customer_id: data.customer_id ?? "", customer_name: data.customer_name ?? "Unknown",
            customer_email: "", customer_phone: "",
            assigned_agent_name: data.assigned_agent_name ?? "Unassigned",
            assigned_queue: data.assigned_queue ?? "",
            received_time: data.received_time ?? data.created_at,
            sla_status: data.sla_risk ?? "unknown",
            sentiment: data.sentiment ?? "neutral",
            root_cause: data.root_cause ?? "",
            escalation_risk: data.escalation_risk_level ?? "low",
            duplicate_complaint: (data as any).duplicate_complaint ?? false,
            is_repeat: data.is_repeat ?? false,
            is_overdue: (data as any).is_overdue ?? false,
            ai_summary: data.ai_summary ?? "",
            
            // Phase 2 mappings
            product: data.product,
            claim_number: data.claim_number,
            detected_language: data.detected_language,
            theme: data.theme,
            customer_requested_outcome: data.customer_requested_outcome,
            recommendation: data.recommendation,
            sentiment_start: data.sentiment_start,
            sentiment_end: data.sentiment_end,
            contributing_factors: data.contributing_factors,
            sla_risk: data.sla_risk,
            resolution_deadline: data.resolution_deadline,
            sla_breach_probability: data.sla_breach_probability,
            regulatory_flag: data.regulatory_flag,
            acknowledged_time: data.acknowledged_time,
            interaction_id: data.interaction_id,
            assigned_agent_id: data.assigned_agent_id,
            created_at: data.created_at ?? new Date().toISOString(),
            updated_at: data.updated_at ?? new Date().toISOString(),

            ai_insights: { negative_keywords: [], detected_entities: [], topics: [], emotion: "neutral", confidence: 0, risk_score: 0 },
            timeline: [], interactions: [],
            customer: { id: data.customer_id ?? "", name: data.customer_name ?? "Unknown", email: "", phone: "", segment: "", city: "", risk_level: "low", total_complaints: 0, total_interactions: 0, lifetime_value: 0, churn_risk: "low", policies: [] },
            attachments: [], notes: [],
          };
          return detail;
        }
      } catch {}
      return mockDetail(id);
    },
    staleTime: 15_000,
    retry: 1,
    enabled: !!id,
  });
}

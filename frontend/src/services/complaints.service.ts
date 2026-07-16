import { api } from "@/services/api-client";
import type { PaginatedResponse } from "@/types/common";
import type {
  AIOverrideRequest,
  Complaint,
  ComplaintIngestResponse,
  RelatedComplaintSummary,
  SLAStatusResult,
} from "@/types/domain";

export const complaintsService = {
  async list(params?: {
    page?: number;
    page_size?: number;
    status?: string;
    priority?: string;
    search?: string;
    channel?: string;
    theme?: string;
    severity?: string;
    sla_risk?: string;              // FR-007
    is_repeat?: boolean;            // FR-008
    detected_language?: string;     // FR-019
    escalation_risk_min?: number;   // FR-006
    product?: string;               // FR-001
    regulatory_flag?: boolean;      // FR-020
    date_from?: string;
    date_to?: string;
    sort_by?: string;
    sort_dir?: string;
    assigned_to_me?: boolean;
    tab?: string;
  }) {
    return api.get<PaginatedResponse<Complaint>>("/complaints", { params });
  },

  async getById(id: string) {
    return api.get<{ data: Complaint }>(`/complaints/${id}`);
  },

  async create(data: Partial<Complaint>) {
    return api.post<{ data: Complaint }>("/complaints", data);
  },

  async update(id: string, data: Partial<Complaint>) {
    return api.patch<{ data: Complaint }>(`/complaints/${id}`, data);
  },

  async updateStatus(id: string, status: string) {
    return api.patch<{ data: Complaint }>(`/complaints/${id}`, { status });
  },

  // FR-001 — Omnichannel ingestion
  async ingest(data: {
    channel: string;
    customer_id?: string;
    policy_number?: string;
    claim_number?: string;
    product?: string;
    transcript?: string;
    email_body?: string;
    language?: string;
    interaction_id?: string;
  }) {
    return api.post<{ data: ComplaintIngestResponse }>("/complaints/ingest", data);
  },

  // FR-010 — Trigger AI analysis on demand
  async triggerAnalysis(id: string) {
    return api.post<{ data: Complaint }>(`/complaints/${id}/analyze`);
  },

  // FR-020 — Get full AI analysis result
  async getAIAnalysis(id: string) {
    return api.get<{ data: Record<string, unknown> }>(`/complaints/${id}/ai-analysis`);
  },

  // FR-014 — Human override of AI classification
  async applyAIOverride(id: string, override: AIOverrideRequest) {
    return api.post<{ data: Complaint }>(`/complaints/${id}/ai-override`, override);
  },

  // FR-007 — Acknowledge complaint
  async acknowledge(id: string) {
    return api.post<{ data: Complaint }>(`/complaints/${id}/acknowledge`);
  },

  // FR-007 — Real-time SLA status
  async getSLAStatus(id: string) {
    return api.get<{ data: SLAStatusResult }>(`/complaints/${id}/sla-status`);
  },

  // FR-008 — Related/repeat complaints
  async getRelatedComplaints(id: string, limit = 10) {
    return api.get<{ data: RelatedComplaintSummary[] }>(`/complaints/${id}/related`, {
      params: { limit },
    });
  },

  async assign(id: string, agentId: string, queue?: string) {
    return api.post<{ data: Complaint }>(`/complaints/${id}/assign`, {
      agent_id: agentId,
      queue,
    });
  },

  async escalate(id: string) {
    return api.post<{ data: Complaint }>(`/complaints/${id}/escalate`);
  },

  async resolve(id: string, resolutionSummary?: string) {
    return api.post<{ data: Complaint }>(`/complaints/${id}/resolve`, {
      resolution_summary: resolutionSummary,
    });
  },

  async close(id: string, closureReason?: string) {
    return api.post<{ data: Complaint }>(`/complaints/${id}/close`, {
      closure_reason: closureReason,
    });
  },
};

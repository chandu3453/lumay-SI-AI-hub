"use client";

/**
 * Phase2AlertBanner — FR-013
 *
 * Displays Phase 2 real-time AI alert cards directly on the Live Alerts page:
 * - Sentiment Drop alerts (FR-003)
 * - Escalation Risk alerts (FR-006)
 * - SLA Breach alerts (FR-007)
 * - Repeat Complaint alerts (FR-008)
 *
 * Each card has one-click escalate action.
 */

import { useState } from "react";

type AlertType = "sentiment_drop" | "escalation_risk" | "sla_breach" | "repeat_complaint";

interface Phase2Alert {
  id: string;
  type: AlertType;
  severity: "critical" | "high" | "medium";
  complaint_id: string;
  complaint_number: string;
  customer_name: string;
  time: string;
  title: string;
  description: string;
  metadata: Record<string, string | number | boolean>;
  acknowledged: boolean;
}

const MOCK_PHASE2_ALERTS: Phase2Alert[] = [
  {
    id: "p2-001",
    type: "escalation_risk",
    severity: "critical",
    complaint_id: "c-101",
    complaint_number: "CMP-2025-0891",
    customer_name: "Mohammed Al Hinai",
    time: "1m ago",
    title: "🔴 CRITICAL Escalation Risk — Score: 92/100",
    description: "AI detected regulatory threat and legal escalation keywords. Supervisor action required immediately.",
    metadata: { escalation_risk_score: 92, triggers: "regulatory_threat, legal_escalation" },
    acknowledged: false,
  },
  {
    id: "p2-002",
    type: "sla_breach",
    severity: "critical",
    complaint_id: "c-102",
    complaint_number: "CMP-2025-0874",
    customer_name: "Fatima Al Lawati",
    time: "3m ago",
    title: "⏰ SLA Breach Imminent — 95% breach probability",
    description: "Only 0.8h remaining before SLA breach. Claims complaint requires immediate assignment.",
    metadata: { breach_probability: 95, sla_hours_remaining: 0.8 },
    acknowledged: false,
  },
  {
    id: "p2-003",
    type: "sentiment_drop",
    severity: "high",
    complaint_id: "c-103",
    complaint_number: "CMP-2025-0863",
    customer_name: "Sultan Al Khaldi",
    time: "7m ago",
    title: "⚠️ Sentiment Drop — Positive → Very Negative",
    description: "Customer sentiment worsened sharply during the current interaction. Agent intervention recommended.",
    metadata: { sentiment_start: "positive", sentiment_end: "very_negative", sentiment_trend: "declining" },
    acknowledged: false,
  },
  {
    id: "p2-004",
    type: "repeat_complaint",
    severity: "high",
    complaint_id: "c-104",
    complaint_number: "CMP-2025-0851",
    customer_name: "Aisha Al Raisi",
    time: "12m ago",
    title: "🔄 Repeat Complaint — 3 similar complaints in 30 days",
    description: "Customer has filed 3 Claims-related complaints in the past 30 days — indicates a recurring process failure.",
    metadata: { repeat_window_days: 30, prior_complaint_count: 3, theme: "claims" },
    acknowledged: false,
  },
  {
    id: "p2-005",
    type: "sla_breach",
    severity: "medium",
    complaint_id: "c-105",
    complaint_number: "CMP-2025-0842",
    customer_name: "Salim Al Wahaibi",
    time: "18m ago",
    title: "⏱️ SLA At Risk — 82% breach probability",
    description: "Policy & Coverage complaint approaching SLA deadline. 4.2h remaining.",
    metadata: { breach_probability: 82, sla_hours_remaining: 4.2 },
    acknowledged: false,
  },
];

const TYPE_CONFIG: Record<AlertType, { icon: string; label: string; borderColor: string; bgColor: string }> = {
  escalation_risk: { icon: "⚠️", label: "Escalation Risk", borderColor: "#ef4444", bgColor: "#fef2f2" },
  sla_breach:      { icon: "⏰", label: "SLA Breach",      borderColor: "#f97316", bgColor: "#fff7ed" },
  sentiment_drop:  { icon: "💬", label: "Sentiment Drop",  borderColor: "#8b5cf6", bgColor: "#f5f3ff" },
  repeat_complaint:{ icon: "🔄", label: "Repeat Complaint",borderColor: "#f59e0b", bgColor: "#fffbeb" },
};

const SEVERITY_CONFIG: Record<string, { dot: string; label: string }> = {
  critical: { dot: "#ef4444", label: "Critical" },
  high:     { dot: "#f97316", label: "High" },
  medium:   { dot: "#eab308", label: "Medium" },
};

interface Phase2AlertBannerProps {
  onEscalate?: (complaintId: string) => void;
  onViewComplaint?: (complaintId: string) => void;
}

export function Phase2AlertBanner({ onEscalate, onViewComplaint }: Phase2AlertBannerProps) {
  const [alerts, setAlerts] = useState<Phase2Alert[]>(MOCK_PHASE2_ALERTS);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  function acknowledge(id: string) {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, acknowledged: true } : a));
  }

  function dismiss(id: string) {
    setDismissed(prev => new Set([...prev, id]));
  }

  const visible = alerts.filter(a => !dismissed.has(a.id));
  const unacknowledgedCount = visible.filter(a => !a.acknowledged).length;

  if (visible.length === 0) return null;

  return (
    <div id="phase2-alert-banner" style={{ display: "flex", flexDirection: "column", gap: 0 }}>
      {/* Banner header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 10,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "#ef4444",
              boxShadow: "0 0 0 2px #fee2e2",
              animation: "pulse 2s infinite",
            }}
          />
          <span style={{ fontSize: 13, fontWeight: 700, color: "#1e293b" }}>
            AI Real-Time Alerts — Phase 2
          </span>
          <span
            style={{
              fontSize: 10,
              fontWeight: 700,
              color: "#fff",
              background: "#ef4444",
              borderRadius: 99,
              padding: "1px 7px",
            }}
          >
            {unacknowledgedCount} NEW
          </span>
        </div>
        <div style={{ fontSize: 10, color: "#94a3b8" }}>
          FR-013 · Sentiment Drop · Escalation Risk · SLA Breach · Repeat Complaint
        </div>
      </div>

      {/* Alert cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {visible.map((alert) => {
          const typeConf = TYPE_CONFIG[alert.type];
          const sevConf = SEVERITY_CONFIG[alert.severity];

          return (
            <div
              key={alert.id}
              id={`phase2-alert-${alert.id}`}
              style={{
                background: typeConf.bgColor,
                border: `1px solid ${typeConf.borderColor}40`,
                borderLeft: `4px solid ${typeConf.borderColor}`,
                borderRadius: 10,
                padding: "12px 14px",
                display: "flex",
                alignItems: "flex-start",
                gap: 12,
                opacity: alert.acknowledged ? 0.6 : 1,
                transition: "opacity 0.3s ease",
              }}
            >
              {/* Icon */}
              <div style={{ fontSize: 20, flexShrink: 0, marginTop: 2 }}>{typeConf.icon}</div>

              {/* Content */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 4 }}>
                  <span style={{ fontSize: 12, fontWeight: 700, color: "#1e293b" }}>{alert.title}</span>
                  <span
                    style={{
                      fontSize: 10,
                      fontWeight: 600,
                      padding: "1px 6px",
                      borderRadius: 99,
                      background: `${sevConf.dot}18`,
                      color: sevConf.dot,
                    }}
                  >
                    ● {sevConf.label}
                  </span>
                  {alert.acknowledged && (
                    <span style={{ fontSize: 10, color: "#94a3b8" }}>✓ Acknowledged</span>
                  )}
                </div>

                <div style={{ fontSize: 11, color: "#475569", marginBottom: 6 }}>
                  {alert.description}
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 10, color: "#94a3b8" }}>
                  <span>{alert.complaint_number}</span>
                  <span>·</span>
                  <span>{alert.customer_name}</span>
                  <span>·</span>
                  <span>{alert.time}</span>
                </div>
              </div>

              {/* Actions */}
              <div style={{ display: "flex", flexDirection: "column", gap: 4, flexShrink: 0 }}>
                <button
                  id={`alert-escalate-${alert.id}`}
                  onClick={() => {
                    onEscalate?.(alert.complaint_id);
                    acknowledge(alert.id);
                  }}
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    color: "#fff",
                    background: typeConf.borderColor,
                    border: "none",
                    borderRadius: 6,
                    padding: "4px 10px",
                    cursor: "pointer",
                    whiteSpace: "nowrap",
                  }}
                >
                  Escalate ↗
                </button>
                <button
                  id={`alert-view-${alert.id}`}
                  onClick={() => {
                    onViewComplaint?.(alert.complaint_id);
                    acknowledge(alert.id);
                  }}
                  style={{
                    fontSize: 11,
                    fontWeight: 600,
                    color: typeConf.borderColor,
                    background: "transparent",
                    border: `1px solid ${typeConf.borderColor}50`,
                    borderRadius: 6,
                    padding: "4px 10px",
                    cursor: "pointer",
                    whiteSpace: "nowrap",
                  }}
                >
                  View
                </button>
                <button
                  id={`alert-dismiss-${alert.id}`}
                  onClick={() => dismiss(alert.id)}
                  style={{
                    fontSize: 10,
                    color: "#94a3b8",
                    background: "transparent",
                    border: "none",
                    cursor: "pointer",
                    padding: "2px 0",
                  }}
                >
                  Dismiss ✕
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

"use client";

/**
 * AIIntelligencePanel — FR-002 to FR-020
 *
 * Displays the full Phase 2 AI analysis for a complaint:
 * - Complaint Detection badge (FR-002)
 * - Sentiment trend gauge (FR-003)
 * - Theme classification (FR-004)
 * - Escalation risk score ring (FR-006)
 * - SLA breach probability bar (FR-007)
 * - Repeat complaint alert (FR-008)
 * - Language badge (FR-019)
 * - Root cause expandable (FR-016)
 * - AI Explainability (FR-020)
 */

import { useState } from "react";
import type { Complaint } from "@/types/domain";

// ─── Colour utilities ────────────────────────────────────────────────────────

function escalationColor(score: number): string {
  if (score >= 76) return "#ef4444";
  if (score >= 51) return "#f97316";
  if (score >= 26) return "#eab308";
  return "#22c55e";
}

function slaColor(risk: string | null | undefined): string {
  if (risk === "breached") return "#ef4444";
  if (risk === "at_risk") return "#f97316";
  return "#22c55e";
}

function sentimentColor(sentiment: string | null | undefined): string {
  if (sentiment === "very_negative") return "#ef4444";
  if (sentiment === "negative") return "#f97316";
  if (sentiment === "positive") return "#22c55e";
  if (sentiment === "very_positive") return "#16a34a";
  return "#64748b";
}

function sentimentEmoji(sentiment: string | null | undefined): string {
  const map: Record<string, string> = {
    very_positive: "😄",
    positive: "🙂",
    neutral: "😐",
    negative: "😠",
    very_negative: "😡",
  };
  return map[sentiment ?? ""] ?? "😐";
}

function trendArrow(trend: string | null | undefined): string {
  if (trend === "improving") return "↗";
  if (trend === "declining") return "↘";
  if (trend === "volatile") return "↕";
  return "→";
}

function trendColor(trend: string | null | undefined): string {
  if (trend === "improving") return "#22c55e";
  if (trend === "declining") return "#ef4444";
  if (trend === "volatile") return "#f97316";
  return "#64748b";
}

const THEME_LABELS: Record<string, string> = {
  claims: "Claims",
  policy_and_coverage: "Policy & Coverage",
  renewal_and_pricing: "Renewal & Pricing",
  customer_service: "Customer Service",
  provider_and_network: "Provider & Network",
  digital_experience: "Digital Experience",
  financial: "Financial",
};

const THEME_COLORS: Record<string, string> = {
  claims: "#6366f1",
  policy_and_coverage: "#0ea5e9",
  renewal_and_pricing: "#8b5cf6",
  customer_service: "#06b6d4",
  provider_and_network: "#10b981",
  digital_experience: "#f59e0b",
  financial: "#ef4444",
};

const ROOT_CAUSE_LABELS: Record<string, string> = {
  process_failure: "Process Failure",
  system_technical: "System / Technical",
  staff_behaviour: "Staff Behaviour",
  policy_gap: "Policy Gap",
  provider_failure: "Provider Failure",
  customer_expectation: "Customer Expectation",
};

// ─── Sub-components ──────────────────────────────────────────────────────────

function Section({
  title,
  icon,
  children,
  accent,
}: {
  title: string;
  icon: string;
  children: React.ReactNode;
  accent?: string;
}) {
  return (
    <div
      style={{
        background: "#fff",
        border: "1px solid #e2e8f0",
        borderRadius: 10,
        padding: "14px 16px",
        borderLeft: `4px solid ${accent ?? "#6366f1"}`,
      }}
    >
      <div
        style={{
          fontSize: 11,
          fontWeight: 700,
          color: "#94a3b8",
          textTransform: "uppercase",
          letterSpacing: "0.08em",
          marginBottom: 8,
          display: "flex",
          alignItems: "center",
          gap: 6,
        }}
      >
        <span>{icon}</span>
        {title}
      </div>
      {children}
    </div>
  );
}

function Pill({
  label,
  color,
  bg,
}: {
  label: string;
  color: string;
  bg: string;
}) {
  return (
    <span
      style={{
        display: "inline-block",
        fontSize: 11,
        fontWeight: 600,
        padding: "2px 10px",
        borderRadius: 20,
        color,
        background: bg,
      }}
    >
      {label}
    </span>
  );
}

function ScoreRing({
  score,
  color,
  label,
  size = 70,
}: {
  score: number;
  color: string;
  label: string;
  size?: number;
}) {
  const r = (size - 10) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="#f1f5f9"
          strokeWidth={8}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={color}
          strokeWidth={8}
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: "stroke-dasharray 0.6s ease" }}
        />
        <text
          x={size / 2}
          y={size / 2 + 1}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={size * 0.22}
          fontWeight={700}
          fill={color}
        >
          {score}
        </text>
      </svg>
      <span style={{ fontSize: 10, color: "#94a3b8", fontWeight: 600 }}>{label}</span>
    </div>
  );
}

function ProgressBar({
  value,
  color,
  label,
}: {
  value: number;
  color: string;
  label: string;
}) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11 }}>
        <span style={{ color: "#64748b", fontWeight: 500 }}>{label}</span>
        <span style={{ fontWeight: 700, color }}>{value}%</span>
      </div>
      <div
        style={{
          height: 8,
          background: "#f1f5f9",
          borderRadius: 99,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${value}%`,
            background: color,
            borderRadius: 99,
            transition: "width 0.6s ease",
          }}
        />
      </div>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

interface AIIntelligencePanelProps {
  complaint: Complaint;
  onOverrideClick?: () => void;
}

export function AIIntelligencePanel({ complaint, onOverrideClick }: AIIntelligencePanelProps) {
  const [rootCauseExpanded, setRootCauseExpanded] = useState(false);
  const [explanationExpanded, setExplanationExpanded] = useState(false);

  const hasAIData = complaint.detection_type != null || complaint.sentiment != null;

  if (!hasAIData) {
    return (
      <div
        style={{
          background: "#f8fafc",
          border: "1px dashed #cbd5e1",
          borderRadius: 10,
          padding: "24px",
          textAlign: "center",
          color: "#94a3b8",
          fontSize: 13,
        }}
      >
        <div style={{ fontSize: 28, marginBottom: 8 }}>🤖</div>
        <div style={{ fontWeight: 600 }}>AI analysis pending...</div>
        <div style={{ fontSize: 12, marginTop: 4 }}>
          Analysis will run automatically in the background.
        </div>
      </div>
    );
  }

  const escScore = complaint.escalation_risk_score ?? 0;
  const escColor = escalationColor(escScore);
  const slaProb = complaint.sla_breach_probability ?? 0;
  const slaC = slaColor(complaint.sla_risk);
  const themeColor = THEME_COLORS[complaint.theme ?? ""] ?? "#6366f1";

  return (
    <div
      id="ai-intelligence-panel"
      style={{ display: "flex", flexDirection: "column", gap: 10 }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 4,
        }}
      >
        <div
          style={{
            fontSize: 13,
            fontWeight: 700,
            color: "#1e293b",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          <span
            style={{
              width: 28,
              height: 28,
              borderRadius: 8,
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 14,
              color: "#fff",
            }}
          >
            🧠
          </span>
          AI Intelligence — Phase 2
        </div>
        {onOverrideClick && (
          <button
            id="ai-override-btn"
            onClick={onOverrideClick}
            style={{
              fontSize: 11,
              fontWeight: 600,
              color: "#6366f1",
              background: "#eff6ff",
              border: "1px solid #c7d2fe",
              borderRadius: 6,
              padding: "4px 12px",
              cursor: "pointer",
            }}
          >
            ✏️ Override AI
          </button>
        )}
      </div>

      {/* Row 1: Detection + Language */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
        {/* FR-002 Detection */}
        <Section title="Complaint Detection" icon="🔍" accent="#6366f1">
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Pill
              label={
                complaint.detection_type === "definite"
                  ? "✓ Complaint Confirmed"
                  : complaint.detection_type === "possible"
                  ? "⚠ Possible Complaint"
                  : "✗ Not a Complaint"
              }
              color={
                complaint.detection_type === "definite"
                  ? "#16a34a"
                  : complaint.detection_type === "possible"
                  ? "#92400e"
                  : "#64748b"
              }
              bg={
                complaint.detection_type === "definite"
                  ? "#f0fdf4"
                  : complaint.detection_type === "possible"
                  ? "#fefce8"
                  : "#f8fafc"
              }
            />
          </div>
          {complaint.detection_confidence != null && (
            <div style={{ marginTop: 6, fontSize: 11, color: "#94a3b8" }}>
              Confidence: <strong>{Math.round(complaint.detection_confidence * 100)}%</strong>
            </div>
          )}
          {complaint.primary_complaint_statement && (
            <div
              style={{
                marginTop: 8,
                fontSize: 11,
                color: "#475569",
                fontStyle: "italic",
                borderLeft: "2px solid #c7d2fe",
                paddingLeft: 8,
              }}
            >
              "{complaint.primary_complaint_statement}"
            </div>
          )}
        </Section>

        {/* FR-019 Language */}
        <Section title="Language" icon="🌐" accent="#0ea5e9">
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <Pill
              label={
                complaint.detected_language === "ar"
                  ? "🇴🇲 Arabic"
                  : complaint.detected_language === "mixed"
                  ? "🔀 Mixed AR/EN"
                  : "🇬🇧 English"
              }
              color={complaint.detected_language === "ar" ? "#0c4a6e" : "#1e3a5f"}
              bg={complaint.detected_language === "ar" ? "#e0f2fe" : "#eff6ff"}
            />
          </div>
          {complaint.arabic_percentage != null && complaint.arabic_percentage > 0 && (
            <div style={{ marginTop: 8 }}>
              <ProgressBar
                value={complaint.arabic_percentage}
                color="#0ea5e9"
                label="Arabic content"
              />
            </div>
          )}
          {complaint.is_repeat && (
            <div
              style={{
                marginTop: 8,
                background: "#fef3c7",
                border: "1px solid #fcd34d",
                borderRadius: 6,
                padding: "4px 8px",
                fontSize: 11,
                color: "#92400e",
                fontWeight: 600,
              }}
            >
              🔄 Repeat Complaint
              {complaint.repeat_window_days && ` (within ${complaint.repeat_window_days} days)`}
              {complaint.prior_complaint_count && ` — ${complaint.prior_complaint_count} prior`}
            </div>
          )}
        </Section>
      </div>

      {/* Row 2: Sentiment */}
      <Section title="Sentiment Analysis" icon="💬" accent="#8b5cf6">
        <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
          {/* Start */}
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 22 }}>{sentimentEmoji(complaint.sentiment_start)}</div>
            <div style={{ fontSize: 10, color: "#94a3b8" }}>Start</div>
          </div>
          {/* Arrow trend */}
          <div
            style={{
              flex: 1,
              display: "flex",
              alignItems: "center",
              gap: 6,
              minWidth: 80,
            }}
          >
            <div style={{ flex: 1, height: 2, background: "#e2e8f0", borderRadius: 1 }} />
            <div
              style={{
                fontSize: 18,
                fontWeight: 700,
                color: trendColor(complaint.sentiment_trend),
              }}
            >
              {trendArrow(complaint.sentiment_trend)}
            </div>
            <div style={{ flex: 1, height: 2, background: "#e2e8f0", borderRadius: 1 }} />
          </div>
          {/* End */}
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: 22 }}>{sentimentEmoji(complaint.sentiment_end)}</div>
            <div style={{ fontSize: 10, color: "#94a3b8" }}>End</div>
          </div>

          {/* Overall */}
          <div
            style={{
              marginLeft: "auto",
              background: "#f8fafc",
              borderRadius: 8,
              padding: "6px 12px",
              textAlign: "center",
            }}
          >
            <div
              style={{
                fontSize: 11,
                fontWeight: 700,
                color: sentimentColor(complaint.sentiment),
              }}
            >
              {complaint.sentiment?.replace("_", " ")?.toUpperCase() ?? "—"}
            </div>
            <div style={{ fontSize: 10, color: "#94a3b8" }}>Overall</div>
          </div>
        </div>

        {complaint.sentiment_target && (
          <div style={{ marginTop: 8, fontSize: 11, color: "#64748b" }}>
            Target:{" "}
            <strong style={{ color: "#475569" }}>
              {complaint.sentiment_target.replace(/_/g, " ")}
            </strong>
          </div>
        )}
      </Section>

      {/* Row 3: Theme */}
      <Section title="Complaint Theme (FR-004)" icon="🏷️" accent={themeColor}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
          {complaint.theme && (
            <Pill
              label={THEME_LABELS[complaint.theme] ?? complaint.theme}
              color="#fff"
              bg={themeColor}
            />
          )}
          {complaint.theme_secondary?.map((t) => (
            <Pill
              key={t}
              label={THEME_LABELS[t] ?? t}
              color={THEME_COLORS[t] ?? "#64748b"}
              bg={`${THEME_COLORS[t] ?? "#64748b"}20`}
            />
          ))}
        </div>
        {complaint.theme_keywords && complaint.theme_keywords.length > 0 && (
          <div
            style={{
              marginTop: 8,
              display: "flex",
              flexWrap: "wrap",
              gap: 4,
            }}
          >
            {complaint.theme_keywords.map((kw) => (
              <span
                key={kw}
                style={{
                  fontSize: 10,
                  color: "#64748b",
                  background: "#f1f5f9",
                  borderRadius: 4,
                  padding: "1px 6px",
                }}
              >
                {kw}
              </span>
            ))}
          </div>
        )}
      </Section>

      {/* Row 4: Escalation + SLA */}
      <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 10 }}>
        {/* FR-006 Escalation Risk Ring */}
        <Section title="Escalation Risk" icon="⚠️" accent={escColor}>
          <div style={{ display: "flex", justifyContent: "center", paddingTop: 4 }}>
            <ScoreRing score={escScore} color={escColor} label="Risk Score" />
          </div>
          {complaint.escalation_triggers && complaint.escalation_triggers.length > 0 && (
            <div style={{ marginTop: 8 }}>
              {complaint.escalation_triggers.map((t) => (
                <div
                  key={t}
                  style={{
                    fontSize: 10,
                    color: "#dc2626",
                    padding: "1px 0",
                    display: "flex",
                    alignItems: "center",
                    gap: 4,
                  }}
                >
                  <span>⚡</span>
                  {t.replace(/_/g, " ")}
                </div>
              ))}
            </div>
          )}
        </Section>

        {/* FR-007 SLA Breach Risk */}
        <Section title="SLA Breach Risk" icon="⏱️" accent={slaC}>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Pill
                label={
                  complaint.sla_risk === "breached"
                    ? "🔴 Breached"
                    : complaint.sla_risk === "at_risk"
                    ? "🟡 At Risk"
                    : "🟢 Within SLA"
                }
                color={slaC}
                bg={`${slaC}18`}
              />
            </div>
            <ProgressBar
              value={slaProb}
              color={slaC}
              label="Breach probability"
            />
            {complaint.sla_hours_remaining != null && (
              <div style={{ fontSize: 11, color: "#64748b" }}>
                Hours remaining:{" "}
                <strong style={{ color: slaC }}>
                  {complaint.sla_hours_remaining.toFixed(1)}h
                </strong>
              </div>
            )}
          </div>
        </Section>
      </div>

      {/* FR-016 Root Cause */}
      {complaint.root_cause && (
        <Section title="Root Cause Analysis" icon="🔬" accent="#f59e0b">
          <button
            id="root-cause-expand-btn"
            onClick={() => setRootCauseExpanded(!rootCauseExpanded)}
            style={{
              width: "100%",
              background: "none",
              border: "none",
              cursor: "pointer",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              padding: 0,
              textAlign: "left",
            }}
          >
            <div>
              <div
                style={{
                  fontSize: 12,
                  fontWeight: 600,
                  color: "#1e293b",
                }}
              >
                {complaint.root_cause}
              </div>
              {complaint.root_cause_category && (
                <Pill
                  label={ROOT_CAUSE_LABELS[complaint.root_cause_category] ?? complaint.root_cause_category}
                  color="#92400e"
                  bg="#fef3c7"
                />
              )}
            </div>
            <span style={{ color: "#94a3b8", fontSize: 12 }}>
              {rootCauseExpanded ? "▲" : "▼"}
            </span>
          </button>

          {rootCauseExpanded && (
            <div style={{ marginTop: 10 }}>
              {complaint.contributing_factors && complaint.contributing_factors.length > 0 && (
                <div style={{ marginBottom: 8 }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "#94a3b8", marginBottom: 4 }}>
                    CONTRIBUTING FACTORS
                  </div>
                  {complaint.contributing_factors.map((f) => (
                    <div
                      key={f}
                      style={{
                        fontSize: 11,
                        color: "#475569",
                        padding: "2px 0",
                        display: "flex",
                        gap: 6,
                      }}
                    >
                      <span style={{ color: "#f59e0b" }}>•</span>
                      {f}
                    </div>
                  ))}
                </div>
              )}
              {complaint.process_failure_point && (
                <div style={{ fontSize: 11, color: "#64748b" }}>
                  <strong>Failure point:</strong> {complaint.process_failure_point}
                </div>
              )}
            </div>
          )}
        </Section>
      )}

      {/* FR-020 AI Explainability */}
      {complaint.ai_explanation && Object.keys(complaint.ai_explanation).length > 0 && (
        <Section title="AI Explainability" icon="💡" accent="#64748b">
          <button
            id="ai-explanation-expand-btn"
            onClick={() => setExplanationExpanded(!explanationExpanded)}
            style={{
              width: "100%",
              background: "none",
              border: "none",
              cursor: "pointer",
              fontSize: 11,
              color: "#6366f1",
              fontWeight: 600,
              textAlign: "left",
              padding: 0,
            }}
          >
            {explanationExpanded ? "▲ Hide explanations" : "▼ Show why AI made these decisions"}
          </button>
          {explanationExpanded && (
            <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 6 }}>
              {Object.entries(complaint.ai_explanation).map(([key, explanation]) =>
                explanation ? (
                  <div
                    key={key}
                    style={{
                      fontSize: 11,
                      color: "#475569",
                      borderLeft: "2px solid #e2e8f0",
                      paddingLeft: 8,
                    }}
                  >
                    <strong style={{ color: "#1e293b", textTransform: "capitalize" }}>
                      {key.replace(/_/g, " ")}:
                    </strong>{" "}
                    {explanation}
                  </div>
                ) : null
              )}
            </div>
          )}
        </Section>
      )}

      {/* FR-014 Override history badge */}
      {complaint.ai_override_log && complaint.ai_override_log.length > 0 && (
        <div
          style={{
            fontSize: 10,
            color: "#6366f1",
            background: "#eff6ff",
            border: "1px solid #c7d2fe",
            borderRadius: 6,
            padding: "4px 10px",
            display: "inline-flex",
            alignItems: "center",
            gap: 4,
          }}
        >
          ✏️ {complaint.ai_override_log.length} human override
          {complaint.ai_override_log.length > 1 ? "s" : ""} applied
        </div>
      )}
    </div>
  );
}

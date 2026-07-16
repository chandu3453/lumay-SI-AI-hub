"use client";

/**
 * AIOverridePanel — FR-014
 *
 * Allows agents to override AI-generated fields while the original AI values
 * are preserved in the audit log (ai_override_log). Shows diff: AI: X → Override: Y
 */

import { useState } from "react";
import type { Complaint, AIOverrideRequest } from "@/types/domain";

const THEME_OPTIONS = [
  { value: "claims", label: "Claims" },
  { value: "policy_and_coverage", label: "Policy & Coverage" },
  { value: "renewal_and_pricing", label: "Renewal & Pricing" },
  { value: "customer_service", label: "Customer Service" },
  { value: "provider_and_network", label: "Provider & Network" },
  { value: "digital_experience", label: "Digital Experience" },
  { value: "financial", label: "Financial" },
];

const SEVERITY_OPTIONS = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" },
];

const SENTIMENT_OPTIONS = [
  { value: "very_positive", label: "Very Positive" },
  { value: "positive", label: "Positive" },
  { value: "neutral", label: "Neutral" },
  { value: "negative", label: "Negative" },
  { value: "very_negative", label: "Very Negative" },
];

const ROOT_CAUSE_OPTIONS = [
  { value: "process_failure", label: "Process Failure" },
  { value: "system_technical", label: "System / Technical" },
  { value: "staff_behaviour", label: "Staff Behaviour" },
  { value: "policy_gap", label: "Policy Gap" },
  { value: "provider_failure", label: "Provider Failure" },
  { value: "customer_expectation", label: "Customer Expectation" },
];

interface AIOverridePanelProps {
  complaint: Complaint;
  onSubmit?: (override: AIOverrideRequest) => Promise<void>;
  onCancel?: () => void;
}

export function AIOverridePanel({ complaint, onSubmit, onCancel }: AIOverridePanelProps) {
  const [theme, setTheme] = useState(complaint.theme ?? "");
  const [severity, setSeverity] = useState(complaint.severity ?? "");
  const [sentiment, setSentiment] = useState(complaint.sentiment ?? "");
  const [rootCause, setRootCause] = useState(complaint.root_cause ?? "");
  const [rootCauseCategory, setRootCauseCategory] = useState(complaint.root_cause_category ?? "");
  const [overrideReason, setOverrideReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasChanges =
    theme !== (complaint.theme ?? "") ||
    severity !== (complaint.severity ?? "") ||
    sentiment !== (complaint.sentiment ?? "") ||
    rootCause !== (complaint.root_cause ?? "") ||
    rootCauseCategory !== (complaint.root_cause_category ?? "");

  async function handleSubmit() {
    if (!overrideReason.trim() || overrideReason.length < 5) {
      setError("Please provide a reason for the override (min 5 characters).");
      return;
    }
    if (!hasChanges) {
      setError("No changes detected.");
      return;
    }

    const payload: AIOverrideRequest = {
      override_reason: overrideReason,
    };
    if (theme !== (complaint.theme ?? "")) payload.theme = theme;
    if (severity !== (complaint.severity ?? "")) payload.severity = severity;
    if (sentiment !== (complaint.sentiment ?? "")) payload.sentiment = sentiment;
    if (rootCause !== (complaint.root_cause ?? "")) payload.root_cause = rootCause;
    if (rootCauseCategory !== (complaint.root_cause_category ?? ""))
      payload.root_cause_category = rootCauseCategory;

    setSubmitting(true);
    setError(null);
    try {
      await onSubmit?.(payload);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Override failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  function FieldDiff({
    label,
    aiValue,
    newValue,
    hasChange,
  }: {
    label: string;
    aiValue: string;
    newValue: string;
    hasChange: boolean;
  }) {
    if (!hasChange) return null;
    return (
      <div
        style={{
          fontSize: 11,
          color: "#475569",
          display: "flex",
          alignItems: "center",
          gap: 6,
          flexWrap: "wrap",
        }}
      >
        <strong>{label}:</strong>
        <span
          style={{
            padding: "1px 6px",
            background: "#fee2e2",
            color: "#dc2626",
            borderRadius: 4,
            textDecoration: "line-through",
          }}
        >
          {aiValue || "—"}
        </span>
        <span style={{ color: "#94a3b8" }}>→</span>
        <span
          style={{
            padding: "1px 6px",
            background: "#dcfce7",
            color: "#16a34a",
            borderRadius: 4,
          }}
        >
          {newValue || "—"}
        </span>
      </div>
    );
  }

  return (
    <div
      id="ai-override-panel"
      style={{
        background: "#fff",
        border: "1px solid #e2e8f0",
        borderRadius: 12,
        padding: 20,
        display: "flex",
        flexDirection: "column",
        gap: 16,
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ fontSize: 14, fontWeight: 700, color: "#1e293b" }}>
          ✏️ Override AI Classification
        </div>
        <div
          style={{
            fontSize: 11,
            color: "#94a3b8",
            background: "#f8fafc",
            border: "1px solid #e2e8f0",
            borderRadius: 6,
            padding: "3px 8px",
          }}
        >
          FR-014 — Human Override
        </div>
      </div>

      <div
        style={{
          fontSize: 11,
          color: "#64748b",
          background: "#eff6ff",
          borderRadius: 8,
          padding: "8px 12px",
          border: "1px solid #c7d2fe",
        }}
      >
        💡 Original AI values are preserved in the audit log. Only change fields you believe
        are incorrect.
      </div>

      {/* Override fields */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        {/* Theme */}
        <div>
          <label
            style={{ fontSize: 11, fontWeight: 600, color: "#374151", display: "block", marginBottom: 4 }}
          >
            Theme (AI: {complaint.theme?.replace(/_/g, " ") ?? "—"})
          </label>
          <select
            id="override-theme-select"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            style={{
              width: "100%",
              padding: "6px 10px",
              border: "1px solid #d1d5db",
              borderRadius: 6,
              fontSize: 12,
              color: "#1e293b",
              background: "#fff",
            }}
          >
            <option value="">— Keep AI value —</option>
            {THEME_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>

        {/* Severity */}
        <div>
          <label
            style={{ fontSize: 11, fontWeight: 600, color: "#374151", display: "block", marginBottom: 4 }}
          >
            Severity (AI: {complaint.severity ?? "—"})
          </label>
          <select
            id="override-severity-select"
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            style={{
              width: "100%",
              padding: "6px 10px",
              border: "1px solid #d1d5db",
              borderRadius: 6,
              fontSize: 12,
              color: "#1e293b",
              background: "#fff",
            }}
          >
            <option value="">— Keep AI value —</option>
            {SEVERITY_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>

        {/* Sentiment */}
        <div>
          <label
            style={{ fontSize: 11, fontWeight: 600, color: "#374151", display: "block", marginBottom: 4 }}
          >
            Sentiment (AI: {complaint.sentiment?.replace(/_/g, " ") ?? "—"})
          </label>
          <select
            id="override-sentiment-select"
            value={sentiment}
            onChange={(e) => setSentiment(e.target.value)}
            style={{
              width: "100%",
              padding: "6px 10px",
              border: "1px solid #d1d5db",
              borderRadius: 6,
              fontSize: 12,
              color: "#1e293b",
              background: "#fff",
            }}
          >
            <option value="">— Keep AI value —</option>
            {SENTIMENT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>

        {/* Root Cause Category */}
        <div>
          <label
            style={{ fontSize: 11, fontWeight: 600, color: "#374151", display: "block", marginBottom: 4 }}
          >
            Root Cause Category (AI: {complaint.root_cause_category?.replace(/_/g, " ") ?? "—"})
          </label>
          <select
            id="override-root-cause-category-select"
            value={rootCauseCategory}
            onChange={(e) => setRootCauseCategory(e.target.value)}
            style={{
              width: "100%",
              padding: "6px 10px",
              border: "1px solid #d1d5db",
              borderRadius: 6,
              fontSize: 12,
              color: "#1e293b",
              background: "#fff",
            }}
          >
            <option value="">— Keep AI value —</option>
            {ROOT_CAUSE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Root cause text */}
      <div>
        <label
          style={{ fontSize: 11, fontWeight: 600, color: "#374151", display: "block", marginBottom: 4 }}
        >
          Root Cause Description (AI: {complaint.root_cause ?? "—"})
        </label>
        <textarea
          id="override-root-cause-input"
          value={rootCause}
          onChange={(e) => setRootCause(e.target.value)}
          rows={2}
          placeholder="Leave blank to keep AI value..."
          style={{
            width: "100%",
            padding: "8px 10px",
            border: "1px solid #d1d5db",
            borderRadius: 6,
            fontSize: 12,
            color: "#1e293b",
            resize: "vertical",
            boxSizing: "border-box",
          }}
        />
      </div>

      {/* Change diff preview */}
      {hasChanges && (
        <div
          style={{
            background: "#f8fafc",
            border: "1px solid #e2e8f0",
            borderRadius: 8,
            padding: "10px 12px",
            display: "flex",
            flexDirection: "column",
            gap: 6,
          }}
        >
          <div style={{ fontSize: 10, fontWeight: 700, color: "#94a3b8", marginBottom: 4 }}>
            PENDING CHANGES
          </div>
          <FieldDiff
            label="Theme"
            aiValue={complaint.theme?.replace(/_/g, " ") ?? ""}
            newValue={theme.replace(/_/g, " ")}
            hasChange={theme !== (complaint.theme ?? "")}
          />
          <FieldDiff
            label="Severity"
            aiValue={complaint.severity ?? ""}
            newValue={severity}
            hasChange={severity !== (complaint.severity ?? "")}
          />
          <FieldDiff
            label="Sentiment"
            aiValue={complaint.sentiment?.replace(/_/g, " ") ?? ""}
            newValue={sentiment.replace(/_/g, " ")}
            hasChange={sentiment !== (complaint.sentiment ?? "")}
          />
          <FieldDiff
            label="Root Cause"
            aiValue={complaint.root_cause ?? ""}
            newValue={rootCause}
            hasChange={rootCause !== (complaint.root_cause ?? "")}
          />
          <FieldDiff
            label="Root Cause Category"
            aiValue={complaint.root_cause_category?.replace(/_/g, " ") ?? ""}
            newValue={rootCauseCategory.replace(/_/g, " ")}
            hasChange={rootCauseCategory !== (complaint.root_cause_category ?? "")}
          />
        </div>
      )}

      {/* Override reason (required) */}
      <div>
        <label
          style={{ fontSize: 11, fontWeight: 600, color: "#374151", display: "block", marginBottom: 4 }}
        >
          Override Reason <span style={{ color: "#ef4444" }}>*</span>
        </label>
        <textarea
          id="override-reason-input"
          value={overrideReason}
          onChange={(e) => setOverrideReason(e.target.value)}
          rows={2}
          placeholder="Required: Explain why the AI classification is incorrect..."
          style={{
            width: "100%",
            padding: "8px 10px",
            border: `1px solid ${error ? "#ef4444" : "#d1d5db"}`,
            borderRadius: 6,
            fontSize: 12,
            color: "#1e293b",
            resize: "vertical",
            boxSizing: "border-box",
          }}
        />
        <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 2 }}>
          {overrideReason.length}/500 — Minimum 5 characters required
        </div>
      </div>

      {error && (
        <div
          style={{
            fontSize: 12,
            color: "#dc2626",
            background: "#fee2e2",
            borderRadius: 6,
            padding: "6px 10px",
          }}
        >
          {error}
        </div>
      )}

      {/* Actions */}
      <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
        <button
          id="ai-override-cancel-btn"
          onClick={onCancel}
          disabled={submitting}
          style={{
            padding: "8px 16px",
            border: "1px solid #e2e8f0",
            borderRadius: 8,
            background: "#fff",
            color: "#64748b",
            fontSize: 12,
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Cancel
        </button>
        <button
          id="ai-override-submit-btn"
          onClick={handleSubmit}
          disabled={submitting || !hasChanges}
          style={{
            padding: "8px 20px",
            border: "none",
            borderRadius: 8,
            background: hasChanges ? "#6366f1" : "#e2e8f0",
            color: hasChanges ? "#fff" : "#94a3b8",
            fontSize: 12,
            fontWeight: 700,
            cursor: hasChanges ? "pointer" : "not-allowed",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          {submitting ? "Saving..." : "✓ Apply Override"}
        </button>
      </div>
    </div>
  );
}

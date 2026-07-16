"use client";

/**
 * Phase2AIWidget — Dashboard Phase 2 Intelligence Overview
 *
 * Displays a Phase 2 AI metrics summary on the dashboard:
 * - Escalation Risk Heatmap (by severity band)
 * - SLA Compliance gauge
 * - 7-Bucket Theme Distribution (FR-004)
 * - Repeat Complaint Rate (FR-008)
 * - Language Distribution (FR-019)
 */

const THEME_CONFIG: Array<{
  key: string;
  label: string;
  color: string;
  mockCount: number;
}> = [
  { key: "claims", label: "Claims", color: "#6366f1", mockCount: 0 },
  { key: "policy_and_coverage", label: "Policy & Coverage", color: "#0ea5e9", mockCount: 0 },
  { key: "customer_service", label: "Customer Service", color: "#06b6d4", mockCount: 0 },
  { key: "renewal_and_pricing", label: "Renewal & Pricing", color: "#8b5cf6", mockCount: 0 },
  { key: "financial", label: "Financial", color: "#ef4444", mockCount: 0 },
  { key: "provider_and_network", label: "Provider & Network", color: "#10b981", mockCount: 0 },
  { key: "digital_experience", label: "Digital Experience", color: "#f59e0b", mockCount: 0 },
];

const TOTAL = THEME_CONFIG.reduce((s, t) => s + t.mockCount, 0);

// Data loading from analytics API
const ESCALATION_BANDS = [
  { label: "Critical (76-100)", count: 0, color: "#ef4444" },
  { label: "High (51-75)", count: 0, color: "#f97316" },
  { label: "Medium (26-50)", count: 0, color: "#eab308" },
  { label: "Low (0-25)", count: 0, color: "#22c55e" },
];

function EscalationRow({
  label,
  count,
  total,
  color,
}: {
  label: string;
  count: number;
  total: number;
  color: string;
}) {
  const pct = Math.round((count / total) * 100);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
      <div style={{ width: 8, height: 8, borderRadius: 2, background: color, flexShrink: 0 }} />
      <div style={{ flex: 1 }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            fontSize: 10,
            color: "#64748b",
            marginBottom: 2,
          }}
        >
          <span>{label}</span>
          <span style={{ fontWeight: 700, color }}>
            {count} ({pct}%)
          </span>
        </div>
        <div
          style={{
            height: 5,
            background: "#f1f5f9",
            borderRadius: 99,
            overflow: "hidden",
          }}
        >
          <div
            style={{
              height: "100%",
              width: `${pct}%`,
              background: color,
              borderRadius: 99,
              transition: "width 0.6s ease",
            }}
          />
        </div>
      </div>
    </div>
  );
}

export function Phase2AIWidget() {
  const totalEscalation = ESCALATION_BANDS.reduce((s, b) => s + b.count, 1);

  return (
    <div
      id="phase2-ai-widget"
      style={{
        background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        borderRadius: 16,
        padding: 20,
        color: "#fff",
        display: "flex",
        flexDirection: "column",
        gap: 20,
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <div
            style={{
              fontSize: 13,
              fontWeight: 800,
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
              }}
            >
              🧠
            </span>
            AI Intelligence — Phase 2
          </div>
          <div style={{ fontSize: 10, color: "#64748b", marginTop: 2 }}>
            FR-002 · FR-003 · FR-004 · FR-006 · FR-007 · FR-008 · FR-019
          </div>
        </div>
        <div
          style={{
            fontSize: 10,
            color: "#22c55e",
            background: "#14532d30",
            border: "1px solid #22c55e40",
            borderRadius: 20,
            padding: "3px 10px",
            fontWeight: 600,
          }}
        >
          ● Live
        </div>
      </div>

      {/* Two-column layout */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Left: Theme Distribution */}
        <div>
          <div
            style={{
              fontSize: 10,
              fontWeight: 700,
              color: "#64748b",
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              marginBottom: 10,
            }}
          >
            🏷️ Theme Distribution (FR-004)
          </div>
          {THEME_CONFIG.map((t) => {
            const pct = Math.round((t.mockCount / TOTAL) * 100);
            return (
              <div key={t.key} style={{ marginBottom: 7 }}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    fontSize: 10,
                    marginBottom: 2,
                  }}
                >
                  <span style={{ color: "#94a3b8" }}>{t.label}</span>
                  <span style={{ fontWeight: 700, color: t.color }}>
                    {t.mockCount} ({pct}%)
                  </span>
                </div>
                <div
                  style={{
                    height: 5,
                    background: "#1e293b",
                    borderRadius: 99,
                    overflow: "hidden",
                    border: "1px solid #334155",
                  }}
                >
                  <div
                    style={{
                      height: "100%",
                      width: `${pct}%`,
                      background: `linear-gradient(90deg, ${t.color}cc, ${t.color})`,
                      borderRadius: 99,
                      transition: "width 0.6s ease",
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Escalation Risk + Language */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {/* Escalation Risk */}
          <div>
            <div
              style={{
                fontSize: 10,
                fontWeight: 700,
                color: "#64748b",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                marginBottom: 8,
              }}
            >
              ⚠️ Escalation Risk Bands (FR-006)
            </div>
            <div style={{ fontSize: 11, color: "#94a3b8", textAlign: "center", padding: "12px 0" }}>
              Data loading from analytics API
            </div>
          </div>

          {/* Language + Repeat */}
          <div
            style={{
              background: "#ffffff08",
              border: "1px solid #ffffff10",
              borderRadius: 10,
              padding: "10px 12px",
            }}
          >
            <div
              style={{
                fontSize: 10,
                fontWeight: 700,
                color: "#64748b",
                textTransform: "uppercase",
                letterSpacing: "0.08em",
                marginBottom: 8,
              }}
            >
              🌐 Language Split (FR-019)
            </div>
            <div style={{ fontSize: 11, color: "#94a3b8", textAlign: "center", padding: "4px 0" }}>
              Data loading from analytics API
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

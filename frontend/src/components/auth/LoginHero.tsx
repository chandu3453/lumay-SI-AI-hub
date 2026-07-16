/**
 * LoginHero — Left panel for the Login page
 *
 * Deep navy-to-blue gradient background with:
 * - LuMay logo
 * - Headline + description
 * - Pure SVG shield illustration (no PNG, transparent)
 * - Floating icon bubbles
 * - Bottom feature grid
 */

import { Logo } from "@/components/auth/Logo";
import { ShieldSVG } from "@/components/ui/ShieldSVG";
import { Headphones, MessageSquare, Mail, Phone, Sparkles, ShieldCheck } from "lucide-react";

interface BubbleProps {
  icon: React.ReactNode;
  style: React.CSSProperties;
  size?: "sm" | "md";
}

function Bubble({ icon, style, size = "md" }: BubbleProps) {
  const dim = size === "sm" ? 38 : 46;
  return (
    <div
      style={{
        position: "absolute",
        width: dim,
        height: dim,
        borderRadius: "50%",
        background: "rgba(255,255,255,0.15)",
        backdropFilter: "blur(10px)",
        WebkitBackdropFilter: "blur(10px)",
        border: "1px solid rgba(255,255,255,0.25)",
        boxShadow: "0 4px 16px rgba(0,0,0,0.15)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "white",
        zIndex: 20,
        ...style,
      }}
    >
      {icon}
    </div>
  );
}

export function LoginHero() {
  return (
    <div
      className="relative flex h-full flex-col overflow-hidden"
      style={{
        background:
          "linear-gradient(155deg, #0F1F4B 0%, #1a3a8f 40%, #1E40AF 70%, #1D4ED8 100%)",
        padding: "48px 48px 40px",
      }}
    >
      {/* Dot grid texture */}
      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "radial-gradient(circle, rgba(255,255,255,0.06) 1px, transparent 1px)",
          backgroundSize: "24px 24px",
          zIndex: 0,
        }}
      />

      {/* Ambient glow blobs */}
      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          top: -80,
          left: -80,
          width: 340,
          height: 340,
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(96,165,250,0.18) 0%, transparent 70%)",
          zIndex: 0,
        }}
      />
      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          bottom: -80,
          right: -60,
          width: 280,
          height: 280,
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%)",
          zIndex: 0,
        }}
      />

      {/* Logo */}
      <div className="relative z-10">
        <Logo />
      </div>

      {/* Text content */}
      <div className="relative z-10 mt-10 space-y-4">
        <span
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            borderRadius: 99,
            border: "1px solid rgba(255,255,255,0.22)",
            background: "rgba(255,255,255,0.1)",
            padding: "4px 14px",
            fontSize: 10,
            fontWeight: 700,
            letterSpacing: "0.1em",
            color: "rgba(255,255,255,0.85)",
            textTransform: "uppercase",
          }}
        >
          <Sparkles style={{ width: 12, height: 12 }} />
          AI-Powered Insurance Operations
        </span>

        <h1
          style={{
            fontSize: "clamp(1.5rem, 2.2vw, 1.9rem)",
            fontWeight: 900,
            lineHeight: 1.15,
            letterSpacing: "-0.02em",
            color: "#ffffff",
            margin: 0,
          }}
        >
          Intelligent Complaints.
          <br />
          Happier Customers.
          <br />
          Stronger <span style={{ color: "#93C5FD" }}>Insurance.</span>
        </h1>

        <p
          style={{
            fontSize: 13,
            lineHeight: 1.7,
            color: "rgba(255,255,255,0.68)",
            maxWidth: 370,
            margin: 0,
          }}
        >
          LuMay SMART Insurance AI Hub transforms every customer interaction
          into actionable intelligence — real-time detection, sentiment
          analysis, and escalation management.
        </p>
      </div>

      {/* ── Illustration: SVG shield + floating bubbles ── */}
      <div
        className="relative z-10 flex flex-1 items-center justify-center"
        style={{ marginTop: 24 }}
      >
        {/* Container for positioning */}
        <div style={{ position: "relative", width: 280, height: 280 }}>
          {/* Orbit rings */}
          <svg
            width={280}
            height={280}
            viewBox="0 0 280 280"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            style={{ position: "absolute", inset: 0, zIndex: 1 }}
            aria-hidden="true"
          >
            <circle
              cx="140"
              cy="140"
              r="125"
              stroke="rgba(255,255,255,0.12)"
              strokeWidth="1"
              strokeDasharray="4 6"
            />
            <circle
              cx="140"
              cy="140"
              r="90"
              stroke="rgba(255,255,255,0.08)"
              strokeWidth="1"
              strokeDasharray="3 5"
            />
            {/* Connection lines */}
            <line x1="30" y1="50" x2="140" y2="140" stroke="rgba(255,255,255,0.15)" strokeWidth="1" strokeDasharray="3 4" />
            <line x1="250" y1="45" x2="140" y2="140" stroke="rgba(255,255,255,0.15)" strokeWidth="1" strokeDasharray="3 4" />
            <line x1="258" y1="170" x2="140" y2="140" stroke="rgba(255,255,255,0.15)" strokeWidth="1" strokeDasharray="3 4" />
            <line x1="28" y1="208" x2="140" y2="140" stroke="rgba(255,255,255,0.15)" strokeWidth="1" strokeDasharray="3 4" />
          </svg>

          {/* Shield — pure SVG, fully transparent */}
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -55%)",
              zIndex: 10,
            }}
          >
            <ShieldSVG color="#1E40AF" accent="#60A5FA" width={200} height={220} />
          </div>

          {/* Floating bubbles */}
          <Bubble
            icon={<Headphones size={18} />}
            style={{ top: 18, left: 14 }}
            size="md"
          />
          <Bubble
            icon={<MessageSquare size={15} />}
            style={{ top: 24, right: 12 }}
            size="sm"
          />
          <Bubble
            icon={<Phone size={15} />}
            style={{ top: 148, right: 4 }}
            size="sm"
          />
          <Bubble
            icon={<Mail size={18} />}
            style={{ bottom: 46, left: 6 }}
            size="md"
          />
        </div>
      </div>

      {/* Bottom features footer */}
      <div
        className="relative z-10 grid grid-cols-3 gap-3"
        style={{
          borderTop: "1px solid rgba(255,255,255,0.14)",
          paddingTop: 20,
        }}
      >
        {[
          {
            icon: <Sparkles style={{ width: 13, height: 13 }} />,
            label: "AI-Powered",
            desc: "Detect & act in real-time",
          },
          {
            icon: <Headphones style={{ width: 13, height: 13 }} />,
            label: "Omnichannel",
            desc: "Voice, chat, email & more",
          },
          {
            icon: <ShieldCheck style={{ width: 13, height: 13 }} />,
            label: "Enterprise Ready",
            desc: "Secure & compliant",
          },
        ].map((f) => (
          <div key={f.label}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                marginBottom: 3,
              }}
            >
              <div
                style={{
                  width: 24,
                  height: 24,
                  borderRadius: 7,
                  background: "rgba(255,255,255,0.12)",
                  border: "1px solid rgba(255,255,255,0.18)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "#93C5FD",
                  flexShrink: 0,
                }}
              >
                {f.icon}
              </div>
              <span
                style={{ fontSize: 11, fontWeight: 700, color: "#ffffff" }}
              >
                {f.label}
              </span>
            </div>
            <p
              style={{
                fontSize: 10,
                color: "rgba(255,255,255,0.5)",
                lineHeight: 1.4,
                margin: 0,
              }}
            >
              {f.desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

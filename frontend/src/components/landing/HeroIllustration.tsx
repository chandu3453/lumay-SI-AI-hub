/**
 * HeroIllustration — Landing page right-column hero illustration
 *
 * Built entirely in HTML/SVG — no background images.
 * Transparent background, blends seamlessly with the hero gradient.
 *
 * Composition:
 * - Center: Pure SVG shield with gradient, shadow, pedestal
 * - Orbit rings (SVG circles)
 * - Connection lines (SVG paths)
 * - Floating icon bubbles (CSS circles with Lucide icons)
 */

import { ShieldSVG } from "@/components/ui/ShieldSVG";
import { Headphones, MessageSquare, Mail, Phone } from "lucide-react";

interface BubbleProps {
  icon: React.ReactNode;
  style: React.CSSProperties;
  size?: "sm" | "md";
}

function Bubble({ icon, style, size = "md" }: BubbleProps) {
  const dim = size === "sm" ? 44 : 52;
  return (
    <div
      style={{
        position: "absolute",
        width: dim,
        height: dim,
        borderRadius: "50%",
        background: "white",
        boxShadow: "0 6px 24px rgba(0,82,255,0.10), 0 1px 4px rgba(0,0,0,0.06)",
        border: "1px solid rgba(226,232,240,0.8)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "#0052FF",
        zIndex: 20,
        ...style,
      }}
    >
      {icon}
    </div>
  );
}

export function HeroIllustration() {
  const W = 500;
  const H = 500;
  const cx = 250; // center x
  const cy = 240; // center y

  return (
    <div
      style={{
        position: "relative",
        width: W,
        height: H,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        flexShrink: 0,
      }}
    >
      {/* ── Radial glow ── */}
      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          width: 360,
          height: 360,
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(219,234,254,0.55) 0%, rgba(239,246,255,0.2) 55%, transparent 80%)",
          top: cy - 180,
          left: cx - 180,
          zIndex: 0,
        }}
      />

      {/* ── SVG: orbit rings + connection lines ── */}
      <svg
        width={W}
        height={H}
        viewBox={`0 0 ${W} ${H}`}
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ position: "absolute", inset: 0, zIndex: 1 }}
        aria-hidden="true"
      >
        {/* Outer orbit */}
        <circle
          cx={cx}
          cy={cy}
          r={185}
          stroke="#DBEAFE"
          strokeWidth="1"
          strokeDasharray="5 7"
          opacity="0.55"
        />
        {/* Inner orbit */}
        <circle
          cx={cx}
          cy={cy}
          r={125}
          stroke="#EFF6FF"
          strokeWidth="1"
          strokeDasharray="3 5"
          opacity="0.5"
        />
        {/* Lines from bubble centres to shield centre */}
        {/* Top-left headphones bubble is at ~ (80, 100) */}
        <line x1="104" y1="124" x2={cx} y2={cy} stroke="#BFDBFE" strokeWidth="1.2" opacity="0.5" strokeDasharray="3 4" />
        <line x1="80" y1="124" x2={cx} y2={cy} stroke="#BFDBFE" strokeWidth="1.2" opacity="0.5" strokeDasharray="3 4" />
        {/* Top-right chat bubble at ~ (398, 90) */}
        <line x1="398" y1="112" x2={cx} y2={cy} stroke="#BFDBFE" strokeWidth="1.2" opacity="0.5" strokeDasharray="3 4" />
        {/* Right phone bubble at ~ (448, 248) */}
        <line x1="448" y1="248" x2={cx} y2={cy} stroke="#BFDBFE" strokeWidth="1.2" opacity="0.5" strokeDasharray="3 4" />
        {/* Bottom-left mail bubble at ~ (72, 360) */}
        <line x1="96" y1="360" x2={cx} y2={cy} stroke="#BFDBFE" strokeWidth="1.2" opacity="0.5" strokeDasharray="3 4" />
      </svg>

      {/* ── SVG Shield (centered) ── */}
      <div style={{ position: "relative", zIndex: 10 }}>
        <ShieldSVG
          color="#1D4ED8"
          accent="#3B82F6"
          width={220}
          height={240}
        />
      </div>

      {/* ── Floating Bubbles ── */}
      {/* Top-Left: Headphones */}
      <Bubble
        icon={<Headphones size={22} />}
        style={{ top: 98, left: 54 }}
        size="md"
      />
      {/* Top-Right: Chat */}
      <Bubble
        icon={<MessageSquare size={18} />}
        style={{ top: 90, right: 52 }}
        size="sm"
      />
      {/* Right: Phone */}
      <Bubble
        icon={<Phone size={18} />}
        style={{ top: 226, right: 28 }}
        size="sm"
      />
      {/* Bottom-Left: Mail */}
      <Bubble
        icon={<Mail size={20} />}
        style={{ bottom: 126, left: 44 }}
        size="md"
      />
    </div>
  );
}

/**
 * ShieldSVG — Pure SVG illustration of the LuMay AI Shield
 * 
 * Built entirely in code — no PNG background images.
 * Transparent by default, blends perfectly on any background.
 */

interface ShieldSVGProps {
  /** Primary body color of the shield */
  color?: string;
  /** Inner accent / checkmark color */
  accent?: string;
  className?: string;
  width?: number;
  height?: number;
}

export function ShieldSVG({
  color = "#1D4ED8",
  accent = "#60A5FA",
  className = "",
  width = 200,
  height = 220,
}: ShieldSVGProps) {
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 200 220"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <linearGradient id="shieldGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor={accent} />
          <stop offset="100%" stopColor={color} />
        </linearGradient>
        <linearGradient id="shieldHighlight" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="rgba(255,255,255,0.4)" />
          <stop offset="100%" stopColor="rgba(255,255,255,0)" />
        </linearGradient>
        <filter id="shieldShadow" x="-20%" y="-10%" width="140%" height="130%">
          <feDropShadow dx="0" dy="8" stdDeviation="12" floodColor={color} floodOpacity="0.25" />
        </filter>
        <filter id="pedestalShadow">
          <feDropShadow dx="0" dy="4" stdDeviation="8" floodColor="#94A3B8" floodOpacity="0.2" />
        </filter>
      </defs>

      {/* White circular pedestal */}
      <ellipse cx="100" cy="198" rx="58" ry="14" fill="#E2E8F0" filter="url(#pedestalShadow)" />
      <ellipse cx="100" cy="194" rx="56" ry="12" fill="#F8FAFC" />
      <ellipse cx="100" cy="192" rx="54" ry="10" fill="white" />

      {/* Shield body */}
      <path
        d="M100 12 L162 38 L162 95 C162 140 132 172 100 185 C68 172 38 140 38 95 L38 38 Z"
        fill="url(#shieldGrad)"
        filter="url(#shieldShadow)"
      />

      {/* Shield inner border ring */}
      <path
        d="M100 24 L150 46 L150 95 C150 133 126 161 100 173 C74 161 50 133 50 95 L50 46 Z"
        fill="none"
        stroke="rgba(255,255,255,0.3)"
        strokeWidth="2"
      />

      {/* Specular highlight */}
      <path
        d="M100 18 L155 42 L155 85 C155 110 140 133 120 150 C115 128 112 105 112 85 L112 48 Z"
        fill="url(#shieldHighlight)"
        opacity="0.5"
      />

      {/* Checkmark */}
      <path
        d="M74 98 L91 116 L128 76"
        stroke="white"
        strokeWidth="10"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

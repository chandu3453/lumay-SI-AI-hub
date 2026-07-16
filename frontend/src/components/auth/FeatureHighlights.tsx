import { Zap, Radio, Building2 } from "lucide-react";

const HIGHLIGHTS = [
  { label: "AI Powered", icon: Zap },
  { label: "Omnichannel", icon: Radio },
  { label: "Enterprise Ready", icon: Building2 },
];

export function FeatureHighlights() {
  return (
    <div className="flex items-center gap-6">
      {HIGHLIGHTS.map(({ label, icon: Icon }) => (
        <div key={label} className="flex items-center gap-2 text-sm text-[#64748B]">
          <Icon className="h-4 w-4" />
          <span>{label}</span>
        </div>
      ))}
    </div>
  );
}
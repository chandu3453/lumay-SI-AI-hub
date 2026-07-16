import { SlidersHorizontal } from "lucide-react";

type ChannelFilterProps = {
  value: string;
  onChange: (value: string) => void;
};

const channels = [
  { value: "", label: "All Channels" },
  { value: "voice", label: "Voice" },
  { value: "whatsapp", label: "WhatsApp" },
  { value: "email", label: "Email" },
  { value: "in_app", label: "Web Chat" },
  { value: "smart_call", label: "SMART CALL" },
  { value: "crm", label: "CRM" },
  { value: "manual", label: "Manual" },
];

export function ChannelFilter({ value, onChange }: ChannelFilterProps) {
  return (
    <div className="relative inline-block w-44">
      <SlidersHorizontal className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-[#64748B] pointer-events-none" />
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="flex h-10 w-full rounded-xl border border-[#E2E8F0] bg-white pl-10 pr-8 text-xs font-bold text-[#334155] shadow-sm outline-none transition-all focus:border-[#2563EB] cursor-pointer appearance-none"
      >
        {channels.map((ch) => (
          <option key={ch.value} value={ch.value}>
            {ch.label}
          </option>
        ))}
      </select>
      <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-[#64748B]" />
    </div>
  );
}
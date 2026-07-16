import type { ReactNode } from "react";

type ReportCardProps = {
  icon: ReactNode;
  iconBg: string;
  title: string;
  description: string;
  onGenerate: () => void;
};

export function ReportCard({ icon, iconBg, title, description, onGenerate }: ReportCardProps) {
  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm flex flex-col justify-between h-[255px] text-left">
      <div>
        {/* Circular icon container */}
        <div className={`flex h-11 w-11 items-center justify-center rounded-2xl border ${iconBg}`}>
          {icon}
        </div>
        
        {/* Title & Description */}
        <h4 className="text-sm font-extrabold text-[#0F172A] tracking-tight mt-3">{title}</h4>
        <p className="text-[11px] font-semibold text-slate-400 leading-relaxed mt-2">{description}</p>
      </div>

      {/* Text trigger link */}
      <button
        onClick={onGenerate}
        className="text-xs font-bold text-[#0052FF] hover:underline flex items-center gap-1 mt-4 transition-all self-start"
      >
        <span>Generate</span>
        <span>→</span>
      </button>
    </div>
  );
}
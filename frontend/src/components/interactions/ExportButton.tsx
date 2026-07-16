import { Download } from "lucide-react";

type ExportButtonProps = {
  onExport: () => void;
};

export function ExportButton({ onExport }: ExportButtonProps) {
  return (
    <button
      onClick={onExport}
      className="flex h-10 items-center gap-2 rounded-xl border border-[#E2E8F0] bg-white px-4 text-xs font-bold text-[#334155] shadow-sm hover:bg-[#F8FAFC] transition-all"
    >
      <Download className="h-3.5 w-3.5 text-[#64748B]" />
      Export
    </button>
  );
}
import { MessageCircle } from "lucide-react";

type RecentInteractionProps = {
  interaction: any;
  isLoading: boolean;
  onViewAll: () => void;
};

export function RecentInteraction({ onViewAll }: RecentInteractionProps) {
  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm text-left">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-[#0F172A] tracking-tight">Recent Interaction</h3>
        <button
          onClick={onViewAll}
          className="text-xs font-bold text-[#0052FF] hover:underline"
        >
          View All
        </button>
      </div>

      {/* WhatsApp Message Panel */}
      <div className="flex items-start gap-3 rounded-xl border border-slate-100 bg-[#F8FAFC] p-3.5">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-emerald-50 border border-emerald-100 text-[#10B981]">
          <MessageCircle className="h-4.5 w-4.5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs font-bold text-[#0F172A]">WhatsApp Chat</span>
            <span className="text-[10px] font-bold text-slate-400">May 16, 2025 10:24 AM</span>
          </div>
          <p className="text-xs font-semibold text-[#475569] mt-1 leading-relaxed">
            "I am still waiting for my claim update..."
          </p>
        </div>
      </div>
    </div>
  );
}
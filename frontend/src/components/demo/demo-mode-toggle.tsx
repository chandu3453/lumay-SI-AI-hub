"use client";

import { useDemoStore } from "@/stores/demo.store";
import { cn } from "@/lib/cn";
import { Radio, MonitorPlay } from "lucide-react";

export function DemoModeToggle() {
  const enabled = useDemoStore((s) => s.enabled);
  const setEnabled = useDemoStore((s) => s.setEnabled);

  return (
    <button
      onClick={() => setEnabled(!enabled)}
      className={cn(
        "flex items-center gap-2 rounded-xl border px-4 py-2 text-xs font-bold shadow-sm transition-all",
        enabled
          ? "border-emerald-200 bg-emerald-50 text-emerald-700 shadow-emerald-100/50"
          : "border-[#E2E8F0] bg-white text-[#334155] hover:bg-[#F8FAFC]",
      )}
    >
      <MonitorPlay className={cn("h-4 w-4", enabled ? "text-emerald-500" : "text-[#64748B]")} />
      <span>Demo Mode</span>
      <span
        className={cn(
          "ml-1 h-2 w-2 rounded-full",
          enabled ? "bg-emerald-500 shadow-sm shadow-emerald-400" : "bg-[#CBD5E1]",
        )}
      />
    </button>
  );
}

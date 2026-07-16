import { cn } from "@/lib/cn";

export type SeverityTabId = "all" | "high" | "medium" | "low";

type SeverityTabsProps = {
  activeTab: SeverityTabId;
  onTabChange: (tab: SeverityTabId) => void;
  counts?: Record<string, number>;
};

const tabs: { id: SeverityTabId; label: string; dotColor?: string }[] = [
  { id: "all", label: "All (6)" },
  { id: "high", label: "High (2)", dotColor: "bg-red-500" },
  { id: "medium", label: "Medium (2)", dotColor: "bg-amber-500" },
  { id: "low", label: "Low (2)", dotColor: "bg-yellow-400" },
];

export function SeverityTabs({ activeTab, onTabChange }: SeverityTabsProps) {
  return (
    <div className="flex items-center border-b border-[#E2E8F0] w-full sm:w-auto">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "flex items-center gap-2 px-4 py-3.5 text-xs font-bold transition-all relative border-b-2 -mb-[1px]",
              isActive
                ? "border-[#0052FF] text-[#0052FF]"
                : "border-transparent text-[#64748B] hover:text-[#0F172A]"
            )}
          >
            {tab.dotColor && (
              <span className={cn("h-1.5 w-1.5 rounded-full shrink-0", tab.dotColor)} />
            )}
            <span>{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
}
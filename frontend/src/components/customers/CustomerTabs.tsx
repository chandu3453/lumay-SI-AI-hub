import { cn } from "@/lib/cn";

export type CustomerTabId = "overview" | "policies" | "complaints" | "interactions" | "notes";

type CustomerTabsProps = {
  activeTab: CustomerTabId;
  onTabChange: (tab: CustomerTabId) => void;
};

const tabs: { id: CustomerTabId; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "policies", label: "Policies (2)" },
  { id: "complaints", label: "Complaints (5)" },
  { id: "interactions", label: "Interactions (12)" },
  { id: "notes", label: "Notes (3)" },
];

export function CustomerTabs({ activeTab, onTabChange }: CustomerTabsProps) {
  return (
    <div className="flex border-b border-[#E2E8F0] w-full text-left">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "px-4 py-3 text-xs font-bold transition-all relative border-b-2 -mb-[1px]",
              isActive
                ? "border-[#0052FF] text-[#0052FF]"
                : "border-transparent text-[#64748B] hover:text-[#0F172A]"
            )}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
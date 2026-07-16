import { cn } from "@/lib/cn";

export type CaseTabId = "all" | "new" | "acknowledged" | "in_progress" | "pending_review" | "resolved" | "closed" | "escalated" | "overdue";

const TABS: { id: CaseTabId; label: string }[] = [
  { id: "all", label: "All Cases" },
  { id: "new", label: "New" },
  { id: "acknowledged", label: "Acknowledged" },
  { id: "in_progress", label: "In Progress" },
  { id: "pending_review", label: "Pending Review" },
  { id: "resolved", label: "Resolved" },
  { id: "closed", label: "Closed" },
  { id: "escalated", label: "Escalated" },
  { id: "overdue", label: "Overdue" },
];

type ComplaintCaseTabsProps = {
  activeTab: CaseTabId;
  onTabChange: (tab: CaseTabId) => void;
  counts?: Record<string, number>;
};

export function ComplaintCaseTabs({ activeTab, onTabChange }: ComplaintCaseTabsProps) {
  return (
    <div className="flex border-b border-[#E2E8F0] w-full text-left overflow-x-auto">
      {TABS.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "px-4 py-3 text-xs font-bold transition-all relative border-b-2 -mb-[1px] whitespace-nowrap",
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
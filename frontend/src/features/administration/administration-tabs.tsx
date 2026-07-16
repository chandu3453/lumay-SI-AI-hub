import { cn } from "@/lib/cn";

const TABS = [
  { key: "overview", label: "Overview" },
  { key: "categories", label: "Categories & Taxonomy" },
  { key: "sla", label: "SLA & Deadlines" },
  { key: "routing", label: "Routing & Escalation" },
  { key: "users", label: "Users & Roles" },
  { key: "channels", label: "Channels & Sources" },
  { key: "settings", label: "System Settings" },
  { key: "audit", label: "Audit Logs" },
];

type AdministrationTabsProps = {
  active: string;
  onChange: (key: string) => void;
};

export function AdministrationTabs({ active, onChange }: AdministrationTabsProps) {
  return (
    <div className="flex border-b border-[#E2E8F0] w-full text-left overflow-x-auto">
      {TABS.map((tab) => {
        const isActive = active === tab.key;
        return (
          <button
            key={tab.key}
            onClick={() => onChange(tab.key)}
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
import { cn } from "@/lib/cn";

type NotificationsTabsProps = {
  active: string;
  onChange: (key: string) => void;
};

const tabs = [
  { id: "all", label: "All (12)" },
  { id: "unread", label: "Unread (6)" },
  { id: "alerts", label: "Alerts (4)" },
  { id: "case_updates", label: "Case Updates (5)" },
  { id: "sla_deadlines", label: "SLA & Deadlines (2)" },
  { id: "system", label: "System (1)" },
];

export function NotificationsTabs({ active, onChange }: NotificationsTabsProps) {
  return (
    <div className="flex border-b border-[#E2E8F0] w-full text-left overflow-x-auto">
      {tabs.map((tab) => {
        const isActive = active === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
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
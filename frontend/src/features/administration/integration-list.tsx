import { ChevronRight } from "lucide-react";

type IntegrationItem = {
  name: string;
  status: string;
};

const INTEGRATIONS: IntegrationItem[] = [
  { name: "Contact Center (CTI)", status: "Connected" },
  { name: "SMART CALL Platform", status: "Connected" },
  { name: "WhatsApp Business API", status: "Connected" },
  { name: "Email Service (Microsoft 365)", status: "Connected" },
  { name: "CRM System", status: "Connected" },
];

export function IntegrationList() {
  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm text-left">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-50 pb-3 mb-4">
        <h4 className="text-xs font-bold text-[#0F172A] tracking-tight">Integrations & Connectors</h4>
        <button className="text-[10px] font-bold text-[#0052FF] hover:underline">View All</button>
      </div>

      {/* Rows */}
      <div className="divide-y divide-[#F1F5F9] border-b border-[#F1F5F9] mb-4">
        {INTEGRATIONS.map((int) => (
          <div key={int.name} className="flex items-center justify-between py-3 text-xs font-bold">
            <span className="text-[#0F172A]">{int.name}</span>
            <div className="flex items-center gap-2">
              <span className="text-[#10B981] font-bold text-[10px]">{int.status}</span>
              <ChevronRight className="h-4.5 w-4.5 text-[#0052FF]" />
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="flex items-center gap-1.5 text-[10px] font-bold text-[#64748B]">
        <div className="h-1.5 w-1.5 rounded-full bg-[#10B981]" />
        <span>9 of 9 connectors active</span>
      </div>
    </div>
  );
}
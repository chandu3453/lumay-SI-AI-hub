import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Phone, Mail, MessageCircle, MapPin, Calendar, MoreHorizontal } from "lucide-react";
import type { Customer } from "@/types/domain";

type CustomerProfileProps = {
  customer: Customer | null;
  isLoading: boolean;
};

export function CustomerProfile({ customer }: CustomerProfileProps) {
  // If no customer is selected, default to the mockup customer data Mohammed Al Hinai to look high fidelity
  const displayCustomer = (customer as any) || {
    id: "CUST-000198",
    full_name: "Mohammed Al Hinai",
    email: "m.hinai@email.com",
    mobile_number: "+968 9123 4567",
    risk_level: "high",
    customer_since: "Jan 12, 2023",
    city: "Muscat",
    state: "Oman",
    initials: "MH",
  };

  const isHighRisk = displayCustomer.risk_level === "high" || displayCustomer.risk_level === "critical";
  const initials = displayCustomer.initials || displayCustomer.full_name?.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2) || "MH";

  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm text-left">
      {/* Header Profile details row */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-5">
        <div className="flex items-center gap-4">
          <Avatar className="h-14 w-14 rounded-2xl bg-blue-50 text-[#0052FF] font-bold shrink-0 border border-blue-100">
            <AvatarFallback className="rounded-2xl bg-blue-50 text-[#0052FF] text-lg font-bold">
              {initials}
            </AvatarFallback>
          </Avatar>
          
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-base font-extrabold text-[#0F172A] tracking-tight">{displayCustomer.full_name}</h3>
              {isHighRisk && (
                <span className="rounded-lg bg-red-50 border border-red-100 px-2 py-0.5 text-[10px] font-bold text-red-600 capitalize">
                  High Risk
                </span>
              )}
            </div>
            
            <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider mt-0.5">
              <span>{displayCustomer.id}</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3" /> Since {displayCustomer.customer_since || "Jan 12, 2023"}
              </span>
            </div>
          </div>
        </div>

        {/* Action triggers */}
        <div className="flex items-center gap-2">
          <button className="h-9 rounded-xl border border-slate-200 bg-white px-4 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-all shadow-sm">
            View Full Profile
          </button>
          <button className="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-400 hover:text-slate-600 hover:bg-slate-50 transition-all shadow-sm">
            <MoreHorizontal className="h-4.5 w-4.5" />
          </button>
        </div>
      </div>

      {/* Contact information details */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 border-t border-slate-100 pt-4 text-xs font-bold text-slate-500">
        <div className="flex items-center gap-2 truncate">
          <Phone className="h-4 w-4 text-[#94A3B8] shrink-0" />
          <span className="truncate">{displayCustomer.mobile_number || "+968 9123 4567"}</span>
        </div>
        <div className="flex items-center gap-2 truncate">
          <Mail className="h-4 w-4 text-[#94A3B8] shrink-0" />
          <span className="truncate">{displayCustomer.email || "m.hinai@email.com"}</span>
        </div>
        <div className="flex items-center gap-2 truncate">
          <MessageCircle className="h-4 w-4 text-[#10B981] shrink-0" />
          <span>WhatsApp</span>
        </div>
        <div className="flex items-center gap-2 truncate">
          <MapPin className="h-4 w-4 text-[#94A3B8] shrink-0" />
          <span className="truncate">{displayCustomer.city || "Muscat"}, {displayCustomer.state || "Oman"}</span>
        </div>
      </div>
    </div>
  );
}
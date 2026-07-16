"use client";

import { useState } from "react";
import { Download, ShieldCheck, Search, Filter } from "lucide-react";

const SYNTHETIC_POLICIES = [
  { id: "POL-99281-22", name: "Motor Comprehensive", type: "Motor", premium: "OMR 850 /yr", coverage: "Full Coverage", expiry: "15 Mar 2027", status: "Active", icon: "🚗" },
  { id: "POL-44332-22", name: "Medical Elite", type: "Medical", premium: "OMR 1,200 /yr", coverage: "In-patient & Out-patient", expiry: "31 Dec 2026", status: "Active", icon: "❤️" },
  { id: "POL-77112-22", name: "Travel Global", type: "Travel", premium: "OMR 180 /yr", coverage: "Worldwide (excl. US)", expiry: "01 Sep 2026", status: "Active", icon: "✈️" },
  { id: "POL-11928-21", name: "Home Secure", type: "Home", premium: "OMR 350 /yr", coverage: "Property & Contents", expiry: "10 Jan 2027", status: "Active", icon: "🏠" },
  { id: "POL-55092-19", name: "Life Term", type: "Life", premium: "OMR 2,400 /yr", coverage: "OMR 500,000", expiry: "Life", status: "Active", icon: "👨‍👩‍👧" },
  { id: "POL-88210-23", name: "Business Liability", type: "Business", premium: "OMR 5,600 /yr", coverage: "OMR 2,000,000", expiry: "30 Nov 2026", status: "Active", icon: "🏢" }
];

export default function CustomerPoliciesPage() {
  const [searchTerm, setSearchTerm] = useState("");

  const filtered = SYNTHETIC_POLICIES.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    p.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 sm:p-8 space-y-6 animate-fade-in max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-[#0D1B3E]">My Policies</h1>
          <p className="text-sm text-slate-500 mt-1">Manage and view all your active insurance plans.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search policies..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-2 bg-white border border-[#E2E8F0] rounded-xl text-sm focus:outline-none focus:border-[#0052FF]"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-white border border-[#E2E8F0] rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-50 transition-colors">
            <Filter className="h-4 w-4" /> Filter
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map(policy => (
          <div key={policy.id} className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm hover:shadow-xl transition-all flex flex-col justify-between group">
            <div>
              <div className="flex justify-between items-start mb-4">
                <div className="h-12 w-12 rounded-2xl bg-blue-50 flex items-center justify-center text-2xl shadow-inner group-hover:scale-105 transition-transform">{policy.icon}</div>
                <span className="px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-600 border border-emerald-100">
                  {policy.status}
                </span>
              </div>
              <h3 className="text-lg font-black text-[#0D1B3E]">{policy.name}</h3>
              <p className="text-xs text-slate-400 font-mono mt-1">{policy.id}</p>
              
              <div className="mt-6 space-y-3">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-500 font-medium">Insurance Area</span>
                  <span className="font-bold text-[#0D1B3E]">{policy.type}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-500 font-medium">Coverage</span>
                  <span className="font-bold text-[#0D1B3E]">{policy.coverage}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-500 font-medium">Premium</span>
                  <span className="font-bold text-[#0D1B3E]">{policy.premium}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-500 font-medium">Expiry Date</span>
                  <span className="font-bold text-[#0D1B3E]">{policy.expiry}</span>
                </div>
              </div>
            </div>
            
            <div className="mt-8 flex flex-col gap-2">
              <div className="flex gap-2">
                <button className="flex-1 py-2.5 rounded-xl bg-[#0052FF] text-white text-xs font-bold hover:bg-blue-600 transition-colors">
                  View Details
                </button>
                <button className="px-4 py-2.5 rounded-xl border border-[#E2E8F0] text-slate-600 hover:bg-slate-50 transition-colors tooltip tooltip-top" data-tip="Download Policy">
                  <Download className="h-4 w-4" />
                </button>
              </div>
              <button className="w-full py-2.5 rounded-xl border border-blue-200 text-[#0052FF] text-xs font-bold hover:bg-blue-50 transition-colors">
                Renew Policy
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

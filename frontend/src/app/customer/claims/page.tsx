"use client";

import { useState } from "react";
import { Search, Filter, FileText, CheckCircle2, AlertCircle, Clock, UploadCloud, MessageSquare, Eye } from "lucide-react";

const SYNTHETIC_CLAIMS = [
  { id: "CLM-2026-001", type: "Motor", status: "Processing", filed: "28 Jun 2026", amount: "OMR 2,400", officer: "Ahmed S.", progress: 60 },
  { id: "CLM-2026-002", type: "Medical", status: "Approved", filed: "15 May 2026", amount: "OMR 890", officer: "Dr. Laila", progress: 100 },
  { id: "CLM-2026-003", type: "Travel", status: "Open", filed: "12 Jul 2026", amount: "OMR 150", officer: "Pending", progress: 20 },
  { id: "CLM-2025-089", type: "Home", status: "Rejected", filed: "10 Nov 2025", amount: "OMR 4,000", officer: "Salem R.", progress: 100 }
];

export default function CustomerClaimsPage() {
  const [searchTerm, setSearchTerm] = useState("");

  const filtered = SYNTHETIC_CLAIMS.filter(c => 
    c.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.status.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 sm:p-8 space-y-8 animate-fade-in max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-[#0D1B3E]">My Claims</h1>
          <p className="text-sm text-slate-500 mt-1">Track and manage your insurance claims.</p>
        </div>
        <button className="flex items-center gap-2 px-5 py-2.5 bg-[#0052FF] text-white rounded-xl text-sm font-bold hover:bg-blue-600 transition-colors shadow-lg shadow-blue-500/20">
          <FileText className="h-4 w-4" /> File New Claim
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 flex items-center gap-4 shadow-sm">
          <div className="h-10 w-10 rounded-xl bg-blue-50 text-blue-500 flex items-center justify-center"><AlertCircle className="h-5 w-5" /></div>
          <div><p className="text-xl font-black text-[#0D1B3E]">1</p><p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Open Claims</p></div>
        </div>
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 flex items-center gap-4 shadow-sm">
          <div className="h-10 w-10 rounded-xl bg-amber-50 text-amber-500 flex items-center justify-center"><Clock className="h-5 w-5" /></div>
          <div><p className="text-xl font-black text-[#0D1B3E]">1</p><p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Processing</p></div>
        </div>
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 flex items-center gap-4 shadow-sm">
          <div className="h-10 w-10 rounded-xl bg-emerald-50 text-emerald-500 flex items-center justify-center"><CheckCircle2 className="h-5 w-5" /></div>
          <div><p className="text-xl font-black text-[#0D1B3E]">1</p><p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Approved</p></div>
        </div>
        <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 flex items-center gap-4 shadow-sm">
          <div className="h-10 w-10 rounded-xl bg-red-50 text-red-500 flex items-center justify-center"><AlertCircle className="h-5 w-5" /></div>
          <div><p className="text-xl font-black text-[#0D1B3E]">1</p><p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Rejected</p></div>
        </div>
      </div>

      {/* Table Section */}
      <div className="bg-white border border-[#E2E8F0] rounded-[24px] shadow-sm overflow-hidden">
        <div className="p-5 border-b border-[#E2E8F0] flex flex-col sm:flex-row justify-between items-center gap-4 bg-slate-50/50">
          <div className="relative w-full sm:w-72">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search claims..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-white border border-[#E2E8F0] rounded-xl text-sm focus:outline-none focus:border-[#0052FF]"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-white border border-[#E2E8F0] rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-50 transition-colors w-full sm:w-auto justify-center">
            <Filter className="h-4 w-4" /> Filters
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white border-b border-[#E2E8F0]">
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Claim ID</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Insurance Type</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Submitted</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Officer</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Progress</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8F0]">
              {filtered.map((claim) => (
                <tr key={claim.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono font-medium text-[#0D1B3E]">{claim.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-[#0D1B3E]">{claim.type}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                      claim.status === 'Approved' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                      claim.status === 'Rejected' ? 'bg-red-50 text-red-700 border-red-200' :
                      claim.status === 'Processing' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                      'bg-blue-50 text-blue-700 border-blue-200'
                    }`}>
                      {claim.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{claim.filed}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-black text-[#0D1B3E]">{claim.amount}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{claim.officer}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="w-24 bg-slate-100 rounded-full h-1.5 mt-1 relative overflow-hidden">
                      <div 
                        className={`absolute left-0 top-0 h-full rounded-full ${
                          claim.status === 'Approved' ? 'bg-emerald-500' : 
                          claim.status === 'Rejected' ? 'bg-red-500' : 
                          'bg-[#0052FF]'
                        }`} 
                        style={{ width: `${claim.progress}%` }} 
                      />
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors tooltip tooltip-top" data-tip="View Details">
                        <Eye className="h-4 w-4" />
                      </button>
                      <button className="p-1.5 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors tooltip tooltip-top" data-tip="Upload Document">
                        <UploadCloud className="h-4 w-4" />
                      </button>
                      <button className="p-1.5 text-slate-400 hover:text-[#0052FF] hover:bg-blue-50 rounded-lg transition-colors tooltip tooltip-top" data-tip="Chat with Officer">
                        <MessageSquare className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

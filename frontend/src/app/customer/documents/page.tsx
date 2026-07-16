"use client";

import { useState } from "react";
import { Folder, FileText, Download, Eye, UploadCloud, Search, Clock, ShieldCheck, Activity } from "lucide-react";

const FOLDERS = [
  { name: "Policies", count: 4, icon: <ShieldCheck className="h-6 w-6 text-blue-500" />, color: "bg-blue-50" },
  { name: "Claims", count: 2, icon: <Activity className="h-6 w-6 text-emerald-500" />, color: "bg-emerald-50" },
  { name: "Receipts", count: 12, icon: <FileText className="h-6 w-6 text-purple-500" />, color: "bg-purple-50" },
  { name: "Medical Documents", count: 3, icon: <Folder className="h-6 w-6 text-rose-500" />, color: "bg-rose-50" },
  { name: "Garage Estimates", count: 1, icon: <Folder className="h-6 w-6 text-amber-500" />, color: "bg-amber-50" }
];

const RECENT_FILES = [
  { name: "Motor_Policy_Schedule_2026.pdf", folder: "Policies", size: "1.2 MB", date: "15 Mar 2026", version: "v1.0" },
  { name: "Medical_Claim_Receipt_890.pdf", folder: "Claims", size: "850 KB", date: "16 May 2026", version: "v1.0" },
  { name: "Payment_Receipt_PAY001.pdf", folder: "Receipts", size: "420 KB", date: "28 May 2026", version: "v1.0" },
  { name: "Travel_Insurance_Terms.pdf", folder: "Policies", size: "2.4 MB", date: "01 Sep 2025", version: "v2.1" }
];

export default function CustomerDocumentsPage() {
  const [searchTerm, setSearchTerm] = useState("");

  return (
    <div className="p-6 sm:p-8 space-y-8 animate-fade-in max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-[#0D1B3E]">Document Vault</h1>
          <p className="text-sm text-slate-500 mt-1">Securely manage your policies, claims documents, and receipts.</p>
        </div>
        <button className="flex items-center gap-2 px-5 py-2.5 bg-[#0052FF] text-white rounded-xl text-sm font-bold hover:bg-blue-600 transition-colors shadow-lg shadow-blue-500/20">
          <UploadCloud className="h-4 w-4" /> Upload Document
        </button>
      </div>

      {/* Folders Grid */}
      <div>
        <h2 className="text-sm font-bold text-[#0D1B3E] mb-4">Folders</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {FOLDERS.map((f, i) => (
            <button key={i} className="bg-white border border-[#E2E8F0] rounded-[20px] p-5 shadow-sm hover:shadow-md transition-all flex flex-col items-center text-center group">
              <div className={`h-14 w-14 rounded-2xl ${f.color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}>
                {f.icon}
              </div>
              <h3 className="text-sm font-bold text-[#0D1B3E]">{f.name}</h3>
              <p className="text-xs text-slate-400 mt-1">{f.count} files</p>
            </button>
          ))}
        </div>
      </div>

      {/* Recent Files */}
      <div className="bg-white border border-[#E2E8F0] rounded-[24px] shadow-sm overflow-hidden mt-8">
        <div className="p-5 border-b border-[#E2E8F0] flex flex-col sm:flex-row justify-between items-center gap-4 bg-slate-50/50">
          <h2 className="text-base font-bold text-[#0D1B3E] flex items-center gap-2">
            <Clock className="h-4 w-4 text-blue-500" /> Recent Files
          </h2>
          <div className="relative w-full sm:w-72">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search files..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-white border border-[#E2E8F0] rounded-xl text-sm focus:outline-none focus:border-[#0052FF]"
            />
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[#E2E8F0]">
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">File Name</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Folder</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Size</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Created</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8F0]">
              {RECENT_FILES.map((file, i) => (
                <tr key={i} className="hover:bg-slate-50/50 transition-colors group">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <FileText className="h-5 w-5 text-slate-400 group-hover:text-blue-500 transition-colors" />
                      <div>
                        <p className="text-sm font-bold text-[#0D1B3E]">{file.name}</p>
                        <p className="text-[10px] text-slate-400 font-mono mt-0.5">{file.version}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-xs font-medium px-2.5 py-1 bg-slate-100 text-slate-600 rounded-lg">{file.folder}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{file.size}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{file.date}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition-colors tooltip tooltip-top" data-tip="Preview">
                        <Eye className="h-4 w-4" />
                      </button>
                      <button className="p-2 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-xl transition-colors tooltip tooltip-top" data-tip="Download">
                        <Download className="h-4 w-4" />
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

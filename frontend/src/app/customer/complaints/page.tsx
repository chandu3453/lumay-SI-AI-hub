"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/http";
import { AlertCircle, ChevronRight, Search, ShieldAlert, Plus, Filter, ArrowUpDown } from "lucide-react";
import RaiseComplaintModal from "@/components/RaiseComplaintModal";
import { useCustomerSession } from "@/features/customer/use-customer-session";

type ComplaintItem = {
  id: string;
  complaint_number: string | null;
  title: string;
  category: string;
  status: string;
  priority: string;
  assigned_queue: string | null;
  created_at: string;
  updated_at?: string;
  ai_summary?: string;
};

const STATUS_COLORS: Record<string, string> = {
  submitted: "bg-slate-100 text-slate-700 border-slate-200",
  under_review: "bg-blue-50 text-blue-700 border-blue-200",
  investigating: "bg-amber-50 text-amber-700 border-amber-200",
  escalated: "bg-red-50 text-red-700 border-red-200",
  resolved: "bg-emerald-50 text-emerald-700 border-emerald-200",
  closed: "bg-slate-100 text-slate-500 border-slate-200",
};

const PRIORITY_COLORS: Record<string, string> = {
  low: "text-slate-500",
  medium: "text-amber-500",
  high: "text-orange-500",
  critical: "text-red-500",
};

export default function CustomerComplaintsPage() {
  const session = useCustomerSession();
  const [complaints, setComplaints] = useState<ComplaintItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [activeStatus, setActiveStatus] = useState<string>("all");
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchComplaints = async () => {
    if (!session) return;
    try {
      setLoading(true);
      const res = await api.get(`/complaints?page_size=50&customer_id=${session.id}`);
      const list = res.data?.data || [];
      setComplaints(list.sort((a: ComplaintItem, b: ComplaintItem) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()));
    } catch {
      setError("Failed to load complaints.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchComplaints(); }, [session]);

  const filtered = complaints.filter((c) => {
    const matchesSearch = !search || c.title?.toLowerCase().includes(search.toLowerCase()) || c.complaint_number?.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = activeStatus === "all" || 
                          (activeStatus === "open" && ["submitted", "under_review", "investigating"].includes(c.status)) ||
                          (activeStatus === "resolved" && ["resolved", "closed"].includes(c.status)) ||
                          c.status === activeStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="p-6 sm:p-8 space-y-6 animate-fade-in max-w-5xl mx-auto h-full flex flex-col">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-[#0D1B3E]">My Complaints</h1>
          <p className="text-sm text-slate-500 mt-1">Track and manage all your insurance complaints.</p>
        </div>
        <button onClick={() => setIsModalOpen(true)} className="h-11 px-5 rounded-xl bg-[#0052FF] text-white text-sm font-bold flex items-center gap-2 hover:bg-blue-600 transition-all shadow-md hover:shadow-lg shadow-blue-500/20 shrink-0">
          <Plus className="h-4 w-4" /> Raise Complaint
        </button>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-center bg-white p-4 rounded-2xl border border-[#E2E8F0] shadow-sm">
        <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto pb-2 sm:pb-0 scrollbar-hide">
          {[
            { id: "all", label: "All" },
            { id: "open", label: "Open" },
            { id: "investigating", label: "In Progress" },
            { id: "resolved", label: "Resolved" },
            { id: "closed", label: "Closed" }
          ].map((status) => (
            <button
              key={status.id}
              onClick={() => setActiveStatus(status.id)}
              className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
                activeStatus === status.id 
                  ? "bg-[#0D1B3E] text-white shadow-md" 
                  : "bg-slate-50 text-slate-600 hover:bg-slate-100 border border-transparent hover:border-slate-200"
              }`}
            >
              {status.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input type="text" placeholder="Search by number or title..." value={search} onChange={(e) => setSearch(e.target.value)} className="w-full pl-10 pr-4 h-10 rounded-xl border border-[#E2E8F0] bg-slate-50 text-sm focus:outline-none focus:border-[#0052FF] focus:bg-white transition-all font-medium placeholder:text-slate-400" />
          </div>
          <button className="h-10 px-3 rounded-xl border border-[#E2E8F0] bg-slate-50 text-slate-500 hover:bg-white hover:border-[#0052FF] hover:text-[#0052FF] transition-all flex items-center gap-2">
            <Filter className="h-4 w-4" />
          </button>
          <button className="h-10 px-3 rounded-xl border border-[#E2E8F0] bg-slate-50 text-slate-500 hover:bg-white hover:border-[#0052FF] hover:text-[#0052FF] transition-all flex items-center gap-2">
            <ArrowUpDown className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="text-center py-16 text-sm text-slate-400 flex flex-col items-center gap-3">
            <div className="h-6 w-6 rounded-full border-2 border-[#0052FF] border-t-transparent animate-spin"></div>
            Loading complaints...
          </div>
        ) : error ? (
          <div className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-600"><AlertCircle className="h-4 w-4" />{error}</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20 bg-white border border-[#E2E8F0] rounded-3xl border-dashed">
            <ShieldAlert className="h-12 w-12 mx-auto text-slate-300 mb-3" />
            <p className="text-sm font-bold text-slate-400">No complaints found</p>
            <p className="text-xs text-slate-300 mt-1">Try adjusting your filters or raise a new complaint.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filtered.map((c) => (
              <Link key={c.id} href={`/customer/complaints/${c.id}`} className="block bg-white border border-[#E2E8F0] rounded-3xl p-5 hover:shadow-lg hover:border-blue-300 transition-all group relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1.5 h-full bg-gradient-to-b from-blue-400 to-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <div className="flex flex-col sm:flex-row gap-5 items-start justify-between">
                  <div className="flex items-start gap-4 min-w-0 flex-1">
                    <div className="h-12 w-12 rounded-2xl bg-blue-50 flex items-center justify-center text-xl shrink-0 border border-blue-100 shadow-inner group-hover:bg-blue-100 transition-colors">
                      {c.category === "claims" ? "📋" : c.category === "billing" ? "💳" : c.category === "motor" ? "🚗" : c.category === "medical" ? "🏥" : "📌"}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-3 flex-wrap">
                        <span className="text-xs font-mono font-bold text-[#0052FF] bg-blue-50 px-2 py-0.5 rounded-md">{c.complaint_number || "PENDING"}</span>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{c.category}</span>
                      </div>
                      <p className="text-base font-black text-[#0D1B3E] mt-1.5 truncate group-hover:text-[#0052FF] transition-colors">{c.title}</p>
                      
                      {c.ai_summary && (
                        <p className="text-xs text-slate-500 mt-2 line-clamp-1 bg-slate-50 p-2 rounded-lg border border-slate-100">{c.ai_summary}</p>
                      )}
                      
                      <div className="flex items-center gap-4 mt-3 flex-wrap">
                        <div className="flex items-center gap-1.5">
                          <span className="h-2 w-2 rounded-full bg-slate-300"></span>
                          <span className="text-[10px] font-bold text-slate-500">Created: {new Date(c.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</span>
                        </div>
                        {c.assigned_queue && (
                          <div className="flex items-center gap-1.5">
                            <span className="h-2 w-2 rounded-full bg-indigo-300"></span>
                            <span className="text-[10px] font-bold text-slate-500 capitalize">{c.assigned_queue}</span>
                          </div>
                        )}
                        <div className="flex items-center gap-1.5">
                          <span className={`h-2 w-2 rounded-full ${PRIORITY_COLORS[c.priority || 'medium']?.split(' ')[0].replace('text', 'bg')} bg-amber-400`}></span>
                          <span className="text-[10px] font-bold text-slate-500 capitalize">{c.priority || 'Medium'} Priority</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex sm:flex-col items-center sm:items-end justify-between w-full sm:w-auto gap-3 shrink-0 pl-16 sm:pl-0 border-t sm:border-t-0 border-[#E2E8F0] pt-3 sm:pt-0 mt-2 sm:mt-0">
                    <span className={`text-[11px] font-bold px-3 py-1.5 rounded-full border capitalize shadow-sm ${STATUS_COLORS[c.status] || "bg-slate-100 text-slate-700"}`}>
                      {c.status.replace(/_/g, " ")}
                    </span>
                    <div className="flex items-center gap-1 text-[#0052FF] text-xs font-bold opacity-0 group-hover:opacity-100 transition-opacity translate-x-2 group-hover:translate-x-0">
                      View Details <ChevronRight className="h-4 w-4" />
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      <RaiseComplaintModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        customerId={session?.id}
        onSuccess={() => {
          fetchComplaints();
        }}
      />
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "@/lib/http";
import {
  Bell, ChevronRight, CreditCard, FileText, Mail,
  MessageSquare, Phone, RefreshCw, ShieldCheck, AlertCircle,
  Clock, DollarSign, Calendar, Download, LogOut,
  Activity, Sparkles, PlusCircle, Search, X, Loader2, Send,
  Home, FileDigit, Settings, Bot, ArrowUpRight,
  User, CheckCircle2, PhoneCall, HelpCircle, UserCircle, Hexagon
} from "lucide-react";

type CustomerSession = { email: string; name: string };
type InteractionItem = { id: string; channel: string; subject: string; status: string; created_at: string; customer_ref?: string };
type ComplaintItem = { id: string; complaint_number: string | null; title: string; status: string; severity: string; created_at: string };
type NotificationItem = { id: string; notification_type: string; subject: string; message: string; notification_status: string; created_at: string | null; notification_channel: string };

export default function CustomerDashboardPage() {
  const router = useRouter();
  const [session, setSession] = useState<CustomerSession | null>(null);
  const [interactions, setInteractions] = useState<InteractionItem[]>([]);
  const [complaints, setComplaints] = useState<ComplaintItem[]>([]);
  const [aiInput, setAiInput] = useState("");

  const [showRaiseModal, setShowRaiseModal] = useState(false);
  const [raiseMessage, setRaiseMessage] = useState("");
  const [raiseChannel, setRaiseChannel] = useState("web_form");
  const [raising, setRaising] = useState(false);
  const [raiseError, setRaiseError] = useState("");
  const [raiseResult, setRaiseResult] = useState<{ interaction_id?: string; complaint_id?: string; workflow_id?: string } | null>(null);

  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

  useEffect(() => {
    const s = sessionStorage.getItem("customer-session") || localStorage.getItem("customer-session");
    if (!s) { router.push("/customer/login"); return; }
    setSession(JSON.parse(s));
    fetchData();
  }, [router]);

  const fetchData = async () => {
    try {
      const [intRes, compRes, notifRes] = await Promise.allSettled([
        api.get("/interactions?page_size=10"),
        api.get("/complaints?page_size=20"),
        api.get("/notifications?page_size=10"),
      ]);
      if (intRes.status === "fulfilled") setInteractions(intRes.value.data?.data?.slice(0, 5) || []);
      if (compRes.status === "fulfilled") setComplaints(compRes.value.data?.data || []);
      if (notifRes.status === "fulfilled") setNotifications(notifRes.value.data?.data?.slice(0, 10) || []);
    } catch {}
  };

  const handleRaiseComplaint = async () => {
    if (!raiseMessage.trim()) return;
    setRaising(true);
    setRaiseError("");
    setRaiseResult(null);
    try {
      const startRes = await api.post("/interactions/conversations/start", { customer_ref: session?.email, channel: raiseChannel });
      const intId = startRes.data?.data?.id;
      if (!intId) { throw new Error("Failed to start conversation"); }
      const msgRes = await api.post("/interactions/conversations/message", { interaction_id: intId, message: raiseMessage });
      const payload = msgRes.data?.data;
      setRaiseResult({
        interaction_id: intId,
        complaint_id: payload?.complaint_id || undefined,
        workflow_id: payload?.workflow_id || undefined,
      });
      await fetchData();
    } catch (err: any) {
      setRaiseError(err?.response?.data?.detail || err?.response?.data?.message || "Failed to submit complaint.");
    } finally {
      setRaising(false);
    }
  };

  const handleAiChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (aiInput.trim()) {
      router.push("/customer/communication/chat");
    }
  };

  if (!session) return null;

  return (
    <div className="p-6 sm:p-8 space-y-8 animate-fade-in">
      
      {/* Welcome & KPIs row */}
      <div className="flex flex-col xl:flex-row gap-6">
        <div className="flex-1 flex flex-col justify-center">
          <h1 className="text-2xl font-black text-[#0D1B3E]">Good morning, {session.name.split(" ")[0]}!</h1>
          <h2 className="text-lg font-bold text-[#0D1B3E] mt-2">Welcome back to LuMay Insurance</h2>
          <p className="text-sm text-slate-500 mt-1">We're here to protect what matters most to you.</p>
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 flex-1">
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-4 flex gap-4 items-center shadow-sm hover:shadow-md transition-shadow">
            <div className="h-10 w-10 rounded-full bg-blue-50 text-blue-500 flex items-center justify-center shrink-0"><ShieldCheck className="h-5 w-5" /></div>
            <div><p className="text-xs font-semibold text-slate-500">Interactions</p><p className="text-xl font-black text-[#0D1B3E]">{interactions.length}</p><p className="text-[10px] text-slate-400">From backend API</p></div>
          </div>
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-4 flex gap-4 items-center shadow-sm hover:shadow-md transition-shadow">
            <div className="h-10 w-10 rounded-full bg-amber-50 text-amber-500 flex items-center justify-center shrink-0"><FileText className="h-5 w-5" /></div>
            <div><p className="text-xs font-semibold text-slate-500">Complaints</p><p className="text-xl font-black text-[#0D1B3E]">{complaints.length}</p><p className="text-[10px] text-slate-400">From backend API</p></div>
          </div>
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-4 flex gap-4 items-center shadow-sm hover:shadow-md transition-shadow">
            <div className="h-10 w-10 rounded-full bg-purple-50 text-purple-500 flex items-center justify-center shrink-0"><Bell className="h-5 w-5" /></div>
            <div><p className="text-xs font-semibold text-slate-500">Notifications</p><p className="text-xl font-black text-[#0D1B3E]">{notifications.length}</p><p className="text-[10px] text-slate-400">From backend API</p></div>
          </div>
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-4 flex gap-4 items-center shadow-sm hover:shadow-md transition-shadow">
            <div className="h-10 w-10 rounded-full bg-emerald-50 text-emerald-500 flex items-center justify-center shrink-0"><Bot className="h-5 w-5" /></div>
            <div><p className="text-xs font-semibold text-slate-500">LuMay AI</p><p className="text-xl font-black text-emerald-600">Online</p><p className="text-[10px] text-slate-400">Ready to assist</p></div>
          </div>
        </div>
      </div>

      {/* Hero & Quick Actions row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* AI Hero */}
        <div className="xl:col-span-2 relative overflow-hidden rounded-[24px] bg-gradient-to-r from-[#0d1b3e] to-[#0038ff] p-8 text-white shadow-xl flex flex-col justify-center min-h-[300px]">
          <div className="absolute top-0 right-0 opacity-20 pointer-events-none">
            <svg width="400" height="300" viewBox="0 0 400 300" fill="none"><path d="M0 300C100 200 300 300 400 100" stroke="white" strokeWidth="2" /><path d="M0 250C150 150 250 250 400 50" stroke="white" strokeWidth="2" /><path d="M0 200C200 100 200 200 400 0" stroke="white" strokeWidth="2" /></svg>
          </div>
          <div className="relative z-10 flex gap-6 items-center mb-6">
            <div className="h-20 w-20 bg-white/10 rounded-2xl backdrop-blur flex items-center justify-center shrink-0 border border-white/20">
              <Bot className="h-10 w-10 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-blue-200">Your AI Insurance Assistant</h3>
              <h2 className="text-3xl sm:text-4xl font-black mt-1">How can I help you today?</h2>
              <p className="text-sm text-blue-100 mt-2">Ask me anything about your policies, claims, payments or coverage.</p>
            </div>
          </div>
          <form onSubmit={handleAiChatSubmit} className="relative z-10">
            <div className="relative flex items-center bg-white rounded-full p-1.5 pl-6 shadow-lg">
              <input 
                type="text" 
                placeholder="Type your question here..." 
                value={aiInput}
                onChange={(e) => setAiInput(e.target.value)}
                className="flex-1 bg-transparent border-none text-[#0D1B3E] text-sm focus:outline-none placeholder-slate-400"
              />
              <button type="submit" className="h-10 w-10 rounded-full bg-[#0052FF] flex items-center justify-center text-white hover:bg-blue-600 transition-colors shrink-0">
                <Send className="h-4 w-4 ml-0.5" />
              </button>
            </div>
          </form>
          <div className="relative z-10 mt-5 flex flex-wrap gap-2">
            {["Track my claim", "Renew policy", "Download policy", "Check coverage", "Request refund"].map((chip, idx) => (
              <button key={idx} onClick={() => { setAiInput(chip); router.push("/customer/communication/chat"); }} className="text-[11px] font-semibold border border-white/30 rounded-full px-4 py-1.5 hover:bg-white/10 transition-colors flex items-center gap-1.5">
                <CheckCircle2 className="h-3 w-3" /> {chip}
              </button>
            ))}
          </div>
        </div>

        {/* Quick Actions Grid */}
        <div className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm flex flex-col justify-center">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-[#0D1B3E]">Quick Actions</h3>
            <Link href="#" className="text-xs text-blue-600 font-bold hover:underline">View All</Link>
          </div>
          <div className="grid grid-cols-4 gap-3">
            <Link href="/customer/communication/chat" className="flex flex-col items-center gap-2 group">
              <div className="h-12 w-12 rounded-2xl bg-blue-50 text-blue-500 flex items-center justify-center group-hover:scale-105 transition-transform"><MessageSquare className="h-5 w-5" /></div>
              <span className="text-[10px] font-bold text-center leading-tight">Chat with AI</span>
            </Link>
            <Link href="/customer/communication/voice" className="flex flex-col items-center gap-2 group">
              <div className="h-12 w-12 rounded-2xl bg-green-50 text-green-500 flex items-center justify-center group-hover:scale-105 transition-transform"><PhoneCall className="h-5 w-5" /></div>
              <span className="text-[10px] font-bold text-center leading-tight">Voice Support</span>
            </Link>
            <Link href="/customer/communication/whatsapp" className="flex flex-col items-center gap-2 group">
              <div className="h-12 w-12 rounded-2xl bg-emerald-50 text-emerald-500 flex items-center justify-center group-hover:scale-105 transition-transform"><MessageSquare className="h-5 w-5" /></div>
              <span className="text-[10px] font-bold text-center leading-tight">WhatsApp</span>
            </Link>
            <Link href="/customer/communication/email" className="flex flex-col items-center gap-2 group">
              <div className="h-12 w-12 rounded-2xl bg-purple-50 text-purple-500 flex items-center justify-center group-hover:scale-105 transition-transform"><Mail className="h-5 w-5" /></div>
              <span className="text-[10px] font-bold text-center leading-tight">Email Support</span>
            </Link>
            <button onClick={() => setShowRaiseModal(true)} className="flex flex-col items-center gap-2 group">
              <div className="h-12 w-12 rounded-2xl bg-red-50 text-red-500 flex items-center justify-center group-hover:scale-105 transition-transform"><PlusCircle className="h-5 w-5" /></div>
              <span className="text-[10px] font-bold text-center leading-tight">Raise Complaint</span>
            </button>
            <Link href="/customer/claims" className="flex flex-col items-center gap-2 group">
              <div className="h-12 w-12 rounded-2xl bg-blue-50 text-blue-500 flex items-center justify-center group-hover:scale-105 transition-transform"><Search className="h-5 w-5" /></div>
              <span className="text-[10px] font-bold text-center leading-tight">Track Complaint</span>
            </Link>
            <Link href="/customer/renewals" className="flex flex-col items-center gap-2 group">
              <div className="h-12 w-12 rounded-2xl bg-emerald-50 text-emerald-500 flex items-center justify-center group-hover:scale-105 transition-transform"><RefreshCw className="h-5 w-5" /></div>
              <span className="text-[10px] font-bold text-center leading-tight">Renew Policy</span>
            </Link>
            <Link href="/customer/documents" className="flex flex-col items-center gap-2 group">
              <div className="h-12 w-12 rounded-2xl bg-indigo-50 text-indigo-500 flex items-center justify-center group-hover:scale-105 transition-transform"><Download className="h-5 w-5" /></div>
              <span className="text-[10px] font-bold text-center leading-tight">Download Policy</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Third Row: Complaints, Interactions, Notifications */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* Complaints Summary Widget */}
        <div className="xl:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-[#0D1B3E]">My Complaints</h3>
            <Link href="/customer/complaints" className="text-xs text-[#0052FF] font-bold hover:underline flex items-center gap-1">View All <ChevronRight className="h-3 w-3" /></Link>
          </div>
          <div className="bg-white border border-[#E2E8F0] rounded-3xl p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="grid grid-cols-3 gap-4 mb-6 pb-6 border-b border-[#E2E8F0]">
              <div className="text-center">
                <p className="text-3xl font-black text-[#0D1B3E]">{complaints.filter(c => ['submitted', 'under_review', 'investigating'].includes(c.status)).length}</p>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mt-1">Open</p>
              </div>
              <div className="text-center border-l border-r border-[#E2E8F0]">
                <p className="text-3xl font-black text-amber-500">{complaints.filter(c => c.status === 'escalated').length}</p>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mt-1">Pending/Escalated</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-black text-emerald-500">{complaints.filter(c => ['resolved', 'closed'].includes(c.status)).length}</p>
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mt-1">Resolved</p>
              </div>
            </div>
            
            {complaints.length > 0 ? (
              <div>
                <p className="text-xs font-bold text-slate-500 mb-3">Latest Complaint</p>
                <Link href={`/customer/complaints/${complaints[0].id}`} className="block group">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-blue-50 flex items-center justify-center border border-blue-100 group-hover:bg-blue-100 transition-colors">
                        <AlertCircle className="h-5 w-5 text-[#0052FF]" />
                      </div>
                      <div>
                        <p className="text-sm font-bold text-[#0D1B3E] group-hover:text-[#0052FF] transition-colors">{complaints[0].title}</p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-[10px] font-mono text-slate-500">{complaints[0].complaint_number || 'PENDING'}</span>
                          <span className="text-[10px] text-slate-300">•</span>
                          <span className="text-[10px] text-slate-500">{new Date(complaints[0].created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                    <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-amber-50 text-amber-600 capitalize">{complaints[0].status.replace(/_/g, ' ')}</span>
                  </div>
                </Link>
              </div>
            ) : (
              <div className="text-center py-4">
                <p className="text-sm text-slate-400">No complaints found.</p>
              </div>
            )}
            
            <div className="mt-6">
              <Link href="/customer/complaints" className="w-full h-11 bg-slate-50 border border-[#E2E8F0] rounded-xl flex items-center justify-center text-sm font-bold text-slate-600 hover:bg-slate-100 hover:text-[#0052FF] hover:border-blue-200 transition-all gap-2">
                <PlusCircle className="h-4 w-4" /> Raise New Complaint
              </Link>
            </div>
          </div>
        </div>

        {/* Interactions (from real API) */}
        <div className="space-y-4 xl:col-span-1">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-[#0D1B3E]">Recent Interactions</h3>
            <Link href="/customer/communication" className="text-xs text-blue-600 font-bold hover:underline">View All</Link>
          </div>
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm space-y-4">
            {interactions.slice(0, 5).map((intItem, idx) => (
              <div key={idx} className="border-b border-slate-100 last:border-0 pb-4 last:pb-0">
                <div className="flex gap-3">
                  <div className="h-10 w-10 rounded-full bg-slate-50 flex items-center justify-center shrink-0">
                    {intItem.channel === "voice" ? <Phone className="h-4 w-4" /> : 
                     intItem.channel === "whatsapp" ? <MessageSquare className="h-4 w-4" /> : 
                     intItem.channel === "email" ? <Mail className="h-4 w-4" /> : <MessageSquare className="h-4 w-4" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-bold text-[#0D1B3E] truncate">{intItem.subject || "Communication"}</h4>
                    <p className="text-[10px] text-slate-400">{intItem.channel} · {intItem.created_at ? new Date(intItem.created_at).toLocaleDateString() : ""}</p>
                    <span className="text-[9px] font-bold px-2 py-0.5 rounded mt-1 inline-block bg-slate-100 text-slate-600">{intItem.status}</span>
                  </div>
                </div>
              </div>
            ))}
            {interactions.length === 0 && (
              <p className="text-xs text-slate-400 text-center py-4">No interactions yet.</p>
            )}
          </div>
        </div>

        {/* Notifications (from real API) */}
        <div className="space-y-4 xl:col-span-1">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-[#0D1B3E]">Notifications</h3>
            <Link href="/customer/notifications" className="text-xs text-blue-600 font-bold hover:underline">View All</Link>
          </div>
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm space-y-4">
            {notifications.slice(0, 5).map((notif, idx) => (
              <div key={idx} className="flex gap-3 border-b border-slate-100 last:border-0 pb-4 last:pb-0">
                <div className="h-8 w-8 rounded-full bg-blue-50 flex items-center justify-center shrink-0 text-blue-500">
                  <Bell className="h-4 w-4" />
                </div>
                <div className="min-w-0">
                  <p className="text-[11px] text-slate-700 font-medium leading-tight truncate">{notif.subject || notif.message}</p>
                  <p className="text-[9px] text-slate-400 mt-1">{notif.created_at ? new Date(notif.created_at).toLocaleDateString() : ""}</p>
                  <span className="text-[8px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 uppercase">{notif.notification_status}</span>
                </div>
              </div>
            ))}
            {notifications.length === 0 && (
              <p className="text-xs text-slate-400 text-center py-4">No notifications yet.</p>
            )}
          </div>
        </div>
      </div>

      {/* Fourth Row: Recent Activity from real API */}
      <div className="grid grid-cols-1 gap-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-[#0D1B3E]">Recent Activity</h3>
          </div>
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm relative">
            <div className="absolute left-9 top-8 bottom-8 w-px bg-slate-100" />
            <div className="space-y-6 relative z-10">
              {interactions.slice(0, 6).map((act, idx) => (
                <div key={idx} className="flex gap-4 items-start">
                  <div className="h-8 w-8 rounded-full bg-blue-50 text-blue-500 flex items-center justify-center shrink-0 border-2 border-white shadow-sm">
                    {act.channel === "voice" ? <Phone className="h-4 w-4" /> : 
                     act.channel === "whatsapp" ? <MessageSquare className="h-4 w-4" /> : 
                     act.channel === "email" ? <Mail className="h-4 w-4" /> : <MessageSquare className="h-4 w-4" />}
                  </div>
                  <div className="pt-1.5">
                    <p className="text-xs font-medium text-[#0D1B3E] leading-tight">{act.subject || "Communication"} via {act.channel}</p>
                    <p className="text-[10px] text-slate-400 mt-0.5">{act.created_at ? new Date(act.created_at).toLocaleString() : ""}</p>
                  </div>
                </div>
              ))}
              {interactions.length === 0 && complaints.length === 0 && notifications.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-sm text-slate-400">No activity yet. Start by chatting with LuMay AI or filing a complaint.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Raise Complaint Modal */}
      {showRaiseModal && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4" onClick={() => !raising && setShowRaiseModal(false)}>
          <div className="bg-white rounded-[24px] shadow-2xl w-full max-w-lg p-6 space-y-5 animate-fade-up" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-black text-[#0D1B3E] flex items-center gap-2"><AlertCircle className="h-5 w-5 text-red-500" /> Raise a Complaint</h2>
              <button onClick={() => setShowRaiseModal(false)} className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors"><X className="h-5 w-5 text-slate-400" /></button>
            </div>

            {raiseResult ? (
              <div className="space-y-4">
                <div className="flex items-center gap-3 rounded-xl bg-emerald-50 border border-emerald-200 p-4 text-sm text-emerald-800"><span className="h-8 w-8 rounded-full bg-emerald-100 flex items-center justify-center text-lg">✅</span><div><p className="font-bold">Complaint Submitted Successfully</p><p className="text-xs text-emerald-600 mt-0.5">AI analysis completed. Auto-triage initiated.</p></div></div>
                <div className="text-xs space-y-2 bg-slate-50 rounded-xl p-4">
                  {raiseResult.interaction_id && <p className="font-mono text-slate-500"><span className="font-bold text-slate-700">Interaction:</span> {raiseResult.interaction_id}</p>}
                  {raiseResult.complaint_id && <p className="font-mono text-slate-500"><span className="font-bold text-slate-700">Complaint:</span> {raiseResult.complaint_id}</p>}
                  {raiseResult.workflow_id && <p className="font-mono text-slate-500"><span className="font-bold text-slate-700">Workflow:</span> {raiseResult.workflow_id}</p>}
                </div>
                <div className="flex gap-3">
                  <button onClick={() => { setShowRaiseModal(false); router.push("/customer/claims"); }} className="flex-1 py-2.5 rounded-xl bg-[#0052FF] text-white text-sm font-bold hover:bg-blue-600 transition-colors">Track Complaint</button>
                  <button onClick={() => { setRaiseResult(null); setRaiseMessage(""); setRaiseError(""); }} className="flex-1 py-2.5 rounded-xl border border-[#E2E8F0] text-sm font-bold text-slate-600 hover:bg-slate-50 transition-colors">Raise Another</button>
                </div>
              </div>
            ) : (
              <>
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Channel</label>
                  <div className="grid grid-cols-4 gap-2">
                    {[{ value: "web_form", label: "💬 Chat" }, { value: "whatsapp", label: "🟢 WhatsApp" }, { value: "voice", label: "📞 Voice" }, { value: "email", label: "📧 Email" }].map((ch) => (
                      <button key={ch.value} onClick={() => setRaiseChannel(ch.value)} className={`py-2 rounded-xl text-xs font-bold border transition-colors ${raiseChannel === ch.value ? "bg-[#0052FF] text-white border-[#0052FF]" : "bg-white text-slate-600 border-[#E2E8F0] hover:border-blue-200"}`}>{ch.label}</button>
                    ))}
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Describe Your Issue</label>
                  <textarea placeholder="Tell us what happened... (e.g., My motor claim has been delayed for 18 days)" value={raiseMessage} onChange={(e) => setRaiseMessage(e.target.value)} rows={4} className="w-full border border-[#E2E8F0] rounded-xl p-3 text-sm focus:outline-none focus:border-[#0052FF] resize-none" />
                </div>
                {raiseError && <div className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-600"><AlertCircle className="h-4 w-4 shrink-0" /><span className="font-medium">{raiseError}</span></div>}
                <button onClick={handleRaiseComplaint} disabled={raising || !raiseMessage.trim()} className="flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-red-500 text-sm font-bold text-white shadow-md hover:bg-red-600 transition-all disabled:opacity-50">
                  {raising ? <><Loader2 className="h-4 w-4 animate-spin" /> Submitting...</> : <><Send className="h-4 w-4" /> Submit Complaint</>}
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import { useState, useEffect } from "react";
import { Bell, CheckCircle2, AlertCircle, FileText, CreditCard, ShieldCheck, Search, Trash2 } from "lucide-react";
import { api } from "@/services/api-client";

const TYPE_LABEL_MAP: Record<string, string> = {
  alert: "Alerts",
  reminder: "Reminders",
  confirmation: "Confirmations",
  status_update: "Updates",
  escalation: "Escalations",
  resolution: "Resolutions",
};

function getTypeLabel(raw: string): string {
  return TYPE_LABEL_MAP[raw?.toLowerCase()] || raw || "Other";
}

export default function CustomerNotificationsPage() {
  const [activeTab, setActiveTab] = useState("All");
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/notifications?page_size=50")
      .then((res) => setNotifications(res.data?.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = notifications.filter(n => {
    if (activeTab === "Unread") return n.notification_status === "pending" || n.notification_status === "queued";
    if (activeTab !== "All" && getTypeLabel(n.notification_type) !== activeTab) return false;
    return true;
  });

  return (
    <div className="p-6 sm:p-8 space-y-8 animate-fade-in max-w-4xl mx-auto">
      <div className="flex flex-col justify-center text-center mb-8">
        <div className="h-16 w-16 bg-blue-50 text-[#0052FF] rounded-3xl flex items-center justify-center mx-auto mb-4">
          <Bell className="h-8 w-8" />
        </div>
        <h1 className="text-2xl font-black text-[#0D1B3E]">Notifications</h1>
        <p className="text-sm text-slate-500 mt-1">Stay updated with your latest policy alerts and messages.</p>
      </div>

      <div className="bg-white border border-[#E2E8F0] rounded-[24px] shadow-sm overflow-hidden">
        {/* Tabs */}
        <div className="flex overflow-x-auto border-b border-[#E2E8F0] p-2 bg-slate-50/50">
          {["All", ...new Set(notifications.map(n => getTypeLabel(n.notification_type)))].concat(loading ? [] : ["Unread"]).map(tab => (
            <button 
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-2.5 rounded-xl text-sm font-bold transition-colors whitespace-nowrap ${
                activeTab === tab 
                  ? "bg-white text-[#0052FF] shadow-sm border border-[#E2E8F0]" 
                  : "text-slate-500 hover:text-[#0D1B3E] hover:bg-slate-100"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* List */}
        <div className="divide-y divide-[#E2E8F0]">
          {loading ? (
            <div className="p-12 text-center text-slate-500">
              <p className="text-sm font-medium">Loading notifications...</p>
            </div>
          ) : filtered.length === 0 ? (
            <div className="p-12 text-center text-slate-500">
              <p className="text-sm font-medium">No notifications in this category.</p>
            </div>
          ) : (
            filtered.map((notif) => {
              const isUnread = notif.notification_status === "pending" || notif.notification_status === "queued";
              const timeAgo = notif.created_at ? new Date(notif.created_at).toLocaleDateString() : "N/A";
              return (
                <div key={notif.id} className={`p-5 flex gap-4 transition-colors hover:bg-slate-50 ${isUnread ? "bg-blue-50/20" : ""}`}>
                  <div className="h-10 w-10 rounded-xl bg-blue-50 flex items-center justify-center shrink-0">
                    {notif.notification_type === "alert" || notif.notification_type === "escalation" ? (
                      <AlertCircle className="h-5 w-5 text-red-500" />
                    ) : notif.notification_type === "resolution" || notif.notification_type === "confirmation" ? (
                      <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                    ) : notif.notification_type === "reminder" ? (
                      <ShieldCheck className="h-5 w-5 text-amber-500" />
                    ) : (
                      <FileText className="h-5 w-5 text-purple-500" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-1">
                      <h4 className={`text-sm ${isUnread ? 'font-black text-[#0D1B3E]' : 'font-bold text-slate-700'}`}>
                        {notif.subject}
                      </h4>
                      <span className="text-xs text-slate-400 font-medium">{timeAgo}</span>
                    </div>
                    <p className="text-xs text-slate-500 leading-relaxed max-w-2xl">{notif.message}</p>

                    {isUnread && (
                      <div className="mt-4 flex items-center gap-3">
                        <button className="text-[11px] font-bold text-[#0052FF] hover:underline">
                          View Details
                        </button>
                        <span className="text-slate-300">•</span>
                        <button className="text-[11px] font-bold text-slate-500 hover:text-[#0D1B3E]">
                          Mark as Read
                        </button>
                      </div>
                    )}
                  </div>
                  <div className="flex items-start">
                    <button className="p-2 text-slate-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

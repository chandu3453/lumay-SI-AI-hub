"use client";

import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { MessageCircle, Phone, Mail, MessageSquare, HelpCircle, ArrowLeft, Clock } from "lucide-react";

import { useCustomerSession } from "@/features/customer/use-customer-session";
import { conversationsService } from "@/services/conversations.service";
import type { ConversationSummary } from "@/features/conversations/types";

const CHANNEL_ICON: Record<string, React.ReactNode> = {
  web_chat: <MessageSquare className="h-5 w-5 text-blue-500" />,
  voice: <Phone className="h-5 w-5 text-emerald-500" />,
  whatsapp: <MessageCircle className="h-5 w-5 text-[#25D366]" />,
  email: <Mail className="h-5 w-5 text-purple-500" />,
};

const CHANNEL_ROUTE: Record<string, string> = {
  web_chat: "/customer/communication/chat",
  voice: "/customer/communication/voice",
  whatsapp: "/customer/communication/whatsapp",
  email: "/customer/communication/email",
};

const STATUS_LABEL: Record<string, string> = {
  new: "New", active: "Active", waiting_for_customer: "Waiting on you",
  waiting_for_agent: "Waiting on agent", ai_handling: "AI handling",
  human_handling: "With an agent", escalated: "Escalated", resolved: "Resolved", closed: "Closed",
};

function useCustomerConversationHistory(customerId: string | undefined) {
  return useQuery({
    queryKey: ["customer-conversation-history", customerId],
    queryFn: async () => {
      if (!customerId) return [];
      const res = await conversationsService.list({ customer_id: customerId, page_size: 20 });
      return (res.data.data ?? []) as ConversationSummary[];
    },
    enabled: !!customerId,
  });
}

export default function CustomerConversationHistoryPage() {
  const router = useRouter();
  const session = useCustomerSession();
  const { data: conversations = [], isLoading } = useCustomerConversationHistory(session?.id);

  return (
    <div className="p-6 sm:p-8 space-y-6 animate-fade-in max-w-3xl mx-auto">
      <button
        onClick={() => router.push("/customer/communication")}
        className="inline-flex items-center gap-1.5 text-sm font-semibold text-slate-500 hover:text-[#0052FF] transition-colors"
      >
        <ArrowLeft className="h-4 w-4" /> Back to Communication
      </button>

      <div>
        <h1 className="text-2xl font-black text-[#0D1B3E]">Conversation History</h1>
        <p className="text-sm text-slate-500 mt-1">Every conversation you've had with us, across every channel.</p>
      </div>

      <div className="space-y-3">
        {isLoading ? (
          <p className="text-sm text-slate-400 text-center py-12">Loading your conversations…</p>
        ) : conversations.length === 0 ? (
          <div className="bg-white border border-[#E2E8F0] rounded-2xl p-10 text-center">
            <MessageSquare className="h-8 w-8 text-slate-300 mx-auto mb-3" />
            <p className="text-sm font-semibold text-slate-500">No conversations yet.</p>
            <p className="text-xs text-slate-400 mt-1">Start a chat, WhatsApp, or email conversation and it will show up here.</p>
          </div>
        ) : (
          conversations.map((c) => (
            <button
              key={c.id}
              onClick={() => router.push(CHANNEL_ROUTE[c.current_channel] ?? "/customer/communication/chat")}
              className="w-full text-left bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all flex items-start gap-4"
            >
              <div className="h-11 w-11 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center shrink-0">
                {CHANNEL_ICON[c.current_channel] ?? <HelpCircle className="h-5 w-5 text-slate-400" />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-bold text-[#0D1B3E] capitalize">{c.current_channel.replace("_", " ")}</span>
                  <span className="text-[11px] font-bold text-slate-400 flex items-center gap-1 shrink-0">
                    <Clock className="h-3 w-3" /> {new Date(c.updated_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1 truncate">{c.last_message_preview ?? "No messages yet."}</p>
                <span className="inline-block mt-2 text-[10px] font-bold uppercase tracking-wider text-[#0052FF] bg-blue-50 rounded-full px-2 py-0.5">
                  {STATUS_LABEL[c.current_status] ?? c.current_status}
                </span>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
}

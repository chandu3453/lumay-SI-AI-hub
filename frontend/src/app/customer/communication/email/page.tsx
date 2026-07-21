"use client";

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Send, Paperclip, Mail, CheckCircle2, Inbox, Star, Clock, FileText, Trash2, MoreVertical, Reply, Forward, Printer } from "lucide-react";
import { interactionsService } from "@/services/interactions.service";
import { useCustomerSession } from "@/features/customer/use-customer-session";

interface ChatMessage { role: string; content: string; timestamp: string; }

export default function CustomerEmailPage() {
  const session = useCustomerSession();
  const firstName = session?.name?.split(" ")[0] ?? "there";
  const customerName = session?.name ?? "Customer";
  const customerEmail = session?.email ?? "";
  const customerInitials = customerName.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [interactionId, setInteractionId] = useState<string | null>(null);
  const [textInput, setTextInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!session) return;
    startSession();
  }, [session]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const startSession = async () => {
    try {
      const res = await interactionsService.start(session?.email, "email");
      const dbInt = res.data?.data;
      if (dbInt) {
        setInteractionId(dbInt.id);
        setMessages([{ role: "assistant", content: `Subject: Welcome to LuMay Insurance Support\n\nDear ${firstName},\n\nWelcome to LuMay Insurance email support. We have received your inquiry.\n\nOur team is dedicated to providing you with the best possible service. How can we assist you today?\n\nBest regards,\nLuMay Auto-Responder Engine\nLuMay Insurance Co.`, timestamp: new Date().toISOString() }]);
      }
    } catch (err) { console.error("Failed to start Email:", err); }
  };

  const handleSend = async (text: string) => {
    if (!text.trim() || !interactionId) return;
    setMessages(prev => [...prev, { role: "user", content: text, timestamp: new Date().toISOString() }]);
    setTextInput(""); setIsSending(true);
    try {
      const res = await interactionsService.sendMessage(interactionId, text);
      const payload = res.data?.data;
      setIsSending(false);
      if (payload) setMessages(prev => [...prev, { role: "assistant", content: `Subject: Re: Your Inquiry\n\nDear ${firstName},\n\n${payload.answer}\n\nBest regards,\nLuMay Support Team`, timestamp: new Date().toISOString() }]);
    } catch (err) { setIsSending(false); }
  };

  return (
    <div className="h-full w-full flex bg-[#F8FAFC] animate-fade-in">
      
      {/* Email Sidebar (Folders) */}
      <div className="w-56 bg-[#F3F4F6] border-r border-[#E5E7EB] p-4 flex flex-col hidden lg:flex">
        <button className="w-full bg-[#0052FF] text-white rounded-xl py-2.5 font-bold text-sm shadow-sm hover:bg-blue-600 transition-all mb-6">
          Compose
        </button>
        <div className="space-y-1">
          <div className="flex items-center gap-3 px-3 py-2 bg-blue-100 text-blue-700 rounded-lg cursor-pointer">
            <Inbox className="h-4 w-4" />
            <span className="text-sm font-bold">Inbox</span>
            <span className="ml-auto text-[10px] font-bold">1</span>
          </div>
          <div className="flex items-center gap-3 px-3 py-2 text-slate-600 hover:bg-slate-200 rounded-lg cursor-pointer">
            <Star className="h-4 w-4" />
            <span className="text-sm font-medium">Starred</span>
          </div>
          <div className="flex items-center gap-3 px-3 py-2 text-slate-600 hover:bg-slate-200 rounded-lg cursor-pointer">
            <Clock className="h-4 w-4" />
            <span className="text-sm font-medium">Snoozed</span>
          </div>
          <div className="flex items-center gap-3 px-3 py-2 text-slate-600 hover:bg-slate-200 rounded-lg cursor-pointer">
            <Send className="h-4 w-4" />
            <span className="text-sm font-medium">Sent</span>
          </div>
          <div className="flex items-center gap-3 px-3 py-2 text-slate-600 hover:bg-slate-200 rounded-lg cursor-pointer">
            <FileText className="h-4 w-4" />
            <span className="text-sm font-medium">Drafts</span>
          </div>
        </div>
      </div>

      {/* Email List (Inbox) */}
      <div className="w-80 bg-white border-r border-[#E5E7EB] flex flex-col shrink-0">
        <div className="h-16 border-b border-[#E5E7EB] px-4 flex items-center justify-between shrink-0">
          <h2 className="text-lg font-black text-[#0D1B3E]">Inbox</h2>
        </div>
        <div className="flex-1 overflow-y-auto">
          <div className="p-4 border-b border-[#E5E7EB] bg-blue-50/50 cursor-pointer relative">
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#0052FF]"></div>
            <div className="flex justify-between items-baseline mb-1">
              <h3 className="text-sm font-bold text-[#0D1B3E]">LuMay Support</h3>
              <span className="text-[11px] font-bold text-blue-600">10:45 AM</span>
            </div>
            <p className="text-xs font-bold text-[#0D1B3E] mb-1">Welcome to LuMay Insurance</p>
            <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
              Dear {firstName}, Welcome to LuMay Insurance email support. We have received your inquiry...
            </p>
          </div>
          
          {/* Read Email Content */}
          <div className="p-4 border-b border-[#E5E7EB] cursor-pointer hover:bg-slate-50">
            <div className="flex justify-between items-baseline mb-1">
              <h3 className="text-sm font-medium text-[#0D1B3E]">Policy Renewals</h3>
              <span className="text-[11px] text-slate-400">Yesterday</span>
            </div>
            <p className="text-xs text-[#0D1B3E] mb-1 truncate">Action Required: Motor Policy</p>
            <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
              This is a reminder that your comprehensive motor policy is expiring next month. Please review...
            </p>
          </div>
        </div>
      </div>

      {/* Email Body */}
      <div className="flex-1 flex flex-col bg-white">
        {/* Toolbar */}
        <div className="h-16 px-6 border-b border-[#E5E7EB] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-4">
            <button className="text-slate-400 hover:text-slate-600"><Trash2 className="h-4 w-4" /></button>
            <button className="text-slate-400 hover:text-slate-600"><Printer className="h-4 w-4" /></button>
          </div>
          <div className="flex items-center gap-2">
            {isSending && <div className="text-xs text-[#0052FF] font-bold flex items-center gap-2"><span className="h-3 w-3 rounded-full border-2 border-[#0052FF] border-t-transparent animate-spin"/> Syncing...</div>}
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto px-10 py-8 relative">
          <h1 className="text-2xl font-black text-[#0D1B3E] mb-8">Welcome to LuMay Insurance Support</h1>
          
          <div className="space-y-12">
            {messages.map((m, idx) => (
              <div key={idx} className="relative">
                <div className="flex justify-between items-start mb-6">
                  <div className="flex items-center gap-3">
                    <div className={`h-10 w-10 rounded-full flex items-center justify-center font-bold text-white shadow-sm ${m.role === "user" ? "bg-slate-800" : "bg-[#0052FF]"}`}>
                      {m.role === "user" ? customerInitials : "LU"}
                    </div>
                    <div>
                      <div className="flex items-baseline gap-2">
                        <p className="text-sm font-bold text-[#0D1B3E]">{m.role === "user" ? customerName : "LuMay Support"}</p>
                        <p className="text-xs text-slate-500">&lt;{m.role === "user" ? customerEmail : "support@lumay.com"}&gt;</p>
                      </div>
                      <p className="text-[11px] text-slate-400 mt-0.5">To: {m.role === "user" ? "support@lumay.com" : customerEmail}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <p className="text-xs text-slate-500">{new Date(m.timestamp).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}</p>
                    <div className="flex gap-2">
                      <Reply className="h-4 w-4 text-slate-400 cursor-pointer hover:text-slate-600" />
                      <MoreVertical className="h-4 w-4 text-slate-400 cursor-pointer hover:text-slate-600" />
                    </div>
                  </div>
                </div>
                
                <div className="pl-13 text-sm text-[#334155] whitespace-pre-wrap leading-relaxed font-sans max-w-3xl">
                <div className="prose prose-sm max-w-none text-[#333333]">
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>
                </div>
                
                {idx !== messages.length - 1 && (
                  <div className="absolute -bottom-6 left-0 right-0 border-b border-[#E5E7EB]"></div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} className="h-4" />
          </div>
        </div>

        {/* Reply Box */}
        <div className="px-10 py-6 border-t border-[#E5E7EB] bg-slate-50 shrink-0">
          <div className="bg-white border border-[#E5E7EB] rounded-2xl shadow-sm focus-within:border-blue-300 focus-within:shadow-md transition-all overflow-hidden flex flex-col">
            <textarea 
              placeholder="Click here to reply..." 
              value={textInput} 
              onChange={e => setTextInput(e.target.value)} 
              rows={4} 
              className="w-full p-4 text-sm focus:outline-none resize-none" 
              disabled={isSending} 
            />
            <div className="px-4 py-3 bg-slate-50 border-t border-[#E5E7EB] flex justify-between items-center">
              <div className="flex gap-4">
                <button className="text-slate-400 hover:text-slate-600 transition-colors"><Paperclip className="h-4 w-4" /></button>
                <button className="text-slate-400 hover:text-slate-600 transition-colors">Aa</button>
              </div>
              <button 
                onClick={() => handleSend(textInput)} 
                disabled={isSending || !textInput.trim()} 
                className="px-6 py-2 bg-[#0052FF] text-white rounded-xl text-sm font-bold flex items-center gap-2 hover:bg-blue-600 transition-colors disabled:opacity-50 shadow-sm shadow-blue-500/20"
              >
                <Send className="h-4 w-4" /> Send
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}

"use client";

import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Send, Sparkles, MoreHorizontal, Paperclip, Smile } from "lucide-react";
import { interactionsService } from "@/services/interactions.service";

interface ChatMessage { role: string; content: string; timestamp: string; }

import { useSearchParams } from "next/navigation";

export default function CustomerWebChatPage() {
  const searchParams = useSearchParams();
  const complaintId = searchParams.get("complaint_id");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [interactionId, setInteractionId] = useState<string | null>(null);
  const [textInput, setTextInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [typing, setTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    startSession();
  }, [complaintId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const startSession = async () => {
    try {
      const res = await interactionsService.start("cust-102", "web_chat", complaintId || undefined);
      const dbInt = res.data?.data;
      if (dbInt) {
        setInteractionId(dbInt.id);
        const initialGreeting = complaintId 
          ? `Hello Fatima! I see you are continuing your conversation regarding complaint #${complaintId.split('-')[0].toUpperCase()}.\n\nHow can I help you further with this issue?`
          : `Hello Fatima! Welcome to LuMay Insurance.\n\nI am your AI Assistant. How can I help you today?`;
        setMessages([{ role: "assistant", content: initialGreeting, timestamp: new Date().toISOString() }]);
      }
    } catch (err) { console.error("Failed to start:", err); }
  };

  const handleSend = async (text: string) => {
    if (!text.trim() || !interactionId || isSending) return;
    setMessages(prev => [...prev, { role: "user", content: text, timestamp: new Date().toISOString() }]);
    setTextInput("");
    setIsSending(true); setTyping(true);
    try {
      const res = await interactionsService.sendMessage(interactionId, text);
      const payload = res.data?.data;
      setTyping(false); setIsSending(false);
      if (payload) setMessages(prev => [...prev, { role: "assistant", content: payload.answer, timestamp: new Date().toISOString() }]);
    } catch (err) {
      setTyping(false); setIsSending(false);
      setMessages(prev => [...prev, { role: "assistant", content: "Sorry, I had trouble processing that request.", timestamp: new Date().toISOString() }]);
    }
  };

  return (
    <div className="h-full w-full flex flex-col bg-[#F8FAFC] animate-fade-in relative">
      {/* Premium Header */}
      <div className="h-20 px-8 bg-white border-b border-[#E2E8F0] flex items-center justify-between shrink-0 shadow-sm z-10">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="h-12 w-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-blue-400 text-white flex items-center justify-center shadow-lg shadow-blue-500/20">
              <Sparkles className="h-6 w-6" />
            </div>
            <div className="absolute -bottom-1 -right-1 h-4 w-4 bg-emerald-500 border-2 border-white rounded-full"></div>
          </div>
          <div>
            <h2 className="text-lg font-black text-[#0D1B3E] leading-tight">LuMay AI Assistant</h2>
            <p className="text-xs font-medium text-emerald-600">Online and ready to help</p>
          </div>
        </div>
        <button className="h-10 w-10 rounded-full hover:bg-slate-100 flex items-center justify-center text-slate-400 transition-colors">
          <MoreHorizontal className="h-5 w-5" />
        </button>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-8 space-y-6 scrollbar-hide [&::-webkit-scrollbar]:hidden [-ms-overflow-style:'none'] [scrollbar-width:'none']">
        <div className="text-center pb-4">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider bg-slate-200/50 px-3 py-1 rounded-full">Today</span>
        </div>
        
        {messages.map((m, idx) => (
          <div key={idx} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"} group`}>
            {m.role === "assistant" && (
              <div className="h-8 w-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center mr-3 mt-auto shrink-0 shadow-sm">
                <Sparkles className="h-4 w-4" />
              </div>
            )}
            
            <div className={`max-w-[65%] flex flex-col ${m.role === "user" ? "items-end" : "items-start"}`}>
              <div className={`p-4 text-[15px] leading-relaxed shadow-sm ${
                m.role === "user" 
                  ? "bg-[#0052FF] text-white rounded-3xl rounded-br-sm" 
                  : "bg-white text-[#0D1B3E] border border-[#E2E8F0] rounded-3xl rounded-bl-sm"
              }`}>
                <div className="prose prose-sm prose-slate max-w-none">
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>
              </div>
              <span className={`text-[10px] font-medium text-slate-400 mt-2 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 ${m.role === "user" ? "mr-1" : "ml-1"}`}>
                {new Date(m.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                {m.role === "user" && <span className="text-blue-500 text-xs">✓✓</span>}
              </span>
            </div>
          </div>
        ))}
        
        {typing && (
          <div className="flex justify-start items-end">
            <div className="h-8 w-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center mr-3 shrink-0 shadow-sm">
              <Sparkles className="h-4 w-4" />
            </div>
            <div className="bg-white border border-[#E2E8F0] px-4 py-4 rounded-3xl rounded-bl-sm shadow-sm flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"/>
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]"/>
              <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]"/>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 bg-white border-t border-[#E2E8F0] shrink-0">
        <div className="max-w-4xl mx-auto flex items-end gap-3 bg-slate-50 border border-[#E2E8F0] rounded-3xl p-2 focus-within:bg-white focus-within:border-blue-300 focus-within:shadow-md transition-all">
          <button className="p-3 text-slate-400 hover:text-blue-500 transition-colors shrink-0">
            <Paperclip className="h-5 w-5" />
          </button>
          <textarea 
            placeholder="Type your message..." 
            value={textInput} 
            onChange={e => setTextInput(e.target.value)} 
            onKeyDown={e => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend(textInput);
              }
            }}
            className="flex-1 bg-transparent max-h-32 py-3 text-[15px] text-[#0D1B3E] placeholder-slate-400 focus:outline-none resize-none" 
            rows={1}          />
          <button className="p-3 text-slate-400 hover:text-blue-500 transition-colors shrink-0">
            <Smile className="h-5 w-5" />
          </button>
          <button 
            onClick={() => handleSend(textInput)} 
            disabled={isSending || !textInput.trim()} 
            className="h-12 w-12 bg-[#0052FF] text-white rounded-2xl flex items-center justify-center hover:bg-blue-600 hover:scale-105 transition-all disabled:opacity-50 disabled:hover:scale-100 shrink-0 shadow-md shadow-blue-500/20"
          >
            <Send className="h-5 w-5 ml-0.5" />
          </button>
        </div>
        <p className="text-center text-[10px] text-slate-400 font-medium mt-3">
          Powered by LuMay AI Engine. Conversations may be analyzed for quality.
        </p>
      </div>
    </div>
  );
}

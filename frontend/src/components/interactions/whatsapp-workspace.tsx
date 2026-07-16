"use client";

import { MessageCircle, ImageIcon, Mic, Paperclip, Smile, Send, Check, CheckCheck } from "lucide-react";
import { cn } from "@/lib/cn";
import type { WorkspaceInteraction, WorkspaceMessage } from "@/features/interactions/types";

interface WhatsAppWorkspaceProps {
  interaction: WorkspaceInteraction;
  onSend: (text: string) => void;
  inputValue: string;
  onInputChange: (val: string) => void;
}

function WABubble({ msg, customerName }: { msg: WorkspaceMessage; customerName: string }) {
  const isCustomer = msg.sender === "customer";
  const isSystem = msg.sender === "system" || msg.type === "system_event";
  const isAI = msg.sender === "ai" || msg.type === "ai_note";

  if (isSystem) {
    return (
      <div className="flex justify-center py-1">
        <span className="text-[9px] text-[#667781] bg-[#d9fdd3]/80 px-3 py-1 rounded-full border border-[#d9fdd3]">
          {msg.text}
        </span>
      </div>
    );
  }

  if (isAI) {
    return (
      <div className="flex justify-center py-1">
        <div className="max-w-[75%] bg-violet-50 border border-violet-100 rounded-xl px-3 py-2 text-[10px] text-violet-700 text-center">
          {msg.text}
        </div>
      </div>
    );
  }

  return (
    <div className={cn("flex", isCustomer ? "justify-start" : "justify-end")}>
      <div
        className={cn(
          "max-w-[75%] px-3 py-2 rounded-2xl shadow-sm relative",
          isCustomer
            ? "bg-white text-[#111B21] rounded-tl-none"
            : "text-white rounded-tr-none"
        )}
        style={!isCustomer ? { background: "#25D366" } : {}}
      >
        {isCustomer && (
          <span className="block text-[9px] font-bold text-[#25D366] mb-0.5">{customerName}</span>
        )}
        <p className="text-[12px] leading-relaxed">{msg.text}</p>
        <div className={cn(
          "flex items-center gap-1 mt-1",
          isCustomer ? "justify-start" : "justify-end"
        )}>
          <span className="text-[9px] opacity-60 font-mono">{msg.time}</span>
          {!isCustomer && <CheckCheck className="h-3 w-3 opacity-70" />}
        </div>
      </div>
    </div>
  );
}

export function WhatsAppWorkspace({ interaction, onSend, inputValue, onInputChange }: WhatsAppWorkspaceProps) {
  function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!inputValue.trim()) return;
    onSend(inputValue);
  }

  return (
    <div className="flex flex-col h-full" style={{ background: "#ECE5DD" }}>
      {/* WhatsApp header */}
      <div className="px-4 py-3 flex items-center gap-3 shrink-0" style={{ background: "#128C7E" }}>
        <div className="h-9 w-9 rounded-full bg-[#25D366] flex items-center justify-center text-white font-bold text-sm">
          {interaction.customer.name.charAt(0)}
        </div>
        <div>
          <p className="text-sm font-bold text-white">{interaction.customer.name}</p>
          <p className="text-[10px] text-[#d9fdd3]">{interaction.customer.phone}</p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-[#25D366]" />
          <span className="text-[10px] text-[#d9fdd3]">WhatsApp</span>
        </div>
      </div>

      {/* Customer info strip */}
      <div className="px-4 py-2 flex items-center gap-3 bg-white/80 border-b border-[#d9fdd3] text-[10px] shrink-0">
        <span className="text-[#667781]">Policy:</span>
        <span className="font-bold text-[#111B21]">{interaction.customer.policyNumber}</span>
        <span className="text-[#667781] ml-2">Product:</span>
        <span className="font-bold text-[#111B21]">{interaction.customer.product}</span>
      </div>

      {/* Chat messages */}
      <div
        className="flex-1 overflow-y-auto p-4 space-y-2"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80'%3E%3Crect width='80' height='80' fill='%23E5DDD5'/%3E%3C/svg%3E")`,
        }}
      >
        {/* Date separator */}
        <div className="flex justify-center py-1">
          <span className="text-[9px] text-[#667781] bg-white/80 px-3 py-1 rounded-full shadow-sm">
            Today
          </span>
        </div>
        {interaction.messages.map(m => (
          <WABubble key={m.id} msg={m} customerName={interaction.customer.name} />
        ))}
      </div>

      {/* Attachment strip */}
      <div className="flex items-center gap-2 px-3 py-1.5 bg-white/90 border-t border-[#d9fdd3] shrink-0">
        <button className="text-[10px] font-semibold text-[#667781] flex items-center gap-1 px-2 py-1 rounded-lg hover:bg-slate-100">
          <ImageIcon className="h-3.5 w-3.5" /> Image
        </button>
        <button className="text-[10px] font-semibold text-[#667781] flex items-center gap-1 px-2 py-1 rounded-lg hover:bg-slate-100">
          <Mic className="h-3.5 w-3.5" /> Voice Note
        </button>
        <button className="text-[10px] font-semibold text-[#667781] flex items-center gap-1 px-2 py-1 rounded-lg hover:bg-slate-100">
          <Paperclip className="h-3.5 w-3.5" /> Attach
        </button>
      </div>

      {/* WhatsApp input */}
      <form onSubmit={handleSend} className="flex items-center gap-2 p-2.5 bg-[#F0F2F5] shrink-0">
        <button type="button" className="p-1.5 text-[#667781] hover:bg-slate-200 rounded-full">
          <Smile className="h-5 w-5" />
        </button>
        <input
          type="text"
          placeholder="Type a message"
          value={inputValue}
          onChange={e => onInputChange(e.target.value)}
          className="flex-1 bg-white px-4 py-2.5 text-sm rounded-3xl focus:outline-none border-0 shadow-sm"
          style={{ color: "#111B21" }}
        />
        <button
          type="submit"
          className="p-2.5 rounded-full text-white transition-all shadow-sm"
          style={{ background: inputValue.trim() ? "#25D366" : "#128C7E" }}
        >
          {inputValue.trim() ? <Send className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
        </button>
      </form>
    </div>
  );
}

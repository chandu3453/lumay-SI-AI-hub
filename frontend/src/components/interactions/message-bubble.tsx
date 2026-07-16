"use client";

import { cn } from "@/lib/cn";
import type { WorkspaceMessage } from "@/features/interactions/types";
import {
  Bot, User, Phone, Mail, Globe, Radio,
  AlertTriangle, FileText, Paperclip,
} from "lucide-react";

const SENDER_CONFIG = {
  customer: {
    label: "Customer",
    icon: <User className="h-3.5 w-3.5" />,
    bubble: "bg-slate-100 text-[#1E293B] rounded-tl-none mr-auto",
    avatar: "bg-slate-200 text-slate-600",
  },
  agent: {
    label: "Agent",
    icon: <User className="h-3.5 w-3.5" />,
    bubble: "bg-[#EFF6FF] text-[#1E3A8A] rounded-tr-none ml-auto border border-[#BFDBFE]/40",
    avatar: "bg-[#0052FF]/10 text-[#0052FF]",
  },
  ai: {
    label: "AI",
    icon: <Bot className="h-3.5 w-3.5" />,
    bubble: "bg-gradient-to-r from-violet-50 to-indigo-50 text-indigo-900 border border-indigo-100 rounded-xl w-full mx-auto",
    avatar: "bg-violet-100 text-violet-600",
  },
  system: {
    label: "System",
    icon: <AlertTriangle className="h-3 w-3" />,
    bubble: "bg-transparent text-slate-400 text-center w-full",
    avatar: "bg-slate-100 text-slate-400",
  },
};

function VoiceTranscriptBubble({ msg }: { msg: WorkspaceMessage }) {
  const isCustomer = msg.text.startsWith("[Customer]");
  return (
    <div className={cn(
      "flex gap-2 max-w-[85%] font-mono",
      isCustomer ? "mr-auto" : "ml-auto flex-row-reverse"
    )}>
      <div className={cn(
        "h-6 w-6 rounded-full flex items-center justify-center text-[9px] font-bold shrink-0 mt-0.5",
        isCustomer ? "bg-slate-200 text-slate-600" : "bg-[#0052FF]/10 text-[#0052FF]"
      )}>
        {isCustomer ? "C" : "A"}
      </div>
      <div className={cn(
        "px-3 py-2 rounded-xl text-[11px] leading-relaxed",
        isCustomer ? "bg-slate-100 text-slate-700 rounded-tl-none" : "bg-[#EFF6FF] text-[#1E3A8A] rounded-tr-none border border-[#BFDBFE]/40"
      )}>
        <span className="text-[9px] font-semibold text-slate-400 block mb-0.5">
          {isCustomer ? "▶ Customer" : "▶ Agent"}
        </span>
        {msg.text.replace(/^\[(Customer|Agent[^\]]*)\]\s*/, "")}
        <span className="text-[8px] text-slate-400 block mt-1 font-sans">{msg.time}</span>
      </div>
    </div>
  );
}

function EmailBubble({ msg }: { msg: WorkspaceMessage }) {
  return (
    <div className="w-full">
      <div className="border border-slate-200 rounded-xl bg-white shadow-sm overflow-hidden">
        <div className="bg-slate-50 border-b border-slate-200 px-4 py-2.5 flex items-center gap-2">
          <Mail className="h-4 w-4 text-[#3B82F6]" />
          <span className="text-xs font-bold text-[#0F172A]">Email Message</span>
          <span className="text-[10px] text-slate-400 ml-auto">{msg.time}</span>
        </div>
        <div className="px-4 py-3 text-xs text-[#334155] whitespace-pre-line leading-relaxed">
          {msg.text}
        </div>
      </div>
    </div>
  );
}

function SystemEventPill({ msg }: { msg: WorkspaceMessage }) {
  return (
    <div className="flex items-center gap-2 justify-center py-0.5">
      <div className="h-px flex-1 bg-slate-200" />
      <span className="text-[10px] text-slate-400 bg-[#F8FAFC] px-3 py-1 rounded-full border border-slate-200/80 whitespace-nowrap max-w-[80%] text-center">
        {msg.text}
      </span>
      <div className="h-px flex-1 bg-slate-200" />
    </div>
  );
}

function AINoteCard({ msg }: { msg: WorkspaceMessage }) {
  return (
    <div className="flex gap-2 items-start w-full">
      <div className="h-6 w-6 rounded-full bg-violet-100 flex items-center justify-center shrink-0 mt-0.5">
        <Bot className="h-3.5 w-3.5 text-violet-600" />
      </div>
      <div className="flex-1 bg-gradient-to-r from-violet-50 to-indigo-50 border border-indigo-100 rounded-xl rounded-tl-none px-3 py-2.5">
        <div className="flex items-center gap-1.5 mb-1">
          <span className="text-[9px] font-bold text-violet-600 uppercase tracking-wider">AI Intelligence</span>
        </div>
        <p className="text-[11px] text-indigo-900 leading-relaxed">{msg.text}</p>
        <span className="text-[8px] text-slate-400 block mt-1">{msg.time}</span>
      </div>
    </div>
  );
}

interface MessageBubbleProps {
  msg: WorkspaceMessage;
}

export function MessageBubble({ msg }: MessageBubbleProps) {
  if (msg.type === "voice_transcript") return <VoiceTranscriptBubble msg={msg} />;
  if (msg.type === "email") return <EmailBubble msg={msg} />;
  if (msg.type === "system_event") return <SystemEventPill msg={msg} />;
  if (msg.type === "ai_note") return <AINoteCard msg={msg} />;

  const config = SENDER_CONFIG[msg.sender];
  const isCustomer = msg.sender === "customer";
  const isSystem = msg.sender === "system";

  if (isSystem) return <SystemEventPill msg={msg} />;

  return (
    <div className={cn(
      "flex gap-2 max-w-[75%]",
      isCustomer ? "mr-auto" : "ml-auto flex-row-reverse"
    )}>
      <div className={cn(
        "h-6 w-6 rounded-full flex items-center justify-center shrink-0 mt-0.5 text-[9px] font-bold",
        config.avatar
      )}>
        {msg.sender === "ai" ? <Bot className="h-3.5 w-3.5" /> : msg.sender === "agent" ? (msg.agentName?.[0] ?? "A") : msg.sender[0].toUpperCase()}
      </div>
      <div>
        {msg.sender === "agent" && msg.agentName && (
          <span className={cn("text-[9px] text-slate-400 block mb-0.5", !isCustomer && "text-right")}>
            {msg.agentName}
          </span>
        )}
        <div className={cn("px-3 py-2 rounded-2xl text-xs leading-relaxed shadow-sm", config.bubble)}>
          {msg.attachments && msg.attachments.length > 0 && (
            <div className="mb-2 space-y-1">
              {msg.attachments.map((a, i) => (
                <div key={i} className="flex items-center gap-1.5 text-[10px] bg-white/60 px-2 py-1 rounded-lg border border-slate-200/50">
                  <Paperclip className="h-3 w-3" />
                  <span className="font-medium">{a.name}</span>
                  <span className="text-slate-400">{a.size}</span>
                </div>
              ))}
            </div>
          )}
          <p>{msg.text}</p>
          <span className={cn("text-[8px] text-slate-400 block mt-1 font-mono", !isCustomer && "text-right")}>
            {msg.time}
          </span>
        </div>
      </div>
    </div>
  );
}

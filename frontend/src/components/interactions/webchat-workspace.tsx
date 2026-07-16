"use client";

import { useRef, useEffect } from "react";
import { Globe, Circle, Loader2, Zap, Bot } from "lucide-react";
import { cn } from "@/lib/cn";
import type { WorkspaceInteraction, WorkspaceMessage } from "@/features/interactions/types";

interface WebChatWorkspaceProps {
  interaction: WorkspaceInteraction;
  onSend: (text: string) => void;
  inputValue: string;
  onInputChange: (val: string) => void;
  isSending?: boolean;
  providerUsed?: string;
}

function ChatBubble({ msg, customerName }: { msg: WorkspaceMessage; customerName: string }) {
  const isCustomer = msg.sender === "customer";
  const isSystem = msg.type === "system_event";
  const isAI = msg.type === "ai_note";

  if (isSystem) {
    return (
      <div className="flex justify-center py-1">
        <span className="text-[9px] text-slate-400 bg-slate-50 px-3 py-1 rounded-full border border-slate-200">
          {msg.text}
        </span>
      </div>
    );
  }

  if (isAI) {
    return (
      <div className="flex gap-2 items-start animate-in fade-in slide-in-from-bottom-2 duration-300">
        <div className="h-6 w-6 rounded-full bg-violet-100 flex items-center justify-center text-[9px] font-bold text-violet-600 shrink-0">
          AI
        </div>
        <div className="bg-violet-50 border border-violet-100 rounded-xl rounded-tl-none px-3 py-2 text-[10px] text-violet-800 leading-relaxed max-w-[80%]">
          {msg.text}
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex gap-2 items-end animate-in fade-in slide-in-from-bottom-2 duration-300",
        isCustomer ? "mr-auto" : "ml-auto flex-row-reverse"
      )}
    >
      <div
        className={cn(
          "h-7 w-7 rounded-full flex items-center justify-center text-[10px] font-extrabold shrink-0",
          isCustomer ? "bg-slate-200 text-slate-600" : "bg-[#0052FF] text-white"
        )}
      >
        {isCustomer ? customerName.charAt(0) : "A"}
      </div>
      <div
        className={cn(
          "max-w-[70%] px-3.5 py-2.5 rounded-2xl text-xs leading-relaxed shadow-sm",
          isCustomer
            ? "bg-white text-[#0F172A] rounded-bl-none border border-slate-100"
            : "bg-[#0052FF] text-white rounded-br-none"
        )}
      >
        <p className="whitespace-pre-wrap">{msg.text}</p>
        <span
          className={cn(
            "text-[8px] block mt-1 font-mono",
            isCustomer ? "text-slate-400" : "text-white/60 text-right"
          )}
        >
          {msg.time}
        </span>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex gap-2 items-end mr-auto animate-in fade-in duration-300">
      <div className="h-7 w-7 rounded-full bg-[#0052FF] flex items-center justify-center text-white shrink-0">
        <Bot className="h-3.5 w-3.5" />
      </div>
      <div className="bg-white border border-slate-100 rounded-2xl rounded-bl-none px-4 py-3 shadow-sm flex items-center gap-1.5">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="h-1.5 w-1.5 rounded-full bg-[#0052FF] animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
        <span className="text-[10px] text-slate-400 ml-1">AI is thinking...</span>
      </div>
    </div>
  );
}

function ProviderBadge({ provider }: { provider?: string }) {
  if (!provider || provider === "unknown") return null;
  const isAzure = provider === "azure_openai";
  const isOpenAI = provider === "openai";
  const isLocal = provider === "local";
  return (
    <div
      className={cn(
        "flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold border",
        isAzure && "bg-blue-50 text-blue-600 border-blue-200",
        isOpenAI && "bg-green-50 text-green-600 border-green-200",
        isLocal && "bg-amber-50 text-amber-600 border-amber-200"
      )}
    >
      <Zap className="h-2.5 w-2.5" />
      {isAzure ? "Azure OpenAI" : isOpenAI ? "OpenAI" : "Local AI"}
    </div>
  );
}

export function WebChatWorkspace({
  interaction,
  onSend,
  inputValue,
  onInputChange,
  isSending = false,
  providerUsed,
}: WebChatWorkspaceProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom whenever messages change or when sending
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [interaction.messages, isSending]);

  function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!inputValue.trim() || isSending) return;
    onSend(inputValue);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend(e as unknown as React.FormEvent);
    }
  }

  return (
    <div className="flex flex-col h-full bg-[#F8FAFC]">
      {/* Chat header */}
      <div className="px-4 py-3 bg-white border-b border-[#E2E8F0] flex items-center gap-3 shrink-0">
        <div className="h-8 w-8 rounded-xl bg-[#8B5CF6]/10 flex items-center justify-center">
          <Globe className="h-4 w-4 text-[#8B5CF6]" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-extrabold text-[#0F172A] truncate">{interaction.customer.name}</p>
          <p className="text-[10px] text-slate-400">
            Live Web Chat · {interaction.customer.policyNumber}
          </p>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <ProviderBadge provider={providerUsed} />
          <div className="flex items-center gap-1.5">
            <Circle
              className={cn(
                "h-2 w-2",
                isSending ? "fill-amber-400 text-amber-400" : "fill-[#10B981] text-[#10B981]"
              )}
            />
            <span
              className={cn(
                "text-[10px] font-semibold",
                isSending ? "text-amber-500" : "text-[#10B981]"
              )}
            >
              {isSending ? "AI Thinking..." : "Active"}
            </span>
          </div>
        </div>
      </div>

      {/* AI complaint banner */}
      {interaction.ai.complaintDetected && (
        <div className="px-4 py-2 bg-[#FFFBEB] border-b border-[#FDE68A] flex items-center justify-between text-xs shrink-0">
          <span className="flex items-center gap-1.5 font-semibold text-[#B45309]">
            <span className="h-1.5 w-1.5 rounded-full bg-[#EF4444] animate-pulse inline-block" />
            AI detected complaint · {interaction.ai.detectionConfidence}% confidence ·{" "}
            {interaction.ai.escalationRiskLevel} escalation risk
          </span>
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {interaction.messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-3 opacity-60">
            <div className="h-12 w-12 rounded-2xl bg-[#8B5CF6]/10 flex items-center justify-center">
              <Globe className="h-6 w-6 text-[#8B5CF6]" />
            </div>
            <p className="text-xs font-semibold text-slate-500">Start the conversation</p>
            <p className="text-[10px] text-slate-400 text-center max-w-[200px]">
              Type a message below to connect with the AI assistant
            </p>
          </div>
        )}
        {interaction.messages.map((m) => (
          <ChatBubble key={m.id} msg={m} customerName={interaction.customer.name} />
        ))}
        {isSending && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Compose input */}
      <form onSubmit={handleSend} className="p-3 bg-white border-t border-[#E2E8F0] shrink-0">
        <div
          className={cn(
            "flex items-center gap-2 border rounded-2xl bg-slate-50 px-3 py-2 transition-all",
            isSending
              ? "border-amber-200 ring-2 ring-amber-100"
              : "border-slate-200 focus-within:ring-2 focus-within:ring-[#0052FF]/20 focus-within:border-[#0052FF]/40"
          )}
        >
          <input
            type="text"
            placeholder={isSending ? "AI is processing your message..." : "Reply via web chat..."}
            value={inputValue}
            onChange={(e) => onInputChange(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 bg-transparent text-xs focus:outline-none text-[#0F172A] disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isSending}
            className="h-7 w-7 rounded-full bg-[#0052FF] hover:bg-[#0040CC] disabled:opacity-40 flex items-center justify-center transition-all shrink-0"
          >
            {isSending ? (
              <Loader2 className="h-3.5 w-3.5 text-white animate-spin" />
            ) : (
              <svg
                className="h-3.5 w-3.5 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2.5}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                />
              </svg>
            )}
          </button>
        </div>
        <p className="text-[9px] text-slate-300 mt-1 pl-1">
          Powered by LuMay AI · {providerUsed === "local" ? "Local Intelligence" : providerUsed === "azure_openai" ? "Azure OpenAI" : providerUsed === "openai" ? "OpenAI" : "AI Gateway"} · Press Enter to send
        </p>
      </form>
    </div>
  );
}

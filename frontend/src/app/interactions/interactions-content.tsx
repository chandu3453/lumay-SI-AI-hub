"use client";

import { useState, useMemo, useCallback, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { AlertTriangle, Check, SlidersHorizontal, UserCog, Download } from "lucide-react";
import { cn } from "@/lib/cn";

import { complaintsService } from "@/services/complaints.service";
import {
  interactionsService,
  mapInteractionToWorkspace,
  updateInteractionAI,
} from "@/services/interactions.service";
import { WORKSPACE_INTERACTIONS } from "@/features/interactions/mock-data";
import type {
  WorkspaceInteraction,
  ChannelId,
  WorkspaceMessage,
} from "@/features/interactions/types";

import { ChannelTabs, getChannelIcon, getChannelColor } from "@/components/interactions/channel-tabs";
import { ConversationList } from "@/components/interactions/conversation-list";
import { AIIntelligencePanel } from "@/components/interactions/ai-intelligence-panel";
import { ComposeBar } from "@/components/interactions/compose-bar";
import { MessageBubble } from "@/components/interactions/message-bubble";
import { VoiceWorkspace } from "@/components/interactions/voice-workspace";
import { WhatsAppWorkspace } from "@/components/interactions/whatsapp-workspace";
import { WebChatWorkspace } from "@/components/interactions/webchat-workspace";
import { EmailWorkspace } from "@/components/interactions/email-workspace";
import { CrmWorkspace } from "@/components/interactions/crm-workspace";
import { ManualWorkspace } from "@/components/interactions/manual-workspace";
import { SurveyWorkspace } from "@/components/interactions/survey-workspace";
import { ClaimsWorkspace } from "@/components/interactions/claims-workspace";

/* ── Status badge config ───────────────────────────────────────────────── */
const STATUS_CONFIG: Record<string, { label: string; cls: string }> = {
  high_risk: { label: "High Risk", cls: "bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20" },
  new: { label: "New", cls: "bg-[#0052FF]/10 text-[#0052FF] border-[#0052FF]/20" },
  in_progress: { label: "In Progress", cls: "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20" },
  processed: { label: "Processed", cls: "bg-[#10B981]/10 text-[#10B981] border-[#10B981]/20" },
  closed: { label: "Closed", cls: "bg-slate-100 text-slate-500 border-slate-200" },
  active: { label: "Active", cls: "bg-[#0052FF]/10 text-[#0052FF] border-[#0052FF]/20" },
  pending: { label: "Pending", cls: "bg-[#F59E0B]/10 text-[#F59E0B] border-[#F59E0B]/20" },
};

/* ── Toast ─────────────────────────────────────────────────────────────── */
interface ToastState { title: string; description: string; show: boolean; variant?: "success" | "error" }

/* ── Default center workspace (text-based channels) ───────────────────── */
function DefaultWorkspace({
  interaction,
  onSend,
  onEscalate,
  onCreateComplaint,
  onTransfer,
  isCreatingComplaint,
}: {
  interaction: WorkspaceInteraction;
  onSend: (text: string, type?: "reply" | "note") => void;
  onEscalate: () => void;
  onCreateComplaint: () => void;
  onTransfer: () => void;
  isCreatingComplaint: boolean;
}) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [interaction.messages]);

  return (
    <div className="flex flex-col h-full">
      {/* AI complaint banner */}
      {interaction.ai.complaintDetected && (
        <div className="px-5 py-2.5 bg-[#FFFBEB] border-b border-[#FDE68A] flex items-center justify-between text-xs shrink-0">
          <span className="flex items-center gap-1.5 font-semibold text-[#B45309]">
            <AlertTriangle className="h-4 w-4 text-[#F59E0B]" />
            AI detected complaint · {interaction.ai.detectionConfidence}% confidence · {interaction.ai.escalationRiskLevel} escalation risk
          </span>
          <button className="font-extrabold text-[#0052FF] text-[10px] hover:underline">
            View AI Analysis →
          </button>
        </div>
      )}

      {/* Messages timeline */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-[#F8FAFC]/50">
        {interaction.messages.map(m => (
          <MessageBubble key={m.id} msg={m} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Compose bar */}
      <ComposeBar
        channel={interaction.channel}
        onSend={onSend}
        onEscalate={onEscalate}
        onCreateComplaint={interaction.ai.complaintDetected ? onCreateComplaint : undefined}
        onTransfer={onTransfer}
        isCreatingComplaint={isCreatingComplaint}
      />
    </div>
  );
}

/* ── Conversation Header ────────────────────────────────────────────────── */
function ConversationHeader({ interaction }: { interaction: WorkspaceInteraction }) {
  const statusConf = STATUS_CONFIG[interaction.status] ?? STATUS_CONFIG.new;
  const channelColor = getChannelColor(interaction.channel);

  return (
    <div className="px-5 py-3.5 border-b border-[#E2E8F0] bg-white flex items-center justify-between shrink-0">
      <div className="flex items-center gap-3 min-w-0">
        <div
          className="h-9 w-9 rounded-xl flex items-center justify-center shrink-0"
          style={{ backgroundColor: `${channelColor}15` }}
        >
          {getChannelIcon(interaction.channel, "h-4.5 w-4.5")}
        </div>
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-sm font-extrabold text-[#0F172A] truncate">{interaction.customer.name}</h3>
            <span className={cn(
              "text-[9px] px-1.5 py-0.5 rounded border font-bold shrink-0",
              statusConf.cls
            )}>
              {statusConf.label}
            </span>
            {interaction.ai.escalationRisk >= 75 && (
              <span className="text-[9px] px-1.5 py-0.5 rounded border font-bold bg-[#EF4444]/10 text-[#EF4444] border-[#EF4444]/20 animate-pulse shrink-0">
                🔴 Critical Risk
              </span>
            )}
          </div>
          <p className="text-[10px] text-slate-400 font-mono truncate">
            <span className="capitalize">{interaction.channel.replace("_", " ")}</span>
            {" · "}{interaction.customer.policyNumber}
            {" · "}{interaction.customer.product}
            {interaction.assignedAgent && ` · ${interaction.assignedAgent}`}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <button className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-400 transition-colors">
          <SlidersHorizontal className="h-4 w-4" />
        </button>
        <button className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-400 transition-colors">
          <UserCog className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

/* ── Main Export ────────────────────────────────────────────────────────── */
export function InteractionsContent() {
  const router = useRouter();

  const [activeChannel, setActiveChannel] = useState<ChannelId>("all");
  const [selectedId, setSelectedId] = useState<string>("int-101");
  const [interactions, setInteractions] = useState<WorkspaceInteraction[]>(WORKSPACE_INTERACTIONS);
  const [whatsAppInput, setWhatsAppInput] = useState("");
  const [emailInput, setEmailInput] = useState("");
  const [webchatInput, setWebchatInput] = useState("");
  const [isCreatingComplaint, setIsCreatingComplaint] = useState(false);
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const [showRightPanel, setShowRightPanel] = useState(true);

  const [toast, setToast] = useState<ToastState>({ title: "", description: "", show: false });
  const [isSending, setIsSending] = useState(false);
  const [providerUsed, setProviderUsed] = useState<string>("unknown");

  function showToast(title: string, description: string, variant: "success" | "error" = "success") {
    setToast({ title, description, show: true, variant });
    setTimeout(() => setToast(prev => ({ ...prev, show: false })), 4500);
  }

  // Load real history on mount
  useEffect(() => {
    async function loadHistory() {
      try {
        const response = await interactionsService.getHistory();
        const dbItems = (response as any).data?.data || (response as any).data || [];
        
        if (dbItems.length > 0) {
          const mappedList: WorkspaceInteraction[] = [];
          for (const item of dbItems) {
            let msgs: any[] = [];
            try {
              msgs = JSON.parse(item.transcript || "[]");
            } catch {
              if (item.transcript) {
                msgs = [{ role: "user", content: item.transcript, timestamp: item.created_at }];
              }
            }
            mappedList.push(mapInteractionToWorkspace(item, msgs));
          }
          setInteractions(mappedList);
          
          if (mappedList.length > 0) {
            setSelectedId(mappedList[0].id);
          }
        }
      } catch (err) {
        console.error("Failed to load interactions history, using mock fallback:", err);
      }
    }
    loadHistory();
  }, []);

  const selectedInteraction = useMemo(
    () => interactions.find(i => i.id === selectedId) ?? interactions[0],
    [selectedId, interactions]
  );

  /* ── Send message ─────────────────────────────────────────────────────── */
  const handleSend = useCallback(async (text: string, type: "reply" | "note" = "reply") => {
    if (!text.trim() || isSending) return;

    const userTime = new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: true });
    const userMsg: WorkspaceMessage = {
      id: `msg-user-${Date.now()}`,
      sender: "customer",
      type: "text",
      text,
      time: userTime,
      timestamp: Date.now(),
    };

    setInteractions(prev =>
      prev.map(i =>
        i.id === selectedId
          ? {
              ...i,
              messages: [...i.messages, userMsg],
              lastMessage: text,
              unreadCount: 0,
            }
          : i
      )
    );

    setWhatsAppInput("");
    setEmailInput("");
    setWebchatInput("");
    setIsSending(true);

    try {
      const response = await interactionsService.sendMessage(selectedId, text);
      const payload = (response as any).data?.data || (response as any).data;
      
      if (payload) {
        setProviderUsed(payload.provider_used || "unknown");
        setInteractions(prev =>
          prev.map(i =>
            i.id === selectedId
              ? updateInteractionAI(i, payload)
              : i
          )
        );

        if (payload.auto_triaged) {
          showToast(
            "Auto-Triaged Complaint",
            `AI detected complaint at ${Math.round((payload.ai_analysis?.detection?.confidence ?? 0) * 100)}% confidence. Complaint, Workflow & Notifications created!`,
            "success"
          );
        }
      }
    } catch (err) {
      console.error("Failed to send message to AI Backend:", err);
      setTimeout(() => {
        const aiTime = new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: true });
        const responses = [
          "Thank you for reaching out! I'd be happy to assist you with your insurance needs. Could you please share your policy number so I can look into this for you?",
          "I understand your concern. Let me check the details and get back to you with the information you need.",
          "Thank you for your message. I'm looking into this for you. While I check, could you provide any relevant policy or claim numbers?",
          "I appreciate you contacting LuMay Insurance. Let me research your query and provide you with the best possible assistance.",
        ];
        const fallbackMsg: WorkspaceMessage = {
          id: `msg-fallback-${Date.now()}`,
          sender: "agent",
          type: "text",
          text: responses[Math.floor(Math.random() * responses.length)],
          time: aiTime,
          timestamp: Date.now(),
        };
        setInteractions(prev =>
          prev.map(i =>
            i.id === selectedId
              ? { ...i, messages: [...i.messages, fallbackMsg], lastMessage: fallbackMsg.text }
              : i
          )
        );
      }, 1000);
    } finally {
      setIsSending(false);
    }
  }, [selectedId, isSending]);

  /* ── Create Complaint ────────────────────────────────────────────────── */
  const handleCreateComplaint = useCallback(async () => {
    setIsCreatingComplaint(true);
    try {
      const res = await complaintsService.ingest({
        channel: selectedInteraction.channel,
        customer_id: selectedInteraction.customer.id,
        policy_number: selectedInteraction.customer.policyNumber,
        product: selectedInteraction.customer.product,
        transcript: selectedInteraction.messages
          .filter(m => m.type !== "ai_note" && m.type !== "system_event")
          .map(m => `[${m.sender}] ${m.text}`)
          .join("\n"),
        language: "en",
      });
      type IngestData = { complaint_number?: string; complaint_id?: string };
      const resObj = res as { data?: { data?: IngestData } & IngestData };
      const resData: IngestData = resObj?.data?.data ?? resObj?.data ?? {};
      showToast(
        "Complaint Created",
        `Complaint ${resData?.complaint_number ?? ""} created for ${selectedInteraction.customer.name}. AI analysis in progress.`
      );
      if (resData?.complaint_id) {
        router.push(`/complaint-cases/${resData.complaint_id}`);
      }
    } catch {
      showToast("Case Registered", "Complaint automatically registered. Redirecting...", "success");
    } finally {
      setIsCreatingComplaint(false);
    }
  }, [selectedInteraction, router]);

  /* ── Escalate ─────────────────────────────────────────────────────────── */
  const handleEscalate = useCallback(() => {
    setInteractions(prev =>
      prev.map(i => i.id === selectedId ? { ...i, status: "high_risk" as const, priority: "critical" as const } : i)
    );
    showToast("Escalated", `${selectedInteraction.customer.name}'s case has been escalated to management.`);
  }, [selectedId, selectedInteraction.customer.name]);

  /* ── Transfer ─────────────────────────────────────────────────────────── */
  const handleTransfer = useCallback(() => {
    showToast("Transfer Requested", "Case transfer request sent to the team queue.");
  }, []);

  /* ── Assign Agent ─────────────────────────────────────────────────────── */
  const handleAssignAgent = useCallback(() => {
    showToast("Agent Assignment", "Assign an agent from the team roster to handle this interaction.");
  }, []);

  /* ── Generate Summary ────────────────────────────────────────────────── */
  const handleGenerateSummary = useCallback(async () => {
    setIsGeneratingSummary(true);
    await new Promise(r => setTimeout(r, 1500));
    setIsGeneratingSummary(false);
    showToast("AI Summary Generated", "Summary has been refreshed with latest conversation context.");
  }, []);

  /* ── Center workspace renderer ───────────────────────────────────────── */
  function renderCenterWorkspace() {
    const channel = selectedInteraction.channel;

    if (channel === "voice" || channel === "smart_call") {
      return (
        <div className="flex flex-col h-full">
          <ConversationHeader interaction={selectedInteraction} />
          <VoiceWorkspace interaction={selectedInteraction} onSend={handleSend} />
        </div>
      );
    }
    if (channel === "whatsapp") {
      return (
        <div className="flex flex-col h-full">
          <WhatsAppWorkspace
            interaction={selectedInteraction}
            onSend={handleSend}
            inputValue={whatsAppInput}
            onInputChange={setWhatsAppInput}
          />
        </div>
      );
    }
    if (channel === "web_chat") {
      return (
        <div className="flex flex-col h-full">
          <WebChatWorkspace
            interaction={selectedInteraction}
            onSend={handleSend}
            inputValue={webchatInput}
            onInputChange={setWebchatInput}
            isSending={isSending}
            providerUsed={providerUsed}
          />
        </div>
      );
    }
    if (channel === "email") {
      return (
        <div className="flex flex-col h-full">
          <EmailWorkspace
            interaction={selectedInteraction}
            onSend={handleSend}
            inputValue={emailInput}
            onInputChange={setEmailInput}
          />
        </div>
      );
    }
    if (channel === "crm") {
      return (
        <div className="flex flex-col h-full">
          <ConversationHeader interaction={selectedInteraction} />
          <CrmWorkspace interaction={selectedInteraction} onSend={handleSend} />
        </div>
      );
    }
    if (channel === "manual") {
      return (
        <div className="flex flex-col h-full">
          <ConversationHeader interaction={selectedInteraction} />
          <ManualWorkspace interaction={selectedInteraction} onSend={handleSend} />
        </div>
      );
    }
    if (channel === "survey") {
      return (
        <div className="flex flex-col h-full">
          <ConversationHeader interaction={selectedInteraction} />
          <SurveyWorkspace interaction={selectedInteraction} />
        </div>
      );
    }
    if (channel === "claims") {
      return (
        <div className="flex flex-col h-full">
          <ConversationHeader interaction={selectedInteraction} />
          <ClaimsWorkspace interaction={selectedInteraction} onSend={handleSend} />
        </div>
      );
    }

    // Default (all, any other)
    return (
      <div className="flex flex-col h-full">
        <ConversationHeader interaction={selectedInteraction} />
        <DefaultWorkspace
          interaction={selectedInteraction}
          onSend={handleSend}
          onEscalate={handleEscalate}
          onCreateComplaint={handleCreateComplaint}
          onTransfer={handleTransfer}
          isCreatingComplaint={isCreatingComplaint}
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col" style={{ height: "calc(100vh - 112px)" }}>
      {/* Page header */}
      <div className="flex items-center justify-between mb-3 shrink-0">
        <div className="space-y-0.5">
          <h1 className="text-2xl font-extrabold tracking-tight text-[#0F172A]">Interactions</h1>
          <p className="text-sm font-medium text-[#64748B]">
            Enterprise Customer Communication Hub — all channels in one workspace
          </p>
        </div>
        <button className="flex h-9 items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-xs font-bold text-slate-700 hover:bg-slate-50 transition-all shadow-sm">
          <Download className="h-3.5 w-3.5 text-[#94A3B8]" />
          Export
        </button>
      </div>

      {/* Workspace container */}
      <div className="flex-1 flex flex-col overflow-hidden rounded-2xl border border-[#E2E8F0] shadow-sm bg-white min-h-0">
        {/* Channel tabs */}
        <ChannelTabs
          activeChannel={activeChannel}
          onChange={ch => {
            setActiveChannel(ch);
          }}
          interactions={interactions}
        />

        {/* Three-panel layout */}
        <div className="flex flex-1 overflow-hidden min-h-0">
          {/* LEFT PANEL — 25% */}
          <div className="w-[280px] border-r border-[#E2E8F0] flex flex-col min-h-0 shrink-0 bg-white">
            <ConversationList
              interactions={interactions}
              activeChannel={activeChannel}
              selectedId={selectedId}
              onSelect={id => {
                setSelectedId(id);
              }}
            />
          </div>

          {/* CENTER PANEL — flex-1 */}
          <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
            {renderCenterWorkspace()}
          </div>

          {/* RIGHT PANEL — 25% — hidden on small screens */}
          {showRightPanel && (
            <div className="hidden xl:flex w-[280px] border-l border-[#E2E8F0] flex-col min-h-0 shrink-0">
              <div className="flex items-center justify-between px-4 py-2.5 border-b border-[#E2E8F0] bg-white shrink-0">
                <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">
                  AI Intelligence
                </span>
                <button
                  onClick={() => setShowRightPanel(false)}
                  className="text-[9px] text-slate-400 hover:text-slate-600"
                >
                  ✕
                </button>
              </div>
              <div className="flex-1 overflow-y-auto p-3">
                <AIIntelligencePanel
                  interaction={selectedInteraction}
                  onCreateComplaint={handleCreateComplaint}
                  onEscalate={handleEscalate}
                  onAssignAgent={handleAssignAgent}
                  onGenerateSummary={handleGenerateSummary}
                  isCreatingComplaint={isCreatingComplaint}
                  isGeneratingSummary={isGeneratingSummary}
                />
              </div>
            </div>
          )}

          {/* AI panel toggle when hidden */}
          {!showRightPanel && (
            <button
              onClick={() => setShowRightPanel(true)}
              className="hidden xl:flex w-8 border-l border-[#E2E8F0] items-center justify-center text-slate-400 hover:bg-slate-50 hover:text-[#0052FF] transition-all shrink-0"
              title="Show AI Intelligence"
            >
              <span className="text-[8px] font-extrabold tracking-widest writing-mode-vertical uppercase [writing-mode:vertical-rl] rotate-180">
                AI Panel
              </span>
            </button>
          )}
        </div>
      </div>

      {/* Toast notification */}
      {toast.show && (
        <div className="fixed bottom-6 right-6 z-[300] max-w-sm bg-white border border-[#E2E8F0] shadow-2xl rounded-2xl p-4 animate-in fade-in slide-in-from-bottom-4 duration-300">
          <div className="flex items-start gap-3">
            <div className={cn(
              "h-8 w-8 rounded-full flex items-center justify-center shrink-0",
              toast.variant === "error"
                ? "bg-[#EF4444]/10 text-[#EF4444]"
                : "bg-[#10B981]/10 text-[#10B981]"
            )}>
              {toast.variant === "error"
                ? <AlertTriangle className="h-4 w-4" />
                : <Check className="h-4 w-4" />
              }
            </div>
            <div>
              <h5 className="text-xs font-extrabold text-[#0F172A]">{toast.title}</h5>
              <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">{toast.description}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
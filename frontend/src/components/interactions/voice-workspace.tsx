"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import {
  Mic,
  MicOff,
  PhoneOff,
  Volume2,
  Clock,
  Wifi,
  WifiOff,
  AlertCircle,
} from "lucide-react";
import { cn } from "@/lib/cn";
import type { WorkspaceInteraction, WorkspaceMessage } from "@/features/interactions/types";
import { MessageBubble } from "./message-bubble";
import { useVoiceCall } from "@/hooks/use-voice-call";

interface VoiceWorkspaceProps {
  interaction: WorkspaceInteraction;
  onSend: (text: string) => void;
}

function Waveform({ active }: { active: boolean }) {
  const [time, setTime] = useState(0);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    if (!active) {
      setTime(0);
      return;
    }
    const animate = () => {
      setTime((t) => t + 1);
      rafRef.current = requestAnimationFrame(animate);
    };
    rafRef.current = requestAnimationFrame(animate);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [active]);

  const bars = Array.from({ length: 24 });
  return (
    <div className="flex items-center justify-center gap-0.5 h-10">
      {bars.map((_, i) => (
        <div
          key={i}
          className={cn(
            "w-1 rounded-full transition-all duration-300",
            active ? "bg-[#10B981]" : "bg-slate-300"
          )}
          style={{
            height: active
              ? `${16 + Math.sin(i * 0.5 + time * 0.1) * 12 + 8}px`
              : "4px",
            transition: "height 0.15s ease",
          }}
        />
      ))}
    </div>
  );
}

function ConnectionIndicator({
  status,
}: {
  status: string;
}) {
  const config: Record<string, { color: string; icon: typeof Wifi; label: string }> = {
    idle: { color: "bg-slate-400", icon: WifiOff, label: "Idle" },
    connecting: { color: "bg-amber-500 animate-pulse", icon: Wifi, label: "Connecting..." },
    connected: { color: "bg-[#10B981] animate-pulse", icon: Wifi, label: "Connected" },
    muted: { color: "bg-[#10B981]", icon: MicOff, label: "Muted" },
    on_hold: { color: "bg-amber-500", icon: Wifi, label: "On Hold" },
    error: { color: "bg-red-500", icon: AlertCircle, label: "Error" },
    ended: { color: "bg-slate-400", icon: WifiOff, label: "Ended" },
  };
  const cfg = config[status] || config.idle;
  const Icon = cfg.icon;

  return (
    <div className="flex items-center gap-2">
      <div className={cn("h-2.5 w-2.5 rounded-full", cfg.color)} />
      <Icon className="h-3.5 w-3.5 text-slate-500" />
      <span className="text-[10px] font-medium text-slate-500">{cfg.label}</span>
    </div>
  );
}

export function VoiceWorkspace({ interaction, onSend }: VoiceWorkspaceProps) {
  const isDemoMode = typeof window !== "undefined"
    ? process.env.NEXT_PUBLIC_DEMO_MODE === "true"
    : false;
  const {
    status,
    transcript,
    durationFormatted,
    error,
    isMuted,
    startCall,
    endCall,
    toggleMute,
  } = useVoiceCall();

  const [callStarted, setCallStarted] = useState(false);
  const [inputValue, setInputValue] = useState("");

  const handleStartCall = useCallback(async () => {
    setCallStarted(true);
    await startCall(interaction.customer.id);
  }, [startCall, interaction.customer.id]);

  const handleEndCall = useCallback(async () => {
    await endCall();
  }, [endCall]);

  const isLive = callStarted && status !== "ended" && status !== "idle";

  const transcriptMessages: WorkspaceMessage[] = transcript
    .filter((s) => !s.is_partial)
    .map((s, i) => ({
      id: `voice-${i}-${s.timestamp}`,
      sender: s.role === "customer" ? "customer" : "agent",
      type: "voice_transcript" as const,
      text: s.text,
      time: s.timestamp
        ? new Date(s.timestamp).toLocaleTimeString("en-US", {
            hour: "2-digit",
            minute: "2-digit",
          })
        : "",
      timestamp: s.timestamp ? new Date(s.timestamp).getTime() : Date.now(),
    }));

  const partialTranscript = transcript.filter((s) => s.is_partial);

  return (
    <div className="flex flex-col h-full">
      {/* Connection status bar */}
      <div
        className={cn(
          "px-5 py-3 flex items-center justify-between shrink-0 border-b",
          isLive
            ? "bg-[#10B981]/10 border-[#10B981]/20"
            : status === "error"
            ? "bg-red-50 border-red-100"
            : "bg-slate-50 border-slate-100"
        )}
      >
        <div className="flex items-center gap-3">
          <ConnectionIndicator status={status} />
          {isLive && (
            <div className="flex items-center gap-1.5 text-xs text-slate-500">
              <Clock className="h-3.5 w-3.5" />
              <span className="font-mono font-bold text-slate-700">
                {durationFormatted}
              </span>
            </div>
          )}
        </div>
        {error && (
          <div className="flex items-center gap-1.5 text-xs text-red-600">
            <AlertCircle className="h-3.5 w-3.5" />
            <span>{error}</span>
          </div>
        )}
        {!isLive && !error && (
          <span className="text-[10px] text-slate-400">
            LiveKit Voice Pipeline
          </span>
        )}
      </div>

      {/* Error state */}
      {status === "error" && !isLive && (
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center max-w-md">
            <div className="h-16 w-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="h-8 w-8 text-red-500" />
            </div>
            <h3 className="text-sm font-bold text-slate-800 mb-2">
              Connection Failed
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              {error || "Unable to connect to the voice pipeline. Please try again."}
            </p>
            <button
              onClick={() => {
                setCallStarted(false);
              }}
              className="px-4 py-2 bg-[#0052FF] text-white text-xs font-bold rounded-xl hover:bg-[#0040D0] transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Waveform section */}
      {isLive && (
        <div className="px-5 py-4 bg-gradient-to-r from-[#F0FDF4] to-white border-b border-[#10B981]/10 shrink-0">
          <div className="bg-white rounded-2xl border border-[#10B981]/20 p-4 shadow-sm">
            <div className="flex items-center gap-3 mb-3">
              <div className="h-8 w-8 rounded-full bg-[#10B981]/10 flex items-center justify-center">
                <Volume2 className="h-4 w-4 text-[#10B981]" />
              </div>
              <div>
                <p className="text-xs font-bold text-[#0F172A]">
                  {isMuted ? "Microphone Muted" : "Speaking"}
                </p>
                <p className="text-[10px] text-slate-400">
                  {status === "muted" ? "Tap to unmute" : "AI Voice Agent Active"}
                </p>
              </div>
            </div>
            <Waveform active={!isMuted && status === "connected"} />
          </div>
        </div>
      )}

      {/* Transcript area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {transcriptMessages.length > 0 && (
          <div className="text-[10px] font-bold text-slate-400 uppercase text-center mb-2">
            Live Transcript
          </div>
        )}

        {transcriptMessages.map((msg) => (
          <MessageBubble key={msg.id} msg={msg} />
        ))}

        {/* Partial transcript indicator */}
        {partialTranscript.length > 0 && (
          <div className="flex items-center gap-2 text-xs text-slate-400 italic">
            <div className="h-1.5 w-1.5 rounded-full bg-[#10B981] animate-pulse" />
            <span>
              {partialTranscript[partialTranscript.length - 1]?.text || "Listening..."}
            </span>
          </div>
        )}

        {transcriptMessages.length === 0 && !isLive && status !== "error" && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-3">
                <Mic className="h-8 w-8 text-slate-400" />
              </div>
              <p className="text-sm font-bold text-slate-500 mb-1">
                Voice Pipeline Ready
              </p>
              <p className="text-xs text-slate-400 max-w-sm">
                Connect via LiveKit to start a real-time AI voice conversation.
                The Pipecat pipeline will handle STT, LLM, and TTS.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="px-5 py-4 border-t border-slate-200 bg-white shrink-0">
        {isLive ? (
          <div className="flex items-center justify-center gap-3">
            <button
              onClick={toggleMute}
              className={cn(
                "flex flex-col items-center gap-1 p-3 rounded-2xl transition-all",
                isMuted
                  ? "bg-[#EF4444]/10 text-[#EF4444]"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              )}
            >
              {isMuted ? (
                <MicOff className="h-5 w-5" />
              ) : (
                <Mic className="h-5 w-5" />
              )}
              <span className="text-[9px] font-bold">
                {isMuted ? "Unmute" : "Mute"}
              </span>
            </button>

            <button
              onClick={handleEndCall}
              className="flex flex-col items-center gap-1 p-3 rounded-2xl bg-[#EF4444] text-white hover:bg-[#DC2626] transition-all shadow-sm"
            >
              <PhoneOff className="h-5 w-5" />
              <span className="text-[9px] font-bold">End Call</span>
            </button>
          </div>
        ) : status !== "error" ? (
          <div className="flex items-center justify-center gap-3">
            <button
              onClick={handleStartCall}
              disabled={status === "connecting"}
              className={cn(
                "flex items-center gap-2 px-6 py-3 rounded-2xl font-bold text-sm transition-all shadow-sm",
                status === "connecting"
                  ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                  : "bg-[#10B981] text-white hover:bg-[#059669]"
              )}
            >
              {status === "connecting" ? (
                <>
                  <div className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
                  Connecting...
                </>
              ) : (
                <>
                  <Volume2 className="h-5 w-5" />
                  Start Voice Call
                </>
              )}
            </button>
          </div>
        ) : null}

        {/* Fallback text input for simulated mode (demo only) */}
        {isDemoMode && !isLive && status === "idle" && (
          <div className="mt-3 pt-3 border-t border-slate-100">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (inputValue.trim()) {
                  onSend(inputValue);
                  setInputValue("");
                }
              }}
              className="flex gap-2"
            >
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Simulate voice transcript..."
                className="flex-1 px-4 py-2 border border-slate-200 rounded-xl text-xs focus:outline-none focus:border-[#0052FF]"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-[#0052FF] hover:bg-[#0040D0] text-white font-bold rounded-xl text-xs transition-colors"
              >
                Send
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

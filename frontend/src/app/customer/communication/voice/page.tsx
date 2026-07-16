"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import {
  Phone,
  PhoneOff,
  Mic,
  MicOff,
  Volume2,
  ShieldCheck,
  Settings2,
  Loader2,
  Wifi,
  WifiOff,
  AlertCircle,
  Clock,
} from "lucide-react";
import {
  VoiceClient,
  type TranscriptSegment,
  type VoiceClientStatus,
  type LogType,
} from "@/lib/voice-client";
import { interactionsService } from "@/services/interactions.service";

// ─── Waveform animation ────────────────────────────────────────────────────
function Waveform({ active }: { active: boolean }) {
  const [time, setTime] = useState(0);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    if (!active) { setTime(0); return; }
    const animate = () => {
      setTime((t) => t + 1);
      rafRef.current = requestAnimationFrame(animate);
    };
    rafRef.current = requestAnimationFrame(animate);
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
  }, [active]);

  return (
    <div className="flex items-center justify-center gap-0.5 h-20">
      {Array.from({ length: 32 }).map((_, i) => (
        <div
          key={i}
          className="w-1 rounded-full"
          style={{
            height: active
              ? `${20 + Math.sin(i * 0.4 + time * 0.08) * 18 + 8}px`
              : "4px",
            background: active
              ? `hsl(${160 + i * 2}, 80%, 55%)`
              : "#334155",
            transition: "height 0.12s ease",
          }}
        />
      ))}
    </div>
  );
}

// ─── Log panel ────────────────────────────────────────────────────────────
interface LogEntry { type: LogType; message: string; time: string; }

const LOG_COLORS: Record<LogType, string> = {
  info: "text-slate-400",
  warn: "text-amber-400",
  error: "text-red-400",
  success: "text-emerald-400",
  transcript: "text-sky-400",
};

function LogPanel({ logs }: { logs: LogEntry[] }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [logs]);

  return (
    <div
      ref={ref}
      className="bg-slate-950 rounded-xl border border-slate-700 p-3 h-48 overflow-y-auto font-mono text-xs leading-relaxed"
    >
      {logs.length === 0 ? (
        <span className="text-slate-600">Session events will appear here…</span>
      ) : (
        logs.map((l, i) => (
          <div key={i}>
            <span className="text-slate-600">[{l.time}]</span>{" "}
            <span className={LOG_COLORS[l.type]}>{l.message}</span>
          </div>
        ))
      )}
    </div>
  );
}

// ─── Transcript panel ──────────────────────────────────────────────────────
function TranscriptPanel({ transcript }: { transcript: TranscriptSegment[] }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [transcript]);

  return (
    <div ref={ref} className="flex-1 overflow-y-auto space-y-2 p-2">
      {transcript.length === 0 ? (
        <p className="text-center text-slate-500 text-xs mt-8">Transcript will appear here…</p>
      ) : (
        transcript.map((seg, i) => (
          <div
            key={i}
            className={`flex ${seg.role === "customer" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] px-3 py-2 rounded-xl text-xs leading-relaxed ${
                seg.role === "customer"
                  ? "bg-orange-500/20 text-orange-100 border border-orange-500/30"
                  : seg.role === "assistant"
                  ? "bg-slate-700 text-slate-200"
                  : "bg-slate-800 text-slate-400 italic"
              } ${seg.is_partial ? "opacity-60" : ""}`}
            >
              <span className="text-[10px] font-bold uppercase text-slate-500 block mb-0.5">
                {seg.role === "customer" ? "You" : seg.role === "assistant" ? "AI Agent" : "System"}
                {seg.is_partial && " (typing…)"}
              </span>
              {seg.text}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────
export default function CustomerVoicePage() {
  const [status, setStatus] = useState<VoiceClientStatus>("idle");
  const [transcript, setTranscript] = useState<TranscriptSegment[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [callDuration, setCallDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLogs, setShowLogs] = useState(false);

  const clientRef = useRef<VoiceClient | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const addLog = useCallback((type: LogType, message: string) => {
    setLogs((prev) => [
      ...prev,
      { type, message, time: new Date().toLocaleTimeString() },
    ]);
  }, []);

  const startCall = async () => {
    setError(null);
    setStatus("connecting");
    setTranscript([]);
    setLogs([]);
    setCallDuration(0);
    addLog("info", "Starting session…");

    try {
      const res = await interactionsService.startVoiceSession("customer-portal");
      const data = res.data?.data;
      if (!data) throw new Error("No session data returned from server");

      addLog("success", `Session: ${data.session_id}`);

      const client = new VoiceClient({
        url: data.livekit_url,
        token: data.participant_token,
        roomName: data.room_name,

        onStatusChange: (s) => {
          setStatus(s);
          if (s === "connected") {
            // Start timer
            timerRef.current = setInterval(() => setCallDuration((d) => d + 1), 1000);
          }
        },

        onTranscriptUpdate: (segs) => setTranscript(segs),

        onConnectionStateChange: (connState) => {
          if (connState === "error") setError("Connection lost — reconnecting…");
          if (connState === "connected") setError(null);
        },

        onLog: addLog,

        onError: (err) => {
          setError(err.message);
          setStatus("error");
          addLog("error", err.message);
        },
      });

      client.sessionId = data.session_id;
      clientRef.current = client;
      await client.connect();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to start voice call";
      setError(msg);
      setStatus("error");
      addLog("error", `CONNECT_FAILED: ${msg}`);
    }
  };

  const endCall = async () => {
    addLog("info", "Ending session…");
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    if (clientRef.current) {
      await clientRef.current.disconnect();
      clientRef.current = null;
    }
    setStatus("ended");
    setIsMuted(false);
  };

  const toggleMute = async () => {
    if (clientRef.current) {
      await clientRef.current.toggleMute();
      setIsMuted(clientRef.current.isMuted);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      clientRef.current?.disconnect();
    };
  }, []);

  const fmt = (s: number) => `${Math.floor(s / 60).toString().padStart(2, "0")}:${(s % 60).toString().padStart(2, "0")}`;
  const isLive = status === "connected" || status === "muted";

  return (
    <div className="h-full w-full flex flex-col animate-fade-in bg-slate-900 text-white overflow-hidden relative">
      {/* Dynamic Background Glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full mix-blend-screen filter blur-[120px] opacity-20 transition-all duration-1000 ${
            isLive ? "bg-orange-500 scale-110" : "bg-slate-500 scale-90"
          }`}
        />
        <div
          className={`absolute top-0 right-0 w-[400px] h-[400px] rounded-full mix-blend-screen filter blur-[100px] opacity-20 transition-all duration-1000 delay-500 ${
            isLive ? "bg-purple-500" : "bg-transparent"
          }`}
        />
      </div>

      {/* Header */}
      <div className="relative z-10 h-16 px-6 flex items-center justify-between border-b border-slate-800">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
            End-to-End Encrypted
          </span>
        </div>
        <div className="flex items-center gap-3">
          {isLive && (
            <div className="flex items-center gap-1.5 text-xs text-slate-400">
              <Clock className="h-3.5 w-3.5" />
              <span className="font-mono font-bold text-slate-200">{fmt(callDuration)}</span>
            </div>
          )}
          <button
            onClick={() => setShowLogs((v) => !v)}
            title="Toggle debug logs"
            className="h-8 w-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
          >
            <Settings2 className="h-4 w-4 text-slate-300" />
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="relative z-10 mx-4 mt-3 flex items-center gap-2 bg-red-900/40 border border-red-700/60 rounded-xl px-4 py-2 text-xs text-red-300">
          <AlertCircle className="h-3.5 w-3.5 shrink-0" />
          {error}
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col relative z-10 overflow-hidden">
        {!isLive && status !== "connecting" ? (
          /* ── Pre-call / idle / ended / error state ── */
          <div className="flex-1 flex flex-col items-center justify-center gap-8 p-8">
            <div className="relative">
              <div className="h-32 w-32 bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-full shadow-2xl flex items-center justify-center">
                <span className="text-5xl">
                  {status === "ended" ? "📵" : status === "error" ? "⚠️" : "📞"}
                </span>
              </div>
            </div>
            <div className="text-center">
              <h2 className="text-3xl font-black text-white tracking-tight">LuMay Voice Agent</h2>
              <p className="text-sm font-mono text-slate-400 mt-2">
                {status === "ended" ? "Call ended" : status === "error" ? "Connection failed" : "Ready to connect"}
              </p>
            </div>
            <button
              onClick={status === "ended" || status === "error" ? () => { setStatus("idle"); setError(null); startCall(); } : startCall}
              className="h-16 w-16 rounded-full bg-emerald-500 text-white flex items-center justify-center hover:bg-emerald-600 transition-all hover:scale-110 shadow-lg shadow-emerald-500/20"
            >
              <Phone className="h-6 w-6" />
            </button>
          </div>
        ) : status === "connecting" ? (
          /* ── Connecting state ── */
          <div className="flex-1 flex flex-col items-center justify-center gap-6">
            <div className="h-32 w-32 rounded-full border-2 border-orange-500/40 flex items-center justify-center">
              <Loader2 className="h-10 w-10 text-orange-400 animate-spin" />
            </div>
            <div className="text-center">
              <h2 className="text-2xl font-black text-white">Connecting…</h2>
              <p className="text-sm text-slate-400 mt-1">Joining LiveKit room</p>
            </div>
          </div>
        ) : (
          /* ── Active call state ── */
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Waveform + status */}
            <div className="px-6 py-4 flex flex-col items-center border-b border-slate-800">
              <Waveform active={!isMuted} />
              <p className="text-sm font-mono text-slate-400 mt-2 capitalize">
                {isMuted ? "Microphone muted" : "Listening…"}
              </p>
            </div>

            {/* Transcript */}
            <div className="flex-1 overflow-hidden flex flex-col px-4 py-2">
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2">Live Transcript</p>
              <TranscriptPanel transcript={transcript} />
            </div>

            {/* Controls */}
            <div className="px-6 py-5 border-t border-slate-800 flex items-center justify-center gap-6">
              <button
                onClick={toggleMute}
                className={`h-14 w-14 rounded-full flex items-center justify-center transition-all hover:scale-105 ${
                  isMuted
                    ? "bg-red-500/20 text-red-400 border border-red-500/40"
                    : "bg-white/10 text-white hover:bg-white/20"
                }`}
              >
                {isMuted ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
              </button>

              <button
                onClick={endCall}
                className="h-14 w-14 rounded-full bg-red-500 text-white flex items-center justify-center hover:bg-red-600 transition-all hover:scale-110 shadow-lg shadow-red-500/20"
              >
                <PhoneOff className="h-5 w-5" />
              </button>
            </div>
          </div>
        )}

        {/* Debug Log Panel (toggled via Settings gear) */}
        {showLogs && (
          <div className="relative z-10 border-t border-slate-700 bg-slate-900 p-3">
            <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Pipeline Logs</p>
            <LogPanel logs={logs} />
          </div>
        )}
      </div>
    </div>
  );
}

"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import {
  VoiceClient,
  type TranscriptSegment,
  type VoiceClientStatus,
  type LogType,
} from "@/lib/voice-client";

export interface VoiceLog {
  type: LogType;
  message: string;
  time: string;
}

export function useVoiceCall() {
  const [status, setStatus] = useState<VoiceClientStatus>("idle");
  const [transcript, setTranscript] = useState<TranscriptSegment[]>([]);
  const [duration, setDuration] = useState(0);
  const [sessionId, setSessionId] = useState<string>("");
  const [interactionId, setInteractionId] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<VoiceLog[]>([]);
  const [isMuted, setIsMuted] = useState(false);

  const clientRef = useRef<VoiceClient | null>(null);
  const durationRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => {
      cleanup();
    };
  }, []);

  const addLog = useCallback((type: LogType, message: string) => {
    setLogs((prev) => [
      ...prev,
      { type, message, time: new Date().toLocaleTimeString() },
    ]);
  }, []);

  const cleanup = useCallback(() => {
    if (durationRef.current) {
      clearInterval(durationRef.current);
      durationRef.current = null;
    }
    if (clientRef.current) {
      clientRef.current.disconnect();
      clientRef.current = null;
    }
  }, []);

  const startCall = useCallback(
    async (customerRef?: string) => {
      setError(null);
      setStatus("connecting");
      setTranscript([]);
      setDuration(0);
      setLogs([]);

      try {
        const { voiceService } = await import("@/services/voice.service");
        const response = await voiceService.startSession(customerRef);
        const data = response.data.data;

        setSessionId(data.session_id);
        setInteractionId(data.interaction_id);

        const client = new VoiceClient({
          url: data.livekit_url,
          token: data.participant_token,
          roomName: data.room_name,

          // Status changes route directly into React state
          onStatusChange: (s) => {
            setStatus(s);
          },

          onTranscriptUpdate: (segments) => {
            setTranscript(segments);
          },

          onConnectionStateChange: (connState) => {
            if (connState === "error") {
              setError("Connection lost. Reconnecting...");
            }
          },

          onLog: (type, message) => {
            addLog(type, message);
          },

          onError: (err) => {
            setError(err.message);
            setStatus("error");
          },
        });

        client.sessionId = data.session_id;
        clientRef.current = client;

        await client.connect();

        // Start duration timer
        durationRef.current = setInterval(() => {
          setDuration((d) => d + 1);
        }, 1000);
      } catch (err: unknown) {
        const message =
          err instanceof Error ? err.message : "Failed to start voice call";
        setError(message);
        setStatus("error");
      }
    },
    [addLog]
  );

  const endCall = useCallback(async () => {
    if (clientRef.current) {
      await clientRef.current.disconnect();
    }
    if (durationRef.current) {
      clearInterval(durationRef.current);
      durationRef.current = null;
    }
    setStatus("ended");

    if (sessionId) {
      try {
        const { voiceService } = await import("@/services/voice.service");
        await voiceService.endSession(sessionId);
      } catch {
        // Best-effort cleanup
      }
    }
  }, [sessionId]);

  const toggleMute = useCallback(async () => {
    if (clientRef.current) {
      await clientRef.current.toggleMute();
      setIsMuted(clientRef.current.isMuted);
    }
  }, []);

  const formatDuration = useCallback((totalSeconds: number) => {
    const m = Math.floor(totalSeconds / 60);
    const s = totalSeconds % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  }, []);

  return {
    status,
    transcript,
    duration,
    durationFormatted: formatDuration(duration),
    sessionId,
    interactionId,
    error,
    isMuted,
    logs,
    startCall,
    endCall,
    toggleMute,
  };
}

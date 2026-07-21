// voice-client.ts
// Mirrors the EXACT connection lifecycle of voice_test.html (the verified-working reference).
// Do NOT use @livekit/components-react RoomAudioRenderer or useVoiceAssistant —
// those require a LiveKit Voice Assistant participant type. Our agent is a plain
// Pipecat participant, so we manage audio manually.

export interface VoiceClientConfig {
  url: string;
  token: string;
  roomName: string;
  onTranscriptUpdate?: (segments: TranscriptSegment[]) => void;
  onConnectionStateChange?: (state: ConnectionState) => void;
  onStatusChange?: (status: VoiceClientStatus) => void;
  onLog?: (type: LogType, message: string) => void;
  onError?: (error: Error) => void;
}

export interface TranscriptSegment {
  role: "customer" | "assistant" | "system";
  text: string;
  is_partial: boolean;
  timestamp: string;
}

export type ConnectionState =
  | "disconnected"
  | "connecting"
  | "connected"
  | "reconnecting"
  | "error";

export type VoiceClientStatus =
  | "idle"
  | "connecting"
  | "connected"
  | "muted"
  | "on_hold"
  | "error"
  | "ended";

export type LogType = "info" | "warn" | "error" | "success" | "transcript";

export class VoiceClient {
  private _room: any = null;
  private _localTrack: any = null;
  private _config: VoiceClientConfig;
  private _connectionState: ConnectionState = "disconnected";
  private _status: VoiceClientStatus = "idle";
  private _transcriptSegments: TranscriptSegment[] = [];
  private _pollInterval: ReturnType<typeof setInterval> | null = null;
  private _sessionId: string = "";
  private _reconnectAttempts = 0;
  private _eventSource: EventSource | null = null;
  // Keep track of audio elements so we can clean up properly
  private _audioElements: HTMLAudioElement[] = [];

  constructor(config: VoiceClientConfig) {
    this._config = config;
  }

  get status() { return this._status; }
  get connectionState() { return this._connectionState; }
  get sessionId() { return this._sessionId; }
  set sessionId(id: string) { this._sessionId = id; }
  get transcriptSegments() { return [...this._transcriptSegments]; }

  async connect() {
    this._setConnectionState("connecting");
    this._setStatus("connecting");

    try {
      const { Room, RoomEvent } = await import("livekit-client");

      // ── Identical to voice_test.html: plain Room, no options wrapper ──
      const room = new Room();

      // ROOM_CONNECTED
      room.on(RoomEvent.Connected, () => {
        this._log("success", "ROOM_CONNECTED: Connected to LiveKit room");
        this._setConnectionState("connected");
        this._setStatus("connected");
        this._reconnectAttempts = 0;
        this._startTranscriptPolling();
        this._startSSETranscriptStream();
      });

      // ROOM_DISCONNECTED
      room.on(RoomEvent.Disconnected, (reason: any) => {
        this._log("warn", `ROOM_DISCONNECTED: ${reason}`);
        this._setConnectionState("disconnected");
        this._stopTranscriptPolling();
        this._stopSSETranscriptStream();
      });

      // RECONNECTING
      room.on(RoomEvent.Reconnecting, () => {
        this._log("warn", "ROOM_RECONNECTING");
        this._setConnectionState("reconnecting");
        this._setStatus("connecting");
      });

      // RECONNECTED
      room.on(RoomEvent.Reconnected, () => {
        this._log("success", "ROOM_RECONNECTED");
        this._setConnectionState("connected");
        this._setStatus("connected");
        this._reconnectAttempts = 0;
      });

      // REMOTE_PARTICIPANT_JOINED
      room.on(RoomEvent.ParticipantConnected, (participant: any) => {
        this._log("info", `REMOTE_PARTICIPANT_JOINED: ${participant.identity}`);
      });

      // TRACK_SUBSCRIBED — mirrors voice_test.html exactly:
      //   new Audio() → srcObject = new MediaStream([track.mediaStreamTrack]) → play()
      room.on(RoomEvent.TrackSubscribed, (track: any, _publication: any, participant: any) => {
        this._log("success", `TRACK_SUBSCRIBED: from ${participant.identity} (kind: ${track.kind})`);
        if (track.kind === "audio") {
          this._attachAgentAudio(track, participant.identity);
        }
      });

      // TRACK_UNSUBSCRIBED — clean up audio element
      room.on(RoomEvent.TrackUnsubscribed, (track: any, _publication: any, participant: any) => {
        this._log("info", `TRACK_UNSUBSCRIBED: from ${participant.identity}`);
      });

      this._log("info", `Joining room ${this._config.roomName}...`);
      // ── Connect exactly as voice_test.html does ──
      await room.connect(this._config.url, this._config.token);
      this._log("success", "Room joined");

      // ── Enable microphone AFTER connecting (same order as voice_test.html) ──
      await room.localParticipant.setMicrophoneEnabled(true);
      this._log("success", "MICROPHONE_PUBLISHED: Microphone published to room");

      this._room = room;
    } catch (error) {
      this._setConnectionState("error");
      this._setStatus("error");
      const err = error instanceof Error ? error : new Error(String(error));
      this._log("error", `CONNECT_ERROR: ${err.message}`);
      this._config.onError?.(err);
      throw err;
    }
  }

  async disconnect() {
    this._stopTranscriptPolling();
    this._stopSSETranscriptStream();

    if (this._localTrack) {
      this._localTrack.stop();
      this._localTrack = null;
    }

    if (this._room) {
      try {
        await this._room.localParticipant.setMicrophoneEnabled(false);
      } catch {}
      this._room.disconnect();
      this._room = null;
    }

    this._removeAllAudioElements();
    this._setConnectionState("disconnected");
    this._setStatus("ended");
  }

  async toggleMute() {
    if (this._room) {
      const enabled = this._room.localParticipant.isMicrophoneEnabled;
      await this._room.localParticipant.setMicrophoneEnabled(!enabled);
      const newMuted = !(!enabled);
      this._setStatus(newMuted ? "muted" : "connected");
    }
  }

  get isMuted() {
    if (!this._room) return true;
    return !this._room.localParticipant?.isMicrophoneEnabled;
  }

  // ── Audio attachment — mirrors voice_test.html ──
  private _attachAgentAudio(track: any, participantIdentity: string) {
    try {
      const audio = new Audio();
      audio.srcObject = new MediaStream([track.mediaStreamTrack]);
      audio.volume = 1.0;
      audio.muted = false;
      audio.setAttribute("playsinline", "");
      audio.style.display = "none";
      document.body.appendChild(audio);
      this._audioElements.push(audio);

      this._log("info", `AUDIO_ELEMENT_CREATED for ${participantIdentity}`);

      audio.play()
        .then(() => {
          this._log("success", `AUDIO_PLAY_STARTED for ${participantIdentity}`);
        })
        .catch((e: Error) => {
          this._log("warn", `AUDIO_PLAY_FAILED: ${e.message} — waiting for user gesture`);
          // Re-attempt on user interaction (autoplay policy)
          const resume = () => {
            audio.play()
              .then(() => this._log("success", `AUDIO_PLAY_STARTED (resumed) for ${participantIdentity}`))
              .catch(() => {});
            document.removeEventListener("click", resume);
            document.removeEventListener("touchend", resume);
          };
          document.addEventListener("click", resume, { once: true });
          document.addEventListener("touchend", resume, { once: true });
        });
    } catch (e: any) {
      this._log("error", `AUDIO_ELEMENT_ERROR: ${e.message}`);
    }
  }

  private _removeAllAudioElements() {
    this._audioElements.forEach((el) => {
      try {
        el.pause();
        el.srcObject = null;
        el.remove();
      } catch {}
    });
    this._audioElements = [];
  }

  private _setConnectionState(state: ConnectionState) {
    this._connectionState = state;
    this._config.onConnectionStateChange?.(state);
  }

  private _setStatus(status: VoiceClientStatus) {
    this._status = status;
    this._config.onStatusChange?.(status);
  }

  private _log(type: LogType, message: string) {
    const prefix = `[VoiceClient] ${type.toUpperCase()}: `;
    if (type === "error") console.error(prefix + message);
    else if (type === "warn") console.warn(prefix + message);
    this._config.onLog?.(type, message);
  }

  private _startTranscriptPolling() {
    if (this._pollInterval) return;
    this._pollInterval = setInterval(async () => {
      if (!this._sessionId) return;
      try {
        const { voiceService } = await import("@/services/voice.service");
        const response = await voiceService.getTranscript(this._sessionId);
        const segments = response.data.data || [];
        const mapped: TranscriptSegment[] = segments.map((s: any) => ({
          role: s.role as "customer" | "assistant" | "system",
          text: s.text,
          is_partial: s.is_partial,
          timestamp: s.timestamp,
        }));
        this._transcriptSegments = mapped;
        this._config.onTranscriptUpdate?.(mapped);
      } catch {
        // Polling errors are expected during reconnection
      }
    }, 2000);
  }

  private _stopTranscriptPolling() {
    if (this._pollInterval) {
      clearInterval(this._pollInterval);
      this._pollInterval = null;
    }
  }

  private _startSSETranscriptStream() {
    if (!this._sessionId || this._eventSource) return;
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
    const url = `${baseUrl}/api/v1/voice/sessions/${this._sessionId}/stream`;

    this._eventSource = new EventSource(url);

    this._eventSource.addEventListener("transcript", (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        const segment: TranscriptSegment = {
          role: data.role as "customer" | "assistant" | "system",
          text: data.text,
          is_partial: data.is_partial || false,
          timestamp: data.timestamp,
        };
        const existingIndex = this._transcriptSegments.findIndex(
          (s) => s.timestamp === segment.timestamp && s.role === segment.role
        );
        if (segment.is_partial && existingIndex >= 0) {
          this._transcriptSegments[existingIndex] = segment;
        } else if (!segment.is_partial) {
          if (segment.role === "assistant" || segment.role === "customer") {
            const partialIndex = this._transcriptSegments.findIndex(
              (s) => s.role === segment.role && s.is_partial
            );
            if (partialIndex >= 0) {
              this._transcriptSegments[partialIndex] = segment;
            } else {
              this._transcriptSegments.push(segment);
            }
          } else {
            this._transcriptSegments.push(segment);
          }
        }
        this._config.onTranscriptUpdate?.([...this._transcriptSegments]);
      } catch {
        // Ignore parse errors
      }
    });

    this._eventSource.addEventListener("end", () => {
      this._stopSSETranscriptStream();
    });

    this._eventSource.onerror = () => {
      // SSE error - polling fallback will handle transcripts
    };
  }

  private _stopSSETranscriptStream() {
    if (this._eventSource) {
      this._eventSource.close();
      this._eventSource = null;
    }
  }
}

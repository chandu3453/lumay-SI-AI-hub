import { api } from "@/services/api-client";

export interface VoiceTokenResponse {
  session_id: string;
  interaction_id: string;
  room_name: string;
  participant_token: string;
  livekit_url: string;
}

export interface TranscriptSegment {
  role: string;
  text: string;
  is_partial: boolean;
  timestamp: string;
}

export interface VoiceSessionStatus {
  session_id: string;
  interaction_id: string;
  room_name: string;
  status: string;
  transcript_segments: TranscriptSegment[];
  started_at: string | null;
  ended_at: string | null;
}

export interface VoiceEndResponse {
  session_id: string;
  status: string;
  transcript: TranscriptSegment[];
}

export const voiceService = {
  async getToken(customerRef?: string, roomName?: string) {
    return api.post<{ data: VoiceTokenResponse }>("/voice/token", {
      customer_ref: customerRef,
      room_name: roomName,
    });
  },

  async startSession(customerRef?: string, roomName?: string) {
    return api.post<{ data: VoiceTokenResponse }>("/voice/start", {
      customer_ref: customerRef,
      room_name: roomName,
    });
  },

  async endSession(sessionId: string) {
    return api.post<{ data: VoiceEndResponse }>("/voice/end", {
      session_id: sessionId,
    });
  },

  async getSessionStatus(sessionId: string) {
    return api.get<{ data: VoiceSessionStatus }>(
      `/voice/sessions/${sessionId}`
    );
  },

  async getTranscript(sessionId: string) {
    return api.get<{ data: TranscriptSegment[] }>(
      `/voice/sessions/${sessionId}/transcript`
    );
  },
};

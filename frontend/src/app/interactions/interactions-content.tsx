"use client";

import { InteractionCenterShell } from "@/components/interaction-center/interaction-center-shell";

/** Sprint 28 Phase 3 — Omnichannel Interaction Center. Replaces the old
 * per-channel "workspace" page (9 disconnected components, useState-only,
 * seeded from mock data) with a 3-panel view built on the real
 * `/api/v1/conversations/*` API from Phases 1–2: every channel — web chat,
 * voice, WhatsApp, email, complaint — now shares one merged, live-updating
 * conversation timeline. */
export function InteractionsContent() {
  return (
    <div className="flex flex-col" style={{ height: "calc(100vh - 112px)" }}>
      <div className="mb-3 shrink-0 space-y-0.5">
        <h1 className="text-2xl font-extrabold tracking-tight text-foreground">Interactions</h1>
        <p className="text-sm font-medium text-muted-foreground">
          Unified omnichannel interaction center — every conversation, every channel, one timeline.
        </p>
      </div>

      <InteractionCenterShell />
    </div>
  );
}

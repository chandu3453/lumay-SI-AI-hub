"use client";

import { useEffect, useRef } from "react";
import { useDemoStore, type DemoEvent } from "@/stores/demo.store";

export function useDemoSSE() {
  const enabled = useDemoStore((s) => s.enabled);
  const addEvent = useDemoStore((s) => s.addEvent);
  const esRef = useRef<EventSource | null>(null);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    if (!enabled) {
      esRef.current?.close();
      esRef.current = null;
      return;
    }

    function connect() {
      esRef.current?.close();
      const es = new EventSource("/api/v1/demo/events");
      esRef.current = es;

      es.addEventListener("message", (msg) => {
        try {
          const data = JSON.parse(msg.data) as DemoEvent;
          addEvent(data);
        } catch { /* ignore parse errors */ }
      });

      es.addEventListener("complaint.submitted", (msg) => {
        try { addEvent(JSON.parse(msg.data) as DemoEvent); } catch { /* ignore */ }
      });
      es.addEventListener("interaction.started", (msg) => {
        try { addEvent(JSON.parse(msg.data) as DemoEvent); } catch { /* ignore */ }
      });
      es.addEventListener("interaction.transcript", (msg) => {
        try { addEvent(JSON.parse(msg.data) as DemoEvent); } catch { /* ignore */ }
      });
      es.addEventListener("interaction.sentiment_shift", (msg) => {
        try { addEvent(JSON.parse(msg.data) as DemoEvent); } catch { /* ignore */ }
      });
      es.addEventListener("ai.sentiment_analysis", (msg) => {
        try { addEvent(JSON.parse(msg.data) as DemoEvent); } catch { /* ignore */ }
      });
      es.addEventListener("ai.theme_classification", (msg) => {
        try { addEvent(JSON.parse(msg.data) as DemoEvent); } catch { /* ignore */ }
      });
      es.addEventListener("ai.root_cause_identified", (msg) => {
        try { addEvent(JSON.parse(msg.data) as DemoEvent); } catch { /* ignore */ }
      });
      es.addEventListener("ai.recommendation_generated", (msg) => {
        try { addEvent(JSON.parse(msg.data) as DemoEvent); } catch { /* ignore */ }
      });
      es.addEventListener("ai.override_requested", (msg) => {
        try { addEvent(JSON.parse(msg.data) as DemoEvent); } catch { /* ignore */ }
      });
      es.addEventListener("ai.escalation_triggered", (msg) => {
        try { addEvent(JSON.parse(msg.data) as DemoEvent); } catch { /* ignore */ }
      });
      es.addEventListener("workflow.created", (msg) => {
        try { addEvent(JSON.parse(msg.data) as DemoEvent); } catch { /* ignore */ }
      });
      es.addEventListener("notification.sent", (msg) => {
        try { addEvent(JSON.parse(msg.data) as DemoEvent); } catch { /* ignore */ }
      });
      es.addEventListener("dashboard.update", (msg) => {
        try { addEvent(JSON.parse(msg.data) as DemoEvent); } catch { /* ignore */ }
      });
      es.addEventListener("simulation.complete", (msg) => {
        try { addEvent(JSON.parse(msg.data) as DemoEvent); } catch { /* ignore */ }
      });

      es.onerror = () => {
        es.close();
        reconnectRef.current = setTimeout(connect, 3000);
      };
    }

    connect();

    return () => {
      clearTimeout(reconnectRef.current);
      esRef.current?.close();
    };
  }, [enabled, addEvent]);
}

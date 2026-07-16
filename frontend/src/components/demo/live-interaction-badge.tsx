"use client";

import { useEffect, useState } from "react";
import { useDemoStore } from "@/stores/demo.store";
import { cn } from "@/lib/cn";
import { Phone, MessageCircle, Globe, Headphones, Loader2 } from "lucide-react";

const CHANNEL_ICONS = {
  voice: Phone,
  web_chat: Globe,
  whatsapp: MessageCircle,
  smart_call: Headphones,
  email: MessageCircle,
};

const CHANNEL_LABELS: Record<string, string> = {
  voice: "Voice Call",
  web_chat: "Web Chat",
  whatsapp: "WhatsApp",
  smart_call: "Smart Call",
  email: "Email",
};

export function LiveInteractionBadge() {
  const enabled = useDemoStore((s) => s.enabled);
  const events = useDemoStore((s) => s.events);
  const [active, setActive] = useState(false);
  const [channel, setChannel] = useState<string>("");
  const [customer, setCustomer] = useState<string>("");
  const [phase, setPhase] = useState<string>("");

  useEffect(() => {
    if (!enabled || events.length === 0) return;

    const latest = events[events.length - 1];
    if (latest.event_type === "interaction.started") {
      setActive(true);
      setChannel(latest.data?.channel as string ?? "");
      setCustomer(latest.customer_name ?? "");
      setPhase("In Progress");
      const timer = setTimeout(() => setActive(false), 12000);
      return () => clearTimeout(timer);
    }
    if (latest.event_type === "interaction.ended") {
      setActive(false);
    }
  }, [events, enabled]);

  if (!enabled) return null;

  const Icon = CHANNEL_ICONS[channel as keyof typeof CHANNEL_ICONS] ?? Phone;

  return (
    <div
      className={cn(
        "fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-2xl border px-4 py-3 shadow-lg transition-all duration-500",
        active
          ? "border-emerald-200 bg-white shadow-emerald-100/50 translate-y-0 opacity-100"
          : "translate-y-4 opacity-0 pointer-events-none",
      )}
    >
      <div className="relative">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
          <Icon className="h-5 w-5" />
        </div>
        {active && (
          <span className="absolute -right-1 -top-1 h-3 w-3 rounded-full border-2 border-white bg-emerald-500 shadow-sm shadow-emerald-400">
            <Loader2 className="h-2.5 w-2.5 animate-spin text-white" />
          </span>
        )}
      </div>
      <div className="min-w-0">
        <p className="text-sm font-bold text-[#0F172A]">
          {CHANNEL_LABELS[channel] ?? "Interaction"}
        </p>
        <p className="text-[11px] text-[#64748B] truncate max-w-[160px]">
          {customer || "Live"}
        </p>
      </div>
      <span className="shrink-0 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-700">
        {phase || "Live"}
      </span>
    </div>
  );
}

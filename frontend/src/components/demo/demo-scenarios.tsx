"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/services/api-client";
import { useDemoStore } from "@/stores/demo.store";
import {
  MessageSquareWarning,
  Headphones,
  Brain,
  Play,
  Loader2,
} from "lucide-react";

const SCENARIOS = [
  {
    key: "complaint",
    label: "New Complaint",
    icon: MessageSquareWarning,
    endpoint: "/demo/simulate/complaint",
    description: "Submit a complaint with AI analysis & workflow",
  },
  {
    key: "interaction",
    label: "New Interaction",
    icon: Headphones,
    endpoint: "/demo/simulate/interaction",
    description: "Simulate a call/chat with transcript & sentiment",
  },
  {
    key: "ai-decision",
    label: "AI Decision",
    icon: Brain,
    endpoint: "/demo/simulate/ai-decision",
    description: "Trigger root cause, recommendation, or override",
  },
  {
    key: "full",
    label: "Full Sequence",
    icon: Play,
    endpoint: "/demo/simulate/full",
    description: "End-to-end complaint + interaction + AI decision",
  },
];

export function DemoScenarios() {
  const enabled = useDemoStore((s) => s.enabled);
  const [running, setRunning] = useState<string | null>(null);

  const queryClient = useQueryClient();
  const simulateMutation = useMutation({
    mutationFn: async (endpoint: string) => {
      const res = await api.post(endpoint);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["complaints"] });
      queryClient.invalidateQueries({ queryKey: ["interactions"] });
    },
    onSettled: () => setRunning(null),
  });

  if (!enabled) return null;

  return (
    <div className="space-y-3">
      <p className="text-xs font-semibold text-[#64748B] uppercase tracking-wider">
        Simulation Scenarios
      </p>
      <div className="grid grid-cols-2 gap-2">
        {SCENARIOS.map((s) => {
          const Icon = s.icon;
          const isLoading = running === s.key;
          return (
            <button
              key={s.key}
              disabled={isLoading}
              onClick={() => {
                setRunning(s.key);
                simulateMutation.mutate(s.endpoint);
              }}
              className="flex items-start gap-2.5 rounded-xl border border-[#E2E8F0] bg-white p-3 text-left text-xs shadow-sm transition-all hover:border-emerald-200 hover:bg-emerald-50/30 disabled:opacity-50"
            >
              <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
                {isLoading ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Icon className="h-3.5 w-3.5" />
                )}
              </div>
              <div className="min-w-0">
                <p className="font-semibold text-[#0F172A]">{s.label}</p>
                <p className="mt-0.5 text-[10px] text-[#64748B]">
                  {s.description}
                </p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

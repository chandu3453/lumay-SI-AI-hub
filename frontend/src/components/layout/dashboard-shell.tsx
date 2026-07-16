import type { ReactNode } from "react";

import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { useUiStore } from "@/stores/ui.store";
import { useIsMobile } from "@/hooks/use-media-query";
import { useDemoHealth } from "@/features/dashboard/use-dashboard";
import { Badge } from "@/components/ui/badge";
import { Wifi, WifiOff, RotateCcw, Loader2 } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/services/api-client";

type DashboardShellProps = {
  children: ReactNode;
};

export function DashboardShell({ children }: DashboardShellProps) {
  const { sidebar } = useUiStore();
  const isMobile = useIsMobile();
  const { data: health } = useDemoHealth();

  const isReady = health?.data_loaded ?? false;

  const resetDemo = useMutation({
    mutationFn: async () => {
      const res = await api.post("/demo/reset");
      return res.data;
    },
    onSuccess: () => {
      window.location.reload();
    },
  });

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-[#F8FAFC] dark:bg-background">
      {/* Top Header spans full width */}
      <Header />

      {/* Demo Alerts Banner below Header */}
      {isReady && (
        <div className="flex shrink-0 items-center gap-2 px-5 py-1.5 bg-primary/5 border-b border-primary/10 text-xs text-primary">
          <Wifi className="h-3 w-3" />
          <span>Demo Mode — <strong>4,400</strong> synthetic entities loaded</span>
          <button
            onClick={() => resetDemo.mutate()}
            disabled={resetDemo.isPending}
            className="ml-auto flex items-center gap-1.5 rounded-lg border border-primary/20 bg-white px-2.5 py-1 text-[10px] font-medium text-primary shadow-sm hover:bg-primary/5 transition-all disabled:opacity-50"
          >
            {resetDemo.isPending ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <RotateCcw className="h-3 w-3" />
            )}
            {resetDemo.isPending ? "Resetting..." : "Reset Demo"}
          </button>
          <Badge variant="outline" className="text-[10px] px-1.5 py-0 h-4">DEMO</Badge>
        </div>
      )}
      {!isReady && health && !health.data_loaded && (
        <div className="flex shrink-0 items-center gap-2 px-5 py-1.5 bg-warning/5 border-b border-warning/10 text-xs text-warning">
          <WifiOff className="h-3 w-3" />
          <span>Demo data not loaded. <button onClick={() => window.location.reload()} className="underline">Refresh</button> or visit the Dashboard to load data.</span>
        </div>
      )}

      {/* Main Layout Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar on the left */}
        <Sidebar />

        {/* Scrollable content on the right */}
        <main className="flex-1 overflow-y-auto bg-[#F8FAFC] dark:bg-background p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
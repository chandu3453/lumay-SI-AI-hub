"use client";

import { Suspense } from "react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { InteractionsContent } from "./interactions-content";

function LoadingFallback() {
  return (
    <DashboardShell>
      <div className="flex flex-col gap-3 animate-pulse">
        <div className="h-8 w-64 bg-slate-200 rounded-xl" />
        <div className="h-5 w-96 bg-slate-100 rounded-xl" />
        <div className="flex-1 h-[calc(100vh-180px)] bg-slate-100 rounded-2xl border border-slate-200" />
      </div>
    </DashboardShell>
  );
}

export default function InteractionsPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <DashboardShell>
        <InteractionsContent />
      </DashboardShell>
    </Suspense>
  );
}
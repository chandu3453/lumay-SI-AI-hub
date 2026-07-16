"use client";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { SearchView } from "@/features/search/search-view";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";

export default function SearchPage() {
  return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in">
        <div className="page-header">
          <h1>Enterprise Search</h1>
          <p>Full-text and semantic search across all entities and knowledge base</p>
        </div>
        <SearchView />
      </div>
      <AICopilot />
    </DashboardShell>
  );
}
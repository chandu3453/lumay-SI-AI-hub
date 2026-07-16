"use client";

import { useState } from "react";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

type ComplaintFiltersProps = {
  search: string;
  onSearchChange: (value: string) => void;
  channel: string;
  onChannelChange: (value: string) => void;
  theme: string;
  onThemeChange: (value: string) => void;
  severity: string;
  onSeverityChange: (value: string) => void;
  slaStatus: string;
  onSlaStatusChange: (value: string) => void;
  dateFrom: string;
  dateTo: string;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onClear: () => void;
  onApply: () => void;
};

const selectClass = "h-8 rounded-lg border border-border bg-background px-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-ring focus:border-primary";

export function ComplaintFilters({
  search, onSearchChange,
  channel, onChannelChange,
  theme, onThemeChange,
  severity, onSeverityChange,
  slaStatus, onSlaStatusChange,
  dateFrom, dateTo,
  onDateFromChange, onDateToChange,
  onClear, onApply,
}: ComplaintFiltersProps) {
  const hasFilters = channel || theme || severity || slaStatus || dateFrom || dateTo;

  return (
    <div className="bg-white dark:bg-card rounded-xl border border-border shadow-card p-4 space-y-3">
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search complaints..."
            className="pl-9 h-9"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <select value={channel} onChange={(e) => onChannelChange(e.target.value)} className={selectClass}>
          <option value="">All Channels</option>
          <option value="voice">Voice</option>
          <option value="whatsapp">WhatsApp</option>
          <option value="email">Email</option>
          <option value="web_chat">Web Chat</option>
          <option value="smart_call">SMART CALL</option>
          <option value="crm">CRM</option>
          <option value="manual">Manual</option>
        </select>

        <select value={theme} onChange={(e) => onThemeChange(e.target.value)} className={selectClass}>
          <option value="">All Themes</option>
          <option value="claim_delays">Claim Delays</option>
          <option value="service_quality">Service Quality</option>
          <option value="policy_coverage">Policy & Coverage</option>
          <option value="payments_refunds">Payments & Refunds</option>
          <option value="provider_garage">Provider / Garage</option>
          <option value="renewal">Renewal</option>
        </select>

        <select value={severity} onChange={(e) => onSeverityChange(e.target.value)} className={selectClass}>
          <option value="">All Severities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>

        <select value={slaStatus} onChange={(e) => onSlaStatusChange(e.target.value)} className={selectClass}>
          <option value="">All SLA</option>
          <option value="on_track">On Track</option>
          <option value="at_risk">At Risk</option>
          <option value="overdue">Overdue</option>
        </select>

        <div className="flex items-center gap-1">
          <Input
            type="date"
            value={dateFrom}
            onChange={(e) => onDateFromChange(e.target.value)}
            className="h-8 w-[130px] text-xs"
            placeholder="From"
          />
          <span className="text-xs text-muted-foreground">—</span>
          <Input
            type="date"
            value={dateTo}
            onChange={(e) => onDateToChange(e.target.value)}
            className="h-8 w-[130px] text-xs"
            placeholder="To"
          />
        </div>

        <div className="flex items-center gap-1 ml-auto">
          {hasFilters && (
            <Button variant="ghost" size="sm" className="h-8 gap-1 text-xs" onClick={onClear}>
              <X className="h-3.5 w-3.5" />
              Clear
            </Button>
          )}
          <Button variant="default" size="sm" className="h-8 text-xs" onClick={onApply}>
            Apply
          </Button>
        </div>
      </div>
    </div>
  );
}
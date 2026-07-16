"use client";

import { useQuery } from "@tanstack/react-query";
import { settingsService } from "@/services/settings.service";

export type AdminConfigCard = {
  id: string;
  icon: string;
  title: string;
  subtitle: string;
  count: number;
  countLabel: string;
  secondaryCount?: number;
  secondaryLabel?: string;
};

export type SystemOverview = {
  totalUsers: number;
  activeRoles: number;
  systemConfigs: number;
  pendingChanges: number;
};

export type Integration = {
  id: string;
  name: string;
  description: string;
  status: "connected" | "disconnected" | "warning";
};

export type ActivityItem = {
  id: string;
  activity: string;
  details: string;
  user: string;
  timestamp: string;
  status: "success" | "warning" | "pending" | "failed";
};

export type SlaPolicy = {
  name: string;
  value: number;
  color: string;
};

const CONFIG_CARDS: AdminConfigCard[] = [
  { id: "categories", icon: "Tags", title: "Categories & Taxonomy", subtitle: "Manage complaint themes, sub-themes, products and issue classification", count: 56, countLabel: "Categories" },
  { id: "sla", icon: "Clock", title: "SLA & Deadlines", subtitle: "Define and manage service level agreements, response times and resolution targets", count: 18, countLabel: "SLA Policies" },
  { id: "routing", icon: "GitBranch", title: "Routing & Escalation", subtitle: "Configure complaint routing rules, escalation protocols and assignment logic", count: 14, countLabel: "Routing Rules" },
  { id: "users", icon: "Users", title: "Users & Roles", subtitle: "Manage platform users, roles, permissions, and access control policies", count: 128, countLabel: "Users", secondaryCount: 18, secondaryLabel: "Roles" },
  { id: "channels", icon: "Radio", title: "Channels & Sources", subtitle: "Configure omnichannel sources, integrations, and communication endpoints", count: 9, countLabel: "Channels" },
  { id: "settings", icon: "Settings", title: "System Settings", subtitle: "Global platform configuration, feature toggles, and system preferences", count: 32, countLabel: "Settings" },
  { id: "notifications", icon: "Bell", title: "Notification Settings", subtitle: "Configure notification rules, delivery channels, and alert preferences", count: 24, countLabel: "Notification Rules" },
  { id: "templates", icon: "FileText", title: "Templates & Responses", subtitle: "Create and manage response templates, email templates, and canned responses", count: 42, countLabel: "Templates" },
  { id: "retention", icon: "Database", title: "Data Retention", subtitle: "Define data retention policies, archival rules, and purging schedules", count: 7, countLabel: "Retention Policies" },
  { id: "custom-fields", icon: "PenSquare", title: "Custom Fields", subtitle: "Create and manage custom data fields, forms, and metadata schemas", count: 23, countLabel: "Custom Fields" },
  { id: "ai", icon: "Brain", title: "AI & Detection Settings", subtitle: "Configure AI detection rules for sentiment, severity, escalation and duplicates", count: 15, countLabel: "AI Rules" },
  { id: "security", icon: "Shield", title: "Security & Compliance", subtitle: "Manage security policies, compliance frameworks, and access controls", count: 6, countLabel: "Policies" },
];

export function useConfigCards() {
  return useQuery({
    queryKey: ["admin", "config-cards"],
    queryFn: async () => {
      return CONFIG_CARDS;
    },
    staleTime: Infinity,
  });
}

export function useSystemOverview() {
  return useQuery({
    queryKey: ["admin", "overview"],
    queryFn: async () => {
      const res = await settingsService.getConfig();
      const config = res.data?.data ?? {};
      return {
        totalUsers: (config as any).total_users ?? 128,
        activeRoles: (config as any).active_roles ?? 18,
        systemConfigs: (config as any).system_configs ?? 32,
        pendingChanges: (config as any).pending_changes ?? 7,
      } satisfies SystemOverview;
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useSlaPolicySummary() {
  return useQuery({
    queryKey: ["admin", "sla-policies"],
    queryFn: async () => {
      return [
        { name: "Compliant", value: 68, color: "#16A34A" },
        { name: "At Risk", value: 22, color: "#F59E0B" },
        { name: "Breached", value: 10, color: "#DC2626" },
      ] satisfies SlaPolicy[];
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useIntegrations() {
  return useQuery({
    queryKey: ["admin", "integrations"],
    queryFn: async () => {
      return [
        { id: "cti", name: "Contact Center (CTI)", description: "Telephony integration and call routing", status: "connected" },
        { id: "smart-call", name: "SMART CALL", description: "AI-powered call analysis and transcription", status: "connected" },
        { id: "whatsapp", name: "WhatsApp Business API", description: "WhatsApp messaging channel integration", status: "connected" },
        { id: "m365", name: "Microsoft 365", description: "Email, calendar, and collaboration integration", status: "disconnected" },
        { id: "crm", name: "CRM Platform", description: "Customer relationship management sync", status: "warning" },
      ] satisfies Integration[];
    },
    staleTime: 30_000,
    retry: 1,
  });
}

export function useRecentActivity() {
  return useQuery({
    queryKey: ["admin", "activity"],
    queryFn: async () => {
      return [
        { id: "a1", activity: "User Created", details: "New user account created for Jennifer Adams", user: "Admin User", timestamp: "2 minutes ago", status: "success" },
        { id: "a2", activity: "SLA Policy Updated", details: "Response time threshold changed from 4h to 2h for High priority", user: "System Admin", timestamp: "15 minutes ago", status: "success" },
        { id: "a3", activity: "Category Modified", details: "Billing category split into Billing - Payments and Billing - Disputes", user: "Complaint Manager", timestamp: "1 hour ago", status: "warning" },
        { id: "a4", activity: "Integration Sync Failed", details: "CRM integration synchronization failed due to authentication error", user: "System", timestamp: "2 hours ago", status: "failed" },
        { id: "a5", activity: "Role Permissions Updated", details: "Supervisor role granted access to Escalation Dashboard", user: "Admin User", timestamp: "3 hours ago", status: "success" },
        { id: "a6", activity: "Retention Policy Triggered", details: "Q1 2024 data archival process initiated for 12,450 records", user: "System", timestamp: "5 hours ago", status: "pending" },
        { id: "a7", activity: "AI Rule Deployed", details: "Updated sentiment detection model v2.3 deployed to production", user: "ML Engineer", timestamp: "6 hours ago", status: "success" },
        { id: "a8", activity: "Channel Configuration Changed", details: "WhatsApp Business API rate limit increased from 100 to 250 msg/min", user: "System Admin", timestamp: "8 hours ago", status: "success" },
      ] satisfies ActivityItem[];
    },
    staleTime: 30_000,
    retry: 1,
  });
}
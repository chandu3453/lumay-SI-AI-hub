"use client";

import { Bot, BarChart3, MessageSquare, Shield, GitBranch, Bell } from "lucide-react";
import { Container } from "@/components/landing/Container";
import { SectionTitle } from "@/components/landing/SectionTitle";
import { FeatureCard } from "@/components/landing/FeatureCard";

const FEATURES = [
  {
    icon: <Bot className="h-5 w-5" />,
    title: "AI Complaint Intelligence",
    description: "Automatically classify, analyze sentiment, and prioritize complaints using enterprise-grade AI models.",
  },
  {
    icon: <BarChart3 className="h-5 w-5" />,
    title: "Executive Dashboard",
    description: "Real-time KPIs, trends, and analytics across your entire complaint lifecycle in one unified view.",
  },
  {
    icon: <MessageSquare className="h-5 w-5" />,
    title: "Omnichannel Intake",
    description: "Capture complaints from voice, email, chat, WhatsApp, and web forms into a single workspace.",
  },
  {
    icon: <Shield className="h-5 w-5" />,
    title: "SLA Compliance",
    description: "Automated SLA tracking, escalation management, and compliance reporting for regulatory requirements.",
  },
  {
    icon: <GitBranch className="h-5 w-5" />,
    title: "Smart Workflows",
    description: "Intelligent routing, approval chains, and resolution workflows that adapt to complaint complexity.",
  },
  {
    icon: <Bell className="h-5 w-5" />,
    title: "Multi-Channel Notifications",
    description: "Automated alerts across email, SMS, WhatsApp, and in-app for every stage of the complaint journey.",
  },
];

export function FeatureHighlights() {
  return (
    <section className="border-t border-[#E2E8F0] bg-[#F8FAFC] py-20">
      <Container>
        <SectionTitle
          label="Platform Capabilities"
          title="Everything you need to manage insurance complaints"
          description="Enterprise-grade tools for complaint intake, analysis, workflow, and resolution — all powered by AI."
        />

        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature) => (
            <FeatureCard key={feature.title} icon={feature.icon} title={feature.title} description={feature.description} />
          ))}
        </div>
      </Container>
    </section>
  );
}
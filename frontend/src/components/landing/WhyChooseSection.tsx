import { Container } from "@/components/landing/Container";
import { Brain, Smile, AlertTriangle, Clock, Network, User } from "lucide-react";

const REASONS = [
  {
    icon: <Brain className="h-5.5 w-5.5 text-[#0052FF]" />,
    title: "Complaint Intelligence",
    description: "Automatically detect, classify & prioritize complaints across all channels.",
    bgTheme: "bg-[#EFF6FF] border-[#BFDBFE]/60",
  },
  {
    icon: <Smile className="h-5.5 w-5.5 text-[#10B981]" />,
    title: "Sentiment Analysis",
    description: "Understand customer sentiment and emotion to identify dissatisfaction early.",
    bgTheme: "bg-[#ECFDF5] border-[#A7F3D0]/60",
  },
  {
    icon: <AlertTriangle className="h-5.5 w-5.5 text-[#8B5CF6]" />,
    title: "Escalation Management",
    description: "Predict escalation risk and alert agents & supervisors before it's too late.",
    bgTheme: "bg-[#F5F3FF] border-[#DDD6FE]/60",
  },
  {
    icon: <Clock className="h-5.5 w-5.5 text-[#F59E0B]" />,
    title: "SLA Monitoring",
    description: "Monitor SLA deadlines, predict breaches and ensure timely resolution.",
    bgTheme: "bg-[#FFFBEB] border-[#FEF3C7]/60",
  },
  {
    icon: <Network className="h-5.5 w-5.5 text-[#EC4899]" />,
    title: "Root Cause Analytics",
    description: "Identify recurring issues and systemic problems with AI-driven analytics.",
    bgTheme: "bg-[#FDF2F8] border-[#FBCFE8]/60",
  },
  {
    icon: <User className="h-5.5 w-5.5 text-[#06B6D4]" />,
    title: "Agent Assist",
    description: "Real-time AI suggestions, responses and knowledge during interactions.",
    bgTheme: "bg-[#ECFEFF] border-[#CFFAFE]/60",
  },
];

export function WhyChooseSection() {
  return (
    <section className="bg-white py-24 border-t border-[#E2E8F0] relative">
      <Container>
        {/* Section Header */}
        <div className="flex flex-col items-center text-center space-y-3 mb-16">
          <span className="text-[11px] font-extrabold uppercase tracking-widest text-[#64748B]">
            Why Choose LuMay
          </span>
          <h2 className="text-3xl font-black text-[#0D1B3E] sm:text-4xl tracking-tight">
            Built for Insurers. Powered by AI.
          </h2>
          {/* Subtle line indicator */}
          <div className="h-1 w-12 bg-[#0052FF] rounded-full mt-2" />
        </div>

        {/* Feature Cards Grid */}
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {REASONS.map((reason) => (
            <div
              key={reason.title}
              className="group rounded-3xl border border-[#E2E8F0] bg-white p-8 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md hover:border-slate-300"
            >
              {/* Icon Container */}
              <div className={`mb-6 flex h-12 w-12 items-center justify-center rounded-2xl border ${reason.bgTheme} transition-transform duration-300 group-hover:scale-105`}>
                {reason.icon}
              </div>
              
              {/* Title */}
              <h3 className="mb-3 text-lg font-bold text-[#0D1B3E] tracking-tight">
                {reason.title}
              </h3>
              
              {/* Description */}
              <p className="text-sm leading-relaxed text-[#64748B]">
                {reason.description}
              </p>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}
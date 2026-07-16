import { Container } from "@/components/landing/Container";
import { Smile, ShieldCheck, TrendingUp, FileText } from "lucide-react";

const BENEFITS = [
  {
    icon: <Smile className="h-6 w-6 text-[#0052FF]" />,
    title: "Improve Customer Experience",
    description: "Resolve issues faster and increase customer satisfaction.",
  },
  {
    icon: <ShieldCheck className="h-6 w-6 text-[#0052FF]" />,
    title: "Reduce Operational Risk",
    description: "Detect risks early and prevent SLA or compliance breaches.",
  },
  {
    icon: <TrendingUp className="h-6 w-6 text-[#0052FF]" />,
    title: "Drive Business Insights",
    description: "Uncover trends and pain points across products and channels.",
  },
  {
    icon: <FileText className="h-6 w-6 text-[#0052FF]" />,
    title: "Ensure Compliance",
    description: "Maintain audit trails and meet regulatory requirements.",
  },
];

export function BenefitsSection() {
  return (
    <section className="bg-[#F8FAFF] py-24 border-t border-[#E2E8F0]">
      <Container>
        {/* Section Header */}
        <div className="flex flex-col items-center text-center space-y-3 mb-16">
          <span className="text-[11px] font-extrabold uppercase tracking-widest text-[#64748B]">
            One Platform. Complete Intelligence.
          </span>
          <h2 className="text-3xl font-black text-[#0D1B3E] sm:text-4xl tracking-tight">
            Transform Every Interaction Into Better Outcomes.
          </h2>
          <div className="h-1 w-12 bg-[#0052FF] rounded-full mt-2" />
        </div>

        {/* 4-column benefits grid */}
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {BENEFITS.map((b) => (
            <div
              key={b.title}
              className="group rounded-3xl border border-[#E2E8F0] bg-white p-8 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md hover:border-blue-100"
            >
              <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 border border-blue-100/50 transition-transform duration-300 group-hover:scale-105">
                {b.icon}
              </div>
              <h3 className="mb-2 text-base font-bold text-[#0D1B3E] tracking-tight leading-snug">
                {b.title}
              </h3>
              <p className="text-sm leading-relaxed text-[#64748B]">
                {b.description}
              </p>
            </div>
          ))}
        </div>
      </Container>
    </section>
  );
}
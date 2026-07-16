import Link from "next/link";
import { ArrowRight, Sparkles, Headphones, ShieldCheck, ScanSearch } from "lucide-react";
import { Container } from "@/components/landing/Container";
import { HeroIllustration } from "@/components/landing/HeroIllustration";

const FEATURE_BADGES = [
  {
    icon: <Sparkles className="h-4 w-4 shrink-0" />,
    title: "AI-Powered",
    description: "Detect, analyze & act in real-time",
  },
  {
    icon: <Headphones className="h-4 w-4 shrink-0" />,
    title: "Omnichannel",
    description: "Voice, chat, email, WhatsApp & more",
  },
  {
    icon: <ShieldCheck className="h-4 w-4 shrink-0" />,
    title: "Enterprise Ready",
    description: "Secure, scalable & compliant",
  },
];

export function Hero() {
  return (
    <section
      className="relative overflow-hidden"
      style={{
        background:
          "linear-gradient(135deg, #ffffff 0%, #f0f6ff 45%, #e6f0ff 75%, #f5f9ff 100%)",
      }}
    >
      {/* Background radial glows */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0"
        style={{ zIndex: 0 }}
      >
        <div
          style={{
            position: "absolute",
            right: "-5%",
            top: "10%",
            width: 600,
            height: 600,
            borderRadius: "50%",
            background:
              "radial-gradient(circle, rgba(219,234,254,0.55) 0%, transparent 70%)",
          }}
        />
        <div
          style={{
            position: "absolute",
            left: "-10%",
            bottom: "-10%",
            width: 400,
            height: 400,
            borderRadius: "50%",
            background:
              "radial-gradient(circle, rgba(239,246,255,0.5) 0%, transparent 70%)",
          }}
        />
      </div>

      <Container>
        <div
          className="relative grid items-center gap-0"
          style={{
            zIndex: 1,
            gridTemplateColumns: "1fr 1fr",
            paddingTop: "80px",
            paddingBottom: "80px",
          }}
        >
          {/* ── LEFT COLUMN: Text content ── */}
          <div className="flex flex-col gap-7 lg:max-w-[560px]">
            {/* Badge */}
            <div>
              <span
                className="inline-flex items-center gap-2 rounded-full border border-blue-200/80 bg-blue-50 px-4 py-1.5"
                style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.08em", color: "#1D4ED8", textTransform: "uppercase" }}
              >
                <ScanSearch className="h-3.5 w-3.5 text-blue-500" />
                AI-Powered Insurance Operations
              </span>
            </div>

            {/* Headline */}
            <h1
              style={{
                fontSize: "clamp(2.2rem, 4vw, 3.4rem)",
                fontWeight: 900,
                lineHeight: 1.1,
                letterSpacing: "-0.02em",
                color: "#0D1B3E",
                margin: 0,
              }}
            >
              Intelligent Complaints.
              <br />
              Happier Customers.
              <br />
              Stronger{" "}
              <span style={{ color: "#0052FF" }}>Insurance.</span>
            </h1>

            {/* Description */}
            <p
              style={{
                fontSize: 16,
                lineHeight: 1.75,
                color: "#475569",
                maxWidth: 480,
                margin: 0,
              }}
            >
              LuMay SMART Insurance AI Hub transforms every customer interaction
              into actionable intelligence with real-time detection, sentiment
              analysis, and escalation management.
            </p>

            {/* CTA buttons */}
            <div className="flex flex-wrap items-center gap-3">
              <Link
                href="/login"
                className="inline-flex items-center gap-2 rounded-xl bg-[#0052FF] px-7 py-3.5 text-sm font-bold text-white transition-all hover:bg-blue-700 hover:shadow-lg hover:shadow-blue-400/30 active:scale-[0.98]"
                style={{ boxShadow: "0 4px 14px rgba(0,82,255,0.25)" }}
              >
                Request Demo
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 rounded-xl border border-[#CBD5E1] bg-white px-7 py-3.5 text-sm font-bold text-[#0052FF] transition-all hover:bg-slate-50 hover:border-blue-200 active:scale-[0.98]"
                style={{ boxShadow: "0 2px 8px rgba(0,0,0,0.06)" }}
              >
                Explore Solutions
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>

            {/* Feature badges */}
            <div className="flex items-center gap-6 border-t border-slate-100 pt-6 flex-wrap sm:flex-nowrap">
              {FEATURE_BADGES.map((b) => (
                <div key={b.title} className="flex items-start gap-3">
                  <div
                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-blue-100 bg-blue-50 text-[#0052FF]"
                  >
                    {b.icon}
                  </div>
                  <div>
                    <p className="text-[13px] font-bold text-[#0D1B3E]">{b.title}</p>
                    <p className="text-[12px] text-[#64748B] leading-snug">{b.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* ── RIGHT COLUMN: Hero illustration ── */}
          <div className="hidden lg:flex items-center justify-center">
            <HeroIllustration />
          </div>
        </div>
      </Container>
    </section>
  );
}
import Link from "next/link";
import { Headphones, ArrowRight } from "lucide-react";
import { Container } from "@/components/landing/Container";

export function CTASection() {
  return (
    <section className="bg-white py-20 border-t border-[#E2E8F0] relative">
      <Container>
        <div
          className="relative overflow-hidden rounded-3xl px-8 py-16 lg:px-16 shadow-xl"
          style={{
            background: "linear-gradient(135deg, #0052FF 0%, #1E40AF 60%, #0F1F4B 100%)",
          }}
        >
          {/* Subtle dots background decoration in top-right */}
          <div className="absolute right-6 top-6 opacity-20 pointer-events-none hidden lg:block">
            <svg width="100" height="100" fill="none" viewBox="0 0 100 100">
              <pattern id="dot-pattern-cta" x="0" y="0" width="16" height="16" patternUnits="userSpaceOnUse">
                <circle cx="2" cy="2" r="2" fill="white" />
              </pattern>
              <rect width="100" height="100" fill="url(#dot-pattern-cta)" />
            </svg>
          </div>

          {/* Glowing ambient dots */}
          <div
            className="absolute rounded-full pointer-events-none"
            style={{
              width: 300,
              height: 300,
              background: "radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 80%)",
              top: "-50%",
              left: "-10%",
            }}
          />

          <div className="relative z-10 flex flex-col items-center justify-between gap-10 lg:flex-row">
            {/* Left side: Headset circle + Text content */}
            <div className="flex flex-col items-center gap-6 text-center lg:flex-row lg:text-left">
              {/* Headphone graphic with outline circles */}
              <div className="relative flex shrink-0 items-center justify-center">
                <div className="absolute h-20 w-20 rounded-full border border-white/20" />
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white/10 backdrop-blur-md border border-white/30">
                  <Headphones className="h-7 w-7 text-white" />
                </div>
              </div>

              {/* Text */}
              <div className="space-y-2 max-w-xl">
                <h2 className="text-2xl font-black tracking-tight text-white sm:text-3xl">
                  Ready to Transform Your Customer Experience?
                </h2>
                <p className="text-sm text-blue-50/90 leading-relaxed font-semibold">
                  Join LuMay Insurance and leading insurers in the region who are using AI to deliver exceptional service and operational excellence.
                </p>
              </div>
            </div>

            {/* Right side: Action Buttons */}
            <div className="flex flex-col sm:flex-row items-center gap-4 shrink-0 w-full sm:w-auto">
              <Link
                href="/login"
                className="inline-flex w-full sm:w-auto items-center justify-center rounded-xl bg-white px-7 py-3.5 text-sm font-bold text-[#0052FF] transition-all hover:bg-slate-50 active:scale-[0.98]"
                style={{ boxShadow: "0 4px 12px rgba(0,0,0,0.1)" }}
              >
                Request Demo
              </Link>
              <Link
                href="/login"
                className="inline-flex w-full sm:w-auto items-center justify-center rounded-xl border border-white/30 bg-transparent px-7 py-3.5 text-sm font-bold text-white hover:bg-white/10 transition-all active:scale-[0.98]"
              >
                <span>Contact Sales</span>
                <ArrowRight className="ml-1.5 h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}
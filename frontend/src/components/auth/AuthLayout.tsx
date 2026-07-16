import { LoginHero } from "@/components/auth/LoginHero";
import { LoginCard } from "@/components/auth/LoginCard";
import { Globe, ChevronDown } from "lucide-react";

export function AuthLayout() {
  return (
    <div className="flex min-h-screen">
      {/* ── LEFT: Hero Panel (50% width on desktop) ── */}
      <div className="relative hidden w-1/2 overflow-hidden lg:block">
        <LoginHero />
      </div>

      {/* ── RIGHT: Login form panel ── */}
      <div
        className="relative flex w-full flex-col lg:w-1/2"
        style={{ background: "#F8FAFC" }}
      >
        {/* Top bar — language selector */}
        <div className="flex justify-end p-5 pr-7">
          <button
            type="button"
            className="flex items-center gap-1.5 rounded-lg border border-[#E2E8F0] bg-white px-3 py-1.5 text-xs font-semibold text-[#334155] shadow-sm hover:bg-[#F1F5F9] transition-colors"
          >
            <Globe className="h-3.5 w-3.5 text-[#64748B]" />
            <span>English</span>
            <ChevronDown className="h-3.5 w-3.5 text-[#64748B]" />
          </button>
        </div>

        {/* Centered login card */}
        <div className="flex flex-1 items-center justify-center px-6 pb-8 pt-4">
          <LoginCard />
        </div>
      </div>
    </div>
  );
}
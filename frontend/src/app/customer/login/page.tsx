"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Eye, EyeOff, Mail, Lock, Loader2, AlertCircle, ArrowRight, Sparkles, ChevronDown, Globe } from "lucide-react";
import { customersService } from "@/services/customers.service";

// No real customer authentication exists yet (customer portal has no
// backend session — see frontend/src/lib/http.ts's customer-route token
// skip, a known, documented limitation). This checks the entered email
// against real customer records in Postgres instead of a fully
// disconnected hardcoded name, so the session that results is tied to an
// actual customer row. Password is still a single shared demo value.
const DEMO_EMAIL = "fatima.lawati@example.com";
const DEMO_PASSWORD = "Demo@123";

export default function CustomerLoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [remember, setRemember] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setEmail(DEMO_EMAIL);
    setPassword(DEMO_PASSWORD);
    const saved = localStorage.getItem("demo-role");
    if (saved === "customer") {
      const session = localStorage.getItem("customer-session");
      if (session) {
        try {
          const parsed = JSON.parse(session);
          if (parsed?.email) {
            router.push("/customer/dashboard");
            return;
          }
        } catch {}
      }
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!email.trim() || !password.trim()) {
      setError("Please enter your email and password.");
      return;
    }
    setLoading(true);
    try {
      if (password !== DEMO_PASSWORD) {
        setError("Invalid email or password. Please try again.");
        return;
      }
      const res = await customersService.list({ page: 1, page_size: 100 });
      const customers = res.data.data ?? [];
      const matched = customers.find(
        (c) => c.email?.toLowerCase() === email.trim().toLowerCase(),
      );
      if (!matched) {
        setError("No customer account found for that email.");
        return;
      }
      const session = { id: String(matched.id), email: matched.email!, name: matched.full_name };
      localStorage.setItem("customer-session", JSON.stringify(session));
      sessionStorage.setItem("customer-session", JSON.stringify(session));
      localStorage.setItem("demo-role", "customer");
      router.push("/customer/dashboard");
    } catch {
      setError("Unable to verify your account right now. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* LEFT: Hero */}
      <div
        className="relative hidden w-1/2 flex-col overflow-hidden lg:flex"
        style={{
          background: "linear-gradient(155deg, #0F1F4B 0%, #1a3a8f 40%, #1E40AF 70%, #1D4ED8 100%)",
          padding: "48px 48px 40px",
        }}
      >
        <div aria-hidden="true" style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(circle, rgba(255,255,255,0.06) 1px, transparent 1px)", backgroundSize: "24px 24px", zIndex: 0 }} />
        <div aria-hidden="true" style={{ position: "absolute", top: -80, left: -80, width: 340, height: 340, borderRadius: "50%", background: "radial-gradient(circle, rgba(96,165,250,0.18) 0%, transparent 70%)", zIndex: 0 }} />
        <div className="relative z-10">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/15 backdrop-blur-sm border border-white/20">
              <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5 text-white">
                <path d="M12 3L4 7V13C4 18 8 21 12 22C16 21 20 18 20 13V7L12 3Z" fill="currentColor" opacity="0.3" />
                <path d="M12 8V16M8 12H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </div>
            <span className="text-xl font-black tracking-tight text-white">LuMay</span>
          </Link>
        </div>

        <div className="relative z-10 mt-12 space-y-4">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-white/20 bg-white/10 px-3.5 py-1 text-[10px] font-bold tracking-widest text-white/85 uppercase">
            <Sparkles className="h-3 w-3" />
            Customer Portal
          </span>
          <h1 style={{ fontSize: "clamp(1.5rem, 2.2vw, 1.9rem)", fontWeight: 900, lineHeight: 1.15, letterSpacing: "-0.02em", color: "#fff", margin: 0 }}>
            Your Insurance.
            <br />
            Your Way.
            <br />
            <span style={{ color: "#93C5FD" }}>Anytime.</span>
          </h1>
          <p style={{ fontSize: 13, lineHeight: 1.7, color: "rgba(255,255,255,0.68)", maxWidth: 370, margin: 0 }}>
            Access your policies, track claims, make payments, and connect with our AI support team — all in one place.
          </p>
        </div>

        <div className="relative z-10 mt-auto grid grid-cols-3 gap-3 border-t border-white/14 pt-5">
          {[
            { label: "AI Support", desc: "24/7 intelligent assistance" },
            { label: "Self-Service", desc: "Manage policies anytime" },
            { label: "Secure", desc: "Enterprise-grade security" },
          ].map((f) => (
            <div key={f.label}>
              <span style={{ fontSize: 11, fontWeight: 700, color: "#fff" }}>{f.label}</span>
              <p style={{ fontSize: 10, color: "rgba(255,255,255,0.5)", lineHeight: 1.4, margin: 0 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* RIGHT: Login Form */}
      <div className="relative flex w-full flex-col lg:w-1/2" style={{ background: "#F8FAFC" }}>
        <div className="flex justify-end p-5 pr-7">
          <button type="button" className="flex items-center gap-1.5 rounded-lg border border-[#E2E8F0] bg-white px-3 py-1.5 text-xs font-semibold text-[#334155] shadow-sm hover:bg-[#F1F5F9] transition-colors">
            <Globe className="h-3.5 w-3.5 text-[#64748B]" />
            <span>English</span>
            <ChevronDown className="h-3.5 w-3.5 text-[#64748B]" />
          </button>
        </div>

        <div className="flex flex-1 items-center justify-center px-6 pb-8 pt-4">
          <div className="w-full max-w-[460px] space-y-8">
            <div className="space-y-2 text-center">
              <h2 className="text-3xl font-extrabold tracking-tight text-[#0D1B3E]">Welcome Back</h2>
              <p className="text-sm font-medium text-[#64748B]">
                Sign in to your LuMay Insurance account
              </p>
            </div>

            <div className="rounded-3xl border border-[#E2E8F0] bg-white p-9 shadow-[0_12px_40px_rgba(0,82,255,0.04)]">
              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="flex items-center justify-center gap-2 rounded-xl bg-amber-50 border border-amber-200 px-3 py-2 text-[10px] font-bold text-amber-700 uppercase tracking-wider">
                  <Sparkles className="h-3 w-3" /> Demo Mode — credentials pre-filled
                </div>
                <div className="space-y-1.5">
                  <label htmlFor="email" className="text-sm font-semibold text-[#334155]">Email / Mobile Number</label>
                  <div className="relative">
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-[#94A3B8]">
                      <Mail className="h-4.5 w-4.5" />
                    </div>
                    <input id="email" type="text" placeholder="Enter your email or mobile" value={email} onChange={(e) => setEmail(e.target.value)} className="flex h-11 w-full rounded-xl border border-[#E2E8F0] bg-white pl-10 pr-3 py-2 text-sm text-[#0F172A] placeholder:text-[#94A3B8] outline-none transition-all duration-150 focus:border-[#0052FF] focus:ring-1 focus:ring-[#0052FF] hover:border-slate-300" />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label htmlFor="password" className="text-sm font-semibold text-[#334155]">Password</label>
                  <div className="relative">
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-[#94A3B8]">
                      <Lock className="h-4.5 w-4.5" />
                    </div>
                    <input id="password" type={showPw ? "text" : "password"} placeholder="Enter your password" value={password} onChange={(e) => setPassword(e.target.value)} className="flex h-11 w-full rounded-xl border border-[#E2E8F0] bg-white pl-10 pr-10 text-sm text-[#0F172A] placeholder:text-[#94A3B8] outline-none transition-all duration-150 focus:border-[#0052FF] focus:ring-1 focus:ring-[#0052FF] hover:border-slate-300" />
                    <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#94A3B8] hover:text-[#64748B] transition-colors" tabIndex={-1}>
                      {showPw ? <EyeOff className="h-4.5 w-4.5" /> : <Eye className="h-4.5 w-4.5" />}
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <label className="flex cursor-pointer items-center gap-2 text-sm text-[#64748B]">
                    <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} className="h-4 w-4 rounded border-[#E2E8F0] text-[#0052FF] focus:ring-[#0052FF]" />
                    Remember me
                  </label>
                  <button type="button" className="text-sm font-semibold text-[#0052FF] hover:text-[#0052FF]/85 transition-colors">
                    Forgot Password?
                  </button>
                </div>

                {error && (
                  <div className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-600">
                    <AlertCircle className="h-4 w-4 shrink-0" />
                    <span className="font-medium">{error}</span>
                  </div>
                )}

                <button type="submit" disabled={loading} className="flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-[#0052FF] text-sm font-semibold text-white shadow-md shadow-blue-500/10 transition-all hover:bg-blue-600 hover:shadow-lg hover:shadow-blue-500/15 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60">
                  {loading ? (
                    <><Loader2 className="h-4.5 w-4.5 animate-spin" /> Signing In...</>
                  ) : (
                    <><span>Login</span><ArrowRight className="h-4 w-4" /></>
                  )}
                </button>
              </form>
            </div>

            <div className="flex items-center justify-center gap-2 text-xs font-bold text-[#64748B]">
              <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4 stroke-[#94A3B8]">
                <path d="M12 22C12 22 20 18 20 12V5L12 2L4 5V12C4 18 12 22 12 22Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M9 11L11 13L15 9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              <span>Your data is protected with enterprise-grade security</span>
            </div>

            <div className="text-center">
              <Link href="/" className="text-sm font-semibold text-[#64748B] hover:text-[#0052FF] transition-colors">
                &larr; Back to Home
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

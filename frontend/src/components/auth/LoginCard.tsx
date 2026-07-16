import { LoginForm } from "@/components/auth/LoginForm";

export function LoginCard() {
  return (
    <div className="w-full max-w-[460px] space-y-8">
      {/* Header outside or top of card */}
      <div className="space-y-2 text-center">
        <h2 className="text-3xl font-extrabold tracking-tight text-[#0D1B3E]">Welcome Back</h2>
        <p className="text-sm font-medium text-[#64748B]">
          Sign in to your LuMay SMART AI Hub account
        </p>
      </div>

      {/* Login Card */}
      <div className="rounded-3xl border border-[#E2E8F0] bg-white p-9 shadow-[0_12px_40px_rgba(0,82,255,0.04)]">
        <LoginForm />
      </div>

      {/* Security Message */}
      <div className="flex items-center justify-center gap-2 text-xs font-bold text-[#64748B] transition-colors">
        <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4 stroke-[#94A3B8]" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 22C12 22 20 18 20 12V5L12 2L4 5V12C4 18 12 22 12 22Z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M9 11L11 13L15 9" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <span>Your data is protected with enterprise-grade security</span>
      </div>
    </div>
  );
}
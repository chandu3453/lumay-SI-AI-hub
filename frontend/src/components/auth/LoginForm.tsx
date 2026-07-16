import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2, AlertCircle, Mail, ArrowRight, Sparkles } from "lucide-react";

import { PasswordInput } from "@/components/auth/PasswordInput";
import { RememberMe } from "@/components/auth/RememberMe";
import { useAuthStore } from "@/stores/auth.store";
import { authService } from "@/services/auth.service";
import { setApiToken } from "@/lib/http";
import { ROUTES } from "@/lib/constants";

const DEMO_EMAIL = "admin@gmail.com";
const DEMO_PASSWORD = "Admin@123";

const loginSchema = z.object({
  email: z.string().min(1, "Email is required").email("Please enter a valid email"),
  password: z.string().min(1, "Password is required"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginForm() {
  const router = useRouter();
  const { setTokens, setUser } = useAuthStore();
  const [remember, setRemember] = useState(false);
  const [serverError, setServerError] = useState("");

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  useEffect(() => {
    setValue("email", DEMO_EMAIL);
    setValue("password", DEMO_PASSWORD);
    const saved = localStorage.getItem("demo-role");
    if (saved === "employee") {
      const stored = localStorage.getItem("auth-storage");
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          if (parsed?.state?.token) {
            router.push(ROUTES.DASHBOARD);
            return;
          }
        } catch {}
      }
    }
  }, [setValue, router]);

  const onSubmit = async (data: LoginFormData) => {
    setServerError("");
    try {
      const res = await authService.login(data);
      const tokens = res.data.data;
      setApiToken(tokens.access_token);
      setTokens(tokens.access_token, tokens.refresh_token);
      localStorage.setItem("demo-role", "employee");
      try {
        const userRes = await authService.me();
        setUser(userRes.data.data);
      } catch {}
      router.push(ROUTES.DASHBOARD);
    } catch (err: any) {
      const msg = err?.response?.data?.message || err?.response?.data?.detail || "Invalid email or password. Please try again.";
      setServerError(msg);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="flex items-center justify-center gap-2 rounded-xl bg-amber-50 border border-amber-200 px-3 py-2 text-[10px] font-bold text-amber-700 uppercase tracking-wider">
        <Sparkles className="h-3 w-3" /> Demo Mode — credentials pre-filled
      </div>

      <div className="space-y-1.5">
        <label htmlFor="email" className="text-sm font-semibold text-[#334155]">Email Address</label>
        <div className="relative">
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-[#94A3B8]"><Mail className="h-4.5 w-4.5" /></div>
          <input id="email" type="email" placeholder="Enter your email" className="flex h-11 w-full rounded-xl border border-[#E2E8F0] bg-white pl-10 pr-3 py-2 text-sm text-[#0F172A] placeholder:text-[#94A3B8] outline-none transition-all duration-150 focus:border-[#0052FF] focus:ring-1 focus:ring-[#0052FF] hover:border-slate-300" {...register("email")} />
        </div>
        {errors.email && <p className="text-xs text-red-500 font-medium">{errors.email.message}</p>}
      </div>

      <PasswordInput id="password" label="Password" placeholder="Enter your password" registration={register("password")} error={errors.password?.message} />

      <div className="flex items-center justify-between">
        <RememberMe checked={remember} onChange={setRemember} />
        <button type="button" className="text-sm font-semibold text-[#0052FF] hover:text-[#0052FF]/85 transition-colors">Forgot Password?</button>
      </div>

      {serverError && (
        <div className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-red-600">
          <AlertCircle className="h-4 w-4 shrink-0" /><span className="font-medium">{serverError}</span>
        </div>
      )}

      <button type="submit" disabled={isSubmitting} className="flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-[#0052FF] text-sm font-semibold text-white shadow-md shadow-blue-500/10 transition-all hover:bg-blue-600 hover:shadow-lg hover:shadow-blue-500/15 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60">
        {isSubmitting ? <><Loader2 className="h-4.5 w-4.5 animate-spin" /> Signing In...</> : <><span>Sign In</span><ArrowRight className="h-4 w-4" /></>}
      </button>

      <div className="pt-2 text-center text-sm font-medium text-[#64748B]">
        Don't have an account?{" "}
        <button type="button" className="font-bold text-[#0052FF] hover:text-blue-700 transition-colors">Request Demo</button>
      </div>
    </form>
  );
}
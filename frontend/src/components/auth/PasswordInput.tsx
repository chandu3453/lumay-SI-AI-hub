import { useState } from "react";
import { Eye, EyeOff, Lock } from "lucide-react";
import { cn } from "@/lib/cn";
import { type UseFormRegisterReturn } from "react-hook-form";

type PasswordInputProps = {
  id: string;
  label: string;
  placeholder?: string;
  error?: string;
  registration: UseFormRegisterReturn;
};

export function PasswordInput({ id, label, placeholder = "Enter your password", error, registration }: PasswordInputProps) {
  const [show, setShow] = useState(false);

  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="text-sm font-semibold text-[#334155]">
        {label}
      </label>
      <div className="relative">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 text-[#94A3B8]">
          <Lock className="h-4.5 w-4.5" />
        </div>
        <input
          id={id}
          type={show ? "text" : "password"}
          placeholder={placeholder}
          className={cn(
            "flex h-11 w-full rounded-xl border border-[#E2E8F0] bg-white pl-10 pr-10 text-sm text-[#0F172A] placeholder:text-[#94A3B8] outline-none transition-all duration-150",
            "focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB]",
            error ? "border-red-400 focus:border-red-400 focus:ring-red-400" : "hover:border-slate-300"
          )}
          {...registration}
        />
        <button
          type="button"
          onClick={() => setShow(!show)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-[#94A3B8] hover:text-[#64748B] transition-colors"
          tabIndex={-1}
        >
          {show ? <EyeOff className="h-4.5 w-4.5" /> : <Eye className="h-4.5 w-4.5" />}
        </button>
      </div>
      {error && <p className="text-xs text-red-500 font-medium">{error}</p>}
    </div>
  );
}
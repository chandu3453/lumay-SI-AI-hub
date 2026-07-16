"use client";

import { cn } from "@/lib/cn";

type RememberMeProps = {
  checked: boolean;
  onChange: (checked: boolean) => void;
};

export function RememberMe({ checked, onChange }: RememberMeProps) {
  return (
    <label className="flex cursor-pointer items-center gap-2 text-sm text-[#64748B]">
      <div
        className={cn(
          "flex h-4 w-4 items-center justify-center rounded border transition-colors",
          checked ? "border-[#2563EB] bg-[#2563EB]" : "border-[#E2E8F0] bg-white",
        )}
        onClick={() => onChange(!checked)}
      >
        {checked && (
          <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        )}
      </div>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="sr-only"
      />
      Remember me
    </label>
  );
}
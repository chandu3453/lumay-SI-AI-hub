import { cn } from "@/lib/cn";

type LogoProps = {
  className?: string;
  iconOnly?: boolean;
  inline?: boolean;
  withSubtitle?: boolean;
};

export function Logo({ className, iconOnly, inline = false, withSubtitle = false }: LogoProps) {
  return (
    <div className={cn("flex items-center gap-3", className)}>
      {/* SVG Shield Icon */}
      <div className="flex h-10 w-10 shrink-0 items-center justify-center">
        <svg viewBox="0 0 40 40" fill="none" className="h-full w-full" xmlns="http://www.w3.org/2000/svg">
          {/* Blue Shield Path */}
          <path
            d="M20 3L6 8.25V18.75C6 27.67 12 34.95 20 37C28 34.95 34 27.67 34 18.75V8.25L20 3Z"
            fill="#E0F2FE"
            stroke="#2563EB"
            strokeWidth="3"
            strokeLinejoin="round"
          />
          {/* Green Inner Cross Shield */}
          <path
            d="M20 11V27M12 19H28"
            stroke="#10B981"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>

      {!iconOnly && (
        <div className="flex items-center">
          <div className={cn("flex", inline ? "items-center gap-1.5" : "flex-col -space-y-1.5")}>
            <span className="text-xl font-bold tracking-tight text-[#0F172A]">LuMay</span>
            <span className="text-[13px] font-semibold tracking-wider text-[#10B981] uppercase">Insurance</span>
          </div>

          {withSubtitle && (
            <>
              <div className="mx-4 h-8 w-[1px] bg-slate-200" />
              <div className="flex flex-col -space-y-1 text-left">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">SMART</span>
                <span className="text-sm font-semibold tracking-tight text-[#0F172A]">Insurance AI Hub</span>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
import { type ReactNode } from "react";
import { cn } from "@/lib/cn";

type SectionTitleProps = {
  label?: string;
  title: string;
  description?: string;
  align?: "center" | "left";
  className?: string;
  children?: ReactNode;
};

export function SectionTitle({ label, title, description, align = "center", className, children }: SectionTitleProps) {
  return (
    <div className={cn("space-y-4", align === "center" ? "text-center" : "text-left", className)}>
      {label && (
        <span className="inline-flex items-center rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-xs font-medium text-primary">
          {label}
        </span>
      )}
      <h2 className="text-3xl font-semibold tracking-tight text-[#0F172A] sm:text-4xl">{title}</h2>
      {description && <p className="mx-auto max-w-2xl text-lg leading-relaxed text-[#64748B]">{description}</p>}
      {children}
    </div>
  );
}
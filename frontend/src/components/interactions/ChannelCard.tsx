"use client";

import { cn } from "@/lib/cn";
import { Badge } from "@/components/ui/badge";

type ChannelCardProps = {
  icon: React.ReactNode;
  name: string;
  count: number;
  isActive: boolean;
  onClick: () => void;
};

export function ChannelCard({ icon, name, count, isActive, onClick }: ChannelCardProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 px-4 py-3 rounded-xl border transition-all duration-150 text-left",
        "hover:shadow-sm",
        isActive
          ? "border-primary bg-primary/5 shadow-sm"
          : "border-border bg-white dark:bg-card hover:border-primary/30",
      )}
    >
      <span className={cn("shrink-0", isActive ? "text-primary" : "text-muted-foreground")}>
        {icon}
      </span>
      <span className={cn("text-sm font-medium flex-1", isActive ? "text-primary" : "text-foreground")}>
        {name}
      </span>
      <Badge variant={isActive ? "default" : "neutral"} className="shrink-0">
        {count}
      </Badge>
    </button>
  );
}
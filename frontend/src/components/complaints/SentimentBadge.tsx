"use client";

import { cn } from "@/lib/cn";
import { Smile, Meh, Frown } from "lucide-react";

type SentimentBadgeProps = {
  sentiment: string | null | undefined;
};

const sentimentConfig: Record<string, { icon: React.ReactNode; label: string; color: string }> = {
  positive: { icon: <Smile className="h-3.5 w-3.5" />, label: "Positive", color: "text-success" },
  neutral: { icon: <Meh className="h-3.5 w-3.5" />, label: "Neutral", color: "text-muted-foreground" },
  negative: { icon: <Frown className="h-3.5 w-3.5" />, label: "Negative", color: "text-destructive" },
};

export function SentimentBadge({ sentiment }: SentimentBadgeProps) {
  if (!sentiment) return <span className="text-sm text-muted-foreground">—</span>;

  const config = sentimentConfig[sentiment];
  if (!config) return <span className="text-sm text-muted-foreground capitalize">{sentiment}</span>;

  return (
    <div className={cn("flex items-center gap-1", config.color)}>
      {config.icon}
      <span className="text-xs font-medium">{config.label}</span>
    </div>
  );
}
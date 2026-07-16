"use client";

import { Card, CardContent } from "@/components/ui/card";

type PolicyCardProps = {
  productName: string;
  policyNumber: string;
  status: "active" | "expiring" | "lapsed" | "pending";
  line: string;
};

const statusColors: Record<string, string> = {
  active: "text-[#16A34A]",
  expiring: "text-[#F59E0B]",
  lapsed: "text-[#DC2626]",
  pending: "text-[#64748B]",
};

const lineInitials: Record<string, string> = {
  Motor: "M",
  "Medical & Health": "H",
  Travel: "T",
  Home: "Ho",
  Life: "L",
  "Business Insurance": "B",
};

const lineBgColors: Record<string, string> = {
  Motor: "bg-[#EFF6FF] text-[#2563EB]",
  "Medical & Health": "bg-[#F0FDF4] text-[#16A34A]",
  Travel: "bg-[#F5F3FF] text-[#8B5CF6]",
  Home: "bg-[#FFFBEB] text-[#F59E0B]",
  Life: "bg-[#FDF2F8] text-[#EC4899]",
  "Business Insurance": "bg-[#ECFEFF] text-[#06B6D4]",
};

export function PolicyCard({ productName, policyNumber, status, line }: PolicyCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="pt-5">
        <div className={`h-9 w-9 rounded-lg flex items-center justify-center text-xs font-bold mb-3 ${lineBgColors[line] ?? "bg-muted text-muted-foreground"}`}>
          {lineInitials[line] ?? line.slice(0, 2)}
        </div>
        <p className="text-sm font-medium text-[#0F172A] truncate">{productName}</p>
        <p className="text-xs font-mono text-muted-foreground mt-1">{policyNumber}</p>
        <p className={`text-xs font-medium mt-2 ${statusColors[status] ?? "text-muted-foreground"}`}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </p>
      </CardContent>
    </Card>
  );
}

"use client";

import { ChevronRight } from "lucide-react";

type UserProfileCardProps = {
  name?: string;
  email?: string;
  initials?: string;
};

export function UserProfileCard({ name = "Admin User", email = "admin@lumay.ai", initials = "AD" }: UserProfileCardProps) {
  return (
    <div className="flex items-center gap-3 rounded-lg bg-[#F8FAFC] p-3">
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#2563EB]/10 text-[#2563EB] text-xs font-semibold">
        {initials}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-[#0F172A] truncate">{name}</p>
        <p className="text-xs text-[#94A3B8] truncate">{email}</p>
      </div>
      <ChevronRight className="h-4 w-4 text-[#94A3B8]" />
    </div>
  );
}
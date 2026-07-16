"use client";

import { Bell, HelpCircle, User } from "lucide-react";
import { GlobalSearch } from "@/components/dashboard/GlobalSearch";
import { DateFilter } from "@/components/dashboard/DateFilter";
import { ChannelFilter } from "@/components/dashboard/ChannelFilter";

export function Header() {
  return (
    <header className="flex h-16 items-center gap-4 border-b border-[#E2E8F0] bg-white px-6">
      <GlobalSearch />
      <DateFilter />
      <ChannelFilter />
      <div className="flex items-center gap-2 ml-auto">
        <button className="flex h-9 w-9 items-center justify-center rounded-lg text-[#94A3B8] hover:bg-[#F8FAFC] hover:text-[#64748B] transition-colors">
          <HelpCircle className="h-4 w-4" />
        </button>
        <button className="flex h-9 w-9 items-center justify-center rounded-lg text-[#94A3B8] hover:bg-[#F8FAFC] hover:text-[#64748B] transition-colors relative">
          <Bell className="h-4 w-4" />
          <span className="absolute top-2.5 right-2.5 h-1.5 w-1.5 rounded-full bg-[#DC2626]" />
        </button>
        <button className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#2563EB]/10 text-[#2563EB]">
          <User className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}
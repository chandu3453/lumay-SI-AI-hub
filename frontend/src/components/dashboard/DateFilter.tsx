"use client";

export function DateFilter() {
  return (
    <select className="flex h-9 items-center rounded-lg border border-[#E2E8F0] bg-white px-3 text-sm text-[#0F172A] outline-none focus:border-[#2563EB] focus:ring-1 focus:ring-[#2563EB]">
      <option value="today">Today</option>
      <option value="this-week" selected>This Week</option>
      <option value="this-month">This Month</option>
      <option value="last-month">Last Month</option>
      <option value="custom">Custom Range</option>
    </select>
  );
}
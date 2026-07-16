"use client";

import Link from "next/link";
import { useState } from "react";
import { Menu, X, ChevronDown } from "lucide-react";
import { Container } from "@/components/landing/Container";
import { Logo } from "@/components/auth/Logo";

const NAV_ITEMS = [
  { label: "Products", href: "#", hasDropdown: true },
  { label: "Solutions", href: "#", hasDropdown: true },
  { label: "Resources", href: "#", hasDropdown: true },
  { label: "About Us", href: "#", hasDropdown: false },
  { label: "Contact Us", href: "#", hasDropdown: false },
];

export function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-[#E2E8F0] bg-white/95 backdrop-blur-sm shadow-[0_2px_15px_rgb(0,0,0,0.02)]">
      <Container>
        <div className="flex h-20 items-center justify-between">
          {/* Logo with separator & subtitle */}
          <Link href="/" className="hover:opacity-95 transition-opacity">
            <Logo withSubtitle={true} />
          </Link>

          {/* Navigation Items */}
          <nav className="hidden items-center gap-8 lg:flex">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="group flex items-center gap-1 text-sm font-semibold text-[#475569] transition-colors hover:text-[#0F172A]"
              >
                <span>{item.label}</span>
                {item.hasDropdown && (
                  <ChevronDown className="h-4 w-4 text-[#94A3B8] group-hover:text-[#475569] transition-colors" />
                )}
              </Link>
            ))}
          </nav>

          {/* Action Buttons */}
          <div className="hidden items-center gap-3 lg:flex">
            <Link
              href="/customer/login"
              className="rounded-xl border border-[#D8E2EF] bg-white px-4 py-2.5 text-sm font-bold text-[#0052FF] shadow-sm hover:bg-slate-50 transition-all active:scale-[0.98]"
            >
              Customer Login
            </Link>
            <Link
              href="/login"
              className="rounded-xl border border-[#D8E2EF] bg-white px-4 py-2.5 text-sm font-bold text-[#0D1B3E] shadow-sm hover:bg-slate-50 transition-all active:scale-[0.98]"
            >
              Employee Login
            </Link>
            <Link
              href="/login"
              className="rounded-xl bg-[#0052FF] px-4 py-2.5 text-sm font-bold text-white shadow-md shadow-blue-500/10 hover:bg-blue-600 hover:shadow-lg hover:shadow-blue-500/15 transition-all active:scale-[0.98]"
            >
              Request Demo
            </Link>
          </div>

          {/* Mobile menu toggle */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="flex items-center justify-center rounded-xl p-2.5 text-[#64748B] hover:bg-[#F8FAFC] lg:hidden"
          >
            {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </Container>

      {/* Mobile nav drawer */}
      {mobileOpen && (
        <div className="border-t border-[#E2E8F0] bg-white px-6 pb-6 pt-3 lg:hidden shadow-lg animate-fade-in">
          <nav className="flex flex-col gap-2">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="flex items-center justify-between rounded-xl px-4 py-3 text-sm font-semibold text-[#475569] hover:bg-[#F8FAFC] hover:text-[#0F172A]"
              >
                <span>{item.label}</span>
                {item.hasDropdown && <ChevronDown className="h-4 w-4 text-[#94A3B8]" />}
              </Link>
            ))}
            <hr className="my-3 border-[#E2E8F0]" />
            <div className="flex flex-col gap-3">
              <Link
                href="/customer/login"
                className="rounded-xl border border-[#D8E2EF] py-3 text-center text-sm font-bold text-[#0052FF] hover:bg-slate-50"
              >
                Customer Login
              </Link>
              <Link
                href="/login"
                className="rounded-xl border border-[#D8E2EF] py-3 text-center text-sm font-bold text-[#0D1B3E] hover:bg-slate-50"
              >
                Employee Login
              </Link>
              <Link
                href="/login"
                className="rounded-xl bg-[#0052FF] py-3 text-center text-sm font-bold text-white shadow-md"
              >
                Request Demo
              </Link>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}
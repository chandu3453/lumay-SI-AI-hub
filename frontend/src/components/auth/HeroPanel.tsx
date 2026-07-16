"use client";

import { Logo } from "@/components/auth/Logo";
import { Sparkles, Headphones, ShieldCheck } from "lucide-react";
import Image from "next/image";

export function HeroPanel() {
  return (
    <div className="relative flex h-full flex-col justify-between p-12">
      {/* Top Logo */}
      <div className="relative z-10">
        <Logo />
      </div>

      {/* Hero content */}
      <div className="relative z-10 mt-8 space-y-6">
        {/* Badge */}
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-50 border border-blue-200/50 px-3.5 py-1 text-xs font-semibold uppercase tracking-wider text-blue-600">
            <Sparkles className="h-3.5 w-3.5" />
            AI-Powered Insurance Operations
          </span>
        </div>

        {/* Heading */}
        <h1 className="text-4xl font-extrabold leading-tight tracking-tight text-[#0F172A] xl:text-[42px]">
          Intelligent Complaints.
          <br />
          Happier Customers.
          <br />
          Stronger <span className="text-blue-600">Insurance.</span>
        </h1>

        {/* Description */}
        <p className="max-w-md text-[14px] leading-relaxed text-[#475569]">
          LuMay SMART Insurance AI Hub transforms every customer interaction into actionable intelligence with real-time detection, sentiment analysis, and escalation management.
        </p>
      </div>

      {/* 3D Pedestal Illustration */}
      <div className="relative my-6 flex flex-1 items-center justify-center">
        <div className="relative aspect-square w-full max-w-[280px] xl:max-w-[320px]">
          <Image
            src="/images/shield_illustration.png"
            alt="LuMay SMART Insurance Shield"
            fill
            className="object-contain"
            priority
          />
        </div>
      </div>

      {/* Bottom Features Footer (3 columns) */}
      <div className="relative z-10 grid grid-cols-3 gap-4 border-t border-slate-200/60 pt-6">
        {/* Col 1 */}
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
              <Sparkles className="h-4 w-4" />
            </div>
            <span className="text-xs font-bold text-[#0F172A]">AI-Powered</span>
          </div>
          <p className="text-[10px] leading-normal text-[#64748B]">
            Detect, analyze & act in real-time
          </p>
        </div>

        {/* Col 2 */}
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
              <Headphones className="h-4 w-4" />
            </div>
            <span className="text-xs font-bold text-[#0F172A]">Omnichannel</span>
          </div>
          <p className="text-[10px] leading-normal text-[#64748B]">
            Voice, chat, email, WhatsApp & more
          </p>
        </div>

        {/* Col 3 */}
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
              <ShieldCheck className="h-4 w-4" />
            </div>
            <span className="text-xs font-bold text-[#0F172A]">Enterprise Ready</span>
          </div>
          <p className="text-[10px] leading-normal text-[#64748B]">
            Secure, scalable & compliant
          </p>
        </div>
      </div>
    </div>
  );
}
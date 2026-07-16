"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquare, PhoneCall, Mail, Bot } from "lucide-react";

export default function CommunicationLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  const channels = [
    { name: "Web Chat", href: "/customer/communication/chat", icon: MessageSquare, color: "text-blue-500", bg: "bg-blue-50" },
    { name: "Voice Support", href: "/customer/communication/voice", icon: PhoneCall, color: "text-orange-500", bg: "bg-orange-50" },
    { name: "WhatsApp", href: "/customer/communication/whatsapp", icon: MessageSquare, color: "text-emerald-500", bg: "bg-emerald-50" },
    { name: "Email", href: "/customer/communication/email", icon: Mail, color: "text-purple-500", bg: "bg-purple-50" },
  ];

  return (
    <div className="flex h-full min-h-[calc(100vh-80px)]">
      {/* Communication Inner Sidebar */}
      <div className="w-64 bg-white border-r border-[#E2E8F0] p-4 hidden md:block">
        <div className="flex items-center gap-2 mb-6 px-2">
          <Bot className="h-5 w-5 text-[#0052FF]" />
          <h2 className="text-sm font-bold text-[#0D1B3E]">Channels</h2>
        </div>
        <div className="space-y-1">
          {channels.map((ch) => {
            const isActive = pathname === ch.href;
            const Icon = ch.icon;
            return (
              <Link 
                key={ch.href} 
                href={ch.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-colors ${
                  isActive ? "bg-slate-50 border border-[#E2E8F0] shadow-sm" : "hover:bg-slate-50 border border-transparent"
                }`}
              >
                <div className={`h-8 w-8 rounded-lg ${ch.bg} flex items-center justify-center`}>
                  <Icon className={`h-4 w-4 ${ch.color}`} />
                </div>
                <span className={`text-sm ${isActive ? "font-bold text-[#0D1B3E]" : "font-medium text-slate-600"}`}>
                  {ch.name}
                </span>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Main Channel Content */}
      <div className="flex-1 overflow-hidden bg-[#F8FAFC]">
        {children}
      </div>
    </div>
  );
}

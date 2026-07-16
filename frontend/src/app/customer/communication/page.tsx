"use client";

import Link from "next/link";
import { MessageSquare, PhoneCall, Mail, ArrowRight, Bot } from "lucide-react";

export default function CustomerCommunicationPage() {
  return (
    <div className="p-6 sm:p-8 space-y-8 animate-fade-in max-w-5xl mx-auto h-full flex flex-col justify-center min-h-[80vh]">
      <div className="text-center max-w-2xl mx-auto mb-10">
        <div className="h-20 w-20 bg-blue-100 text-[#0052FF] rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-inner">
          <Bot className="h-10 w-10" />
        </div>
        <h1 className="text-4xl font-black text-[#0D1B3E] mb-4">Communication Center</h1>
        <p className="text-base text-slate-500">Choose how you want to talk with LuMay AI. All channels are connected to your single, continuous interaction history.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Link href="/customer/communication/chat" className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all group flex flex-col items-center text-center">
          <div className="h-16 w-16 rounded-2xl bg-blue-50 text-blue-500 flex items-center justify-center mb-6 shadow-inner group-hover:scale-110 transition-transform">
            <MessageSquare className="h-8 w-8" />
          </div>
          <h3 className="text-lg font-bold text-[#0D1B3E] mb-2">Web Chat</h3>
          <p className="text-xs text-slate-500 mb-6">Chat with our AI assistant directly on the portal.</p>
          <div className="mt-auto flex items-center text-xs font-bold text-[#0052FF]">
            Start Chat <ArrowRight className="h-4 w-4 ml-1" />
          </div>
        </Link>
        
        <Link href="/customer/communication/voice" className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all group flex flex-col items-center text-center">
          <div className="h-16 w-16 rounded-2xl bg-green-50 text-green-500 flex items-center justify-center mb-6 shadow-inner group-hover:scale-110 transition-transform">
            <PhoneCall className="h-8 w-8" />
          </div>
          <h3 className="text-lg font-bold text-[#0D1B3E] mb-2">Voice Support</h3>
          <p className="text-xs text-slate-500 mb-6">Talk to our AI agent using your microphone.</p>
          <div className="mt-auto flex items-center text-xs font-bold text-[#0052FF]">
            Call Now <ArrowRight className="h-4 w-4 ml-1" />
          </div>
        </Link>

        <Link href="/customer/communication/whatsapp" className="bg-[#E7F5E9] border border-[#25D366]/30 rounded-[24px] p-6 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all group flex flex-col items-center text-center relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <MessageSquare className="h-24 w-24 text-[#25D366]" />
          </div>
          <div className="relative z-10">
            <div className="h-16 w-16 rounded-2xl bg-white text-[#25D366] flex items-center justify-center mx-auto mb-6 shadow-sm group-hover:scale-110 transition-transform">
              <MessageSquare className="h-8 w-8" />
            </div>
            <h3 className="text-lg font-bold text-[#0D1B3E] mb-2">WhatsApp</h3>
            <p className="text-xs text-slate-600 mb-6">Experience our WhatsApp integrated AI assistant.</p>
            <div className="mt-auto flex items-center justify-center text-xs font-bold text-[#25D366]">
              Open WhatsApp <ArrowRight className="h-4 w-4 ml-1" />
            </div>
          </div>
        </Link>
        
        <Link href="/customer/communication/email" className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all group flex flex-col items-center text-center">
          <div className="h-16 w-16 rounded-2xl bg-purple-50 text-purple-500 flex items-center justify-center mb-6 shadow-inner group-hover:scale-110 transition-transform">
            <Mail className="h-8 w-8" />
          </div>
          <h3 className="text-lg font-bold text-[#0D1B3E] mb-2">Email</h3>
          <p className="text-xs text-slate-500 mb-6">Send and receive emails from our AI processing engine.</p>
          <div className="mt-auto flex items-center text-xs font-bold text-[#0052FF]">
            Compose <ArrowRight className="h-4 w-4 ml-1" />
          </div>
        </Link>
      </div>
    </div>
  );
}

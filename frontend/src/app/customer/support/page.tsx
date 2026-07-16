"use client";

import Link from "next/link";
import { HelpCircle, MessageSquare, PhoneCall, Mail, FileText, Search, BookOpen, AlertCircle, PlusCircle, ArrowRight } from "lucide-react";

export default function CustomerSupportPage() {
  return (
    <div className="p-6 sm:p-8 space-y-8 animate-fade-in max-w-5xl mx-auto">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto mb-10">
        <div className="h-16 w-16 bg-blue-50 text-[#0052FF] rounded-3xl flex items-center justify-center mx-auto mb-4">
          <HelpCircle className="h-8 w-8" />
        </div>
        <h1 className="text-3xl font-black text-[#0D1B3E] mb-3">How can we help you?</h1>
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search for answers (e.g., How to file a claim?)" 
            className="w-full pl-12 pr-4 py-4 bg-white border border-[#E2E8F0] rounded-2xl text-sm focus:outline-none focus:border-[#0052FF] shadow-sm"
          />
        </div>
      </div>

      {/* Support Options Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link href="/customer/communication/chat" className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm hover:shadow-lg transition-all group flex flex-col justify-between">
          <div>
            <div className="h-14 w-14 rounded-2xl bg-emerald-50 text-emerald-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <MessageSquare className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-bold text-[#0D1B3E] mb-2">Live AI Chat</h3>
            <p className="text-xs text-slate-500 leading-relaxed">Get instant answers to your questions, 24/7. Our AI assistant is ready to help with claims, policies, and more.</p>
          </div>
          <div className="mt-6 flex items-center text-xs font-bold text-[#0052FF]">
            Start Chat <ArrowRight className="h-4 w-4 ml-1" />
          </div>
        </Link>
        
        <Link href="/customer/communication/voice" className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm hover:shadow-lg transition-all group flex flex-col justify-between">
          <div>
            <div className="h-14 w-14 rounded-2xl bg-blue-50 text-blue-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <PhoneCall className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-bold text-[#0D1B3E] mb-2">Call Support</h3>
            <p className="text-xs text-slate-500 leading-relaxed">Prefer talking? Use our voice AI support or get connected to a human agent immediately.</p>
          </div>
          <div className="mt-6 flex items-center text-xs font-bold text-[#0052FF]">
            Call Now <ArrowRight className="h-4 w-4 ml-1" />
          </div>
        </Link>
        
        <Link href="/customer/communication/email" className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm hover:shadow-lg transition-all group flex flex-col justify-between">
          <div>
            <div className="h-14 w-14 rounded-2xl bg-purple-50 text-purple-500 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
              <Mail className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-bold text-[#0D1B3E] mb-2">Email Support</h3>
            <p className="text-xs text-slate-500 leading-relaxed">Send us a detailed message with attachments, and we'll get back to you within 24 hours.</p>
          </div>
          <div className="mt-6 flex items-center text-xs font-bold text-[#0052FF]">
            Send Email <ArrowRight className="h-4 w-4 ml-1" />
          </div>
        </Link>
      </div>

      {/* Second Row Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm">
          <h3 className="text-base font-bold text-[#0D1B3E] mb-4 flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-blue-500" /> Knowledge Base & FAQs
          </h3>
          <div className="space-y-3">
            {[
              "How do I file a motor insurance claim?",
              "What is covered under Medical Elite?",
              "How to download my policy certificate?",
              "What to do in case of an accident?",
              "How to add a family member to my policy?"
            ].map((q, i) => (
              <div key={i} className="flex justify-between items-center p-4 rounded-xl border border-transparent hover:border-[#E2E8F0] hover:bg-slate-50 cursor-pointer transition-colors">
                <span className="text-sm font-medium text-[#0D1B3E]">{q}</span>
                <ArrowRight className="h-4 w-4 text-slate-400" />
              </div>
            ))}
          </div>
          <button className="w-full mt-4 py-2.5 text-[#0052FF] text-sm font-bold hover:bg-blue-50 rounded-xl transition-colors">
            View All Articles
          </button>
        </div>

        <div className="space-y-6">
          <div className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm flex flex-col justify-center items-center text-center">
            <AlertCircle className="h-10 w-10 text-red-500 mb-3" />
            <h3 className="text-base font-bold text-[#0D1B3E]">Not Satisfied?</h3>
            <p className="text-xs text-slate-500 mt-2 mb-4">We take your concerns seriously. If you have a complaint, let us know.</p>
            <button className="w-full py-2.5 rounded-xl bg-red-50 text-red-600 font-bold text-sm hover:bg-red-100 transition-colors flex items-center justify-center gap-2">
              <PlusCircle className="h-4 w-4" /> Raise Complaint
            </button>
          </div>

          <div className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm flex flex-col justify-center items-center text-center">
            <FileText className="h-10 w-10 text-amber-500 mb-3" />
            <h3 className="text-base font-bold text-[#0D1B3E]">Forms & Documents</h3>
            <p className="text-xs text-slate-500 mt-2 mb-4">Download claim forms, medical network guides, and policy wordings.</p>
            <button className="w-full py-2.5 rounded-xl border border-[#E2E8F0] text-slate-600 font-bold text-sm hover:bg-slate-50 transition-colors">
              Download Forms
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

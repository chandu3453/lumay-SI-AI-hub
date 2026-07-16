"use client";

import { RefreshCw, Calendar, ArrowRight, CheckCircle2, AlertCircle } from "lucide-react";

export default function CustomerRenewalsPage() {
  return (
    <div className="p-6 sm:p-8 space-y-8 animate-fade-in max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl font-black text-[#0D1B3E]">Renewals</h1>
        <p className="text-sm text-slate-500 mt-1">Manage your upcoming and expired policy renewals.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <h2 className="text-lg font-bold text-[#0D1B3E] flex items-center gap-2">
            <Calendar className="h-5 w-5 text-blue-500" /> Upcoming Renewals
          </h2>
          
          {/* Renewal Card */}
          <div className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-600 border border-amber-200">
                <AlertCircle className="h-3.5 w-3.5 mr-1.5" /> Due in 30 days
              </span>
            </div>
            
            <div className="flex gap-4">
              <div className="h-14 w-14 rounded-2xl bg-blue-50 flex items-center justify-center text-2xl shadow-inner">✈️</div>
              <div>
                <h3 className="text-lg font-black text-[#0D1B3E]">Travel Global</h3>
                <p className="text-xs text-slate-400 font-mono mt-0.5">POL-77112-22</p>
                <div className="mt-4 grid grid-cols-2 gap-x-8 gap-y-2">
                  <div>
                    <p className="text-xs text-slate-500">Current Expiry</p>
                    <p className="text-sm font-bold text-[#0D1B3E]">01 Sep 2026</p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">Renewal Premium</p>
                    <p className="text-sm font-black text-[#0052FF]">OMR 180 /yr</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-6 pt-6 border-t border-[#E2E8F0] flex gap-3">
              <button className="flex-1 py-3 rounded-xl bg-[#0052FF] text-white text-sm font-bold hover:bg-blue-600 transition-colors flex items-center justify-center gap-2">
                <RefreshCw className="h-4 w-4" /> Renew Now
              </button>
              <button className="flex-1 py-3 rounded-xl border border-[#E2E8F0] text-slate-600 text-sm font-bold hover:bg-slate-50 transition-colors">
                View Quote
              </button>
            </div>
          </div>

          <h2 className="text-lg font-bold text-[#0D1B3E] flex items-center gap-2 mt-10">
            <CheckCircle2 className="h-5 w-5 text-emerald-500" /> Completed Renewals
          </h2>
          <div className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm">
            <div className="flex justify-between items-center">
              <div className="flex gap-4 items-center">
                <div className="h-10 w-10 rounded-xl bg-slate-50 flex items-center justify-center text-lg">🚗</div>
                <div>
                  <h4 className="text-sm font-bold text-[#0D1B3E]">Motor Comprehensive</h4>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">Renewed on 15 Mar 2026</p>
                </div>
              </div>
              <span className="text-xs font-bold text-emerald-600">Active until Mar 2027</span>
            </div>
          </div>
        </div>

        {/* Sidebar recommendations */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-[#0d1b3e] to-[#0038ff] rounded-[24px] p-6 text-white shadow-xl">
            <h3 className="text-sm font-bold text-blue-200 mb-2">Upgrade Recommendation</h3>
            <h2 className="text-2xl font-black mb-2">Medical Elite Plus</h2>
            <p className="text-xs text-blue-100 mb-6 leading-relaxed">Add worldwide coverage to your existing medical plan for just OMR 250 extra per year.</p>
            <button className="w-full py-2.5 bg-white text-[#0052FF] rounded-xl text-sm font-bold shadow-sm hover:bg-blue-50 transition-colors flex items-center justify-center gap-2">
              Upgrade Plan <ArrowRight className="h-4 w-4" />
            </button>
          </div>

          <div className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm">
            <h3 className="text-sm font-bold text-[#0D1B3E] mb-4">Renewal Timeline</h3>
            <div className="space-y-4">
              <div className="flex gap-3">
                <div className="mt-1"><CheckCircle2 className="h-4 w-4 text-emerald-500" /></div>
                <div>
                  <p className="text-xs font-bold text-[#0D1B3E]">Reminder Sent</p>
                  <p className="text-[10px] text-slate-400">01 Aug 2026</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="mt-1"><RefreshCw className="h-4 w-4 text-blue-500 animate-spin-slow" /></div>
                <div>
                  <p className="text-xs font-bold text-[#0D1B3E]">Action Required</p>
                  <p className="text-[10px] text-slate-400">Pending renewal</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

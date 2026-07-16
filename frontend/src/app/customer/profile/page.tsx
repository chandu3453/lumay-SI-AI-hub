"use client";

import { User, Shield, Bell, MapPin, Phone, Mail, Lock, Settings, CreditCard, Sparkles } from "lucide-react";

export default function CustomerProfilePage() {
  return (
    <div className="p-6 sm:p-8 space-y-8 animate-fade-in max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-black text-[#0D1B3E]">My Profile</h1>
        <p className="text-sm text-slate-500 mt-1">Manage your personal information, security, and preferences.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Avatar & Quick Stats */}
        <div className="space-y-6">
          <div className="bg-white border border-[#E2E8F0] rounded-[24px] p-8 shadow-sm flex flex-col items-center text-center">
            <div className="h-24 w-24 rounded-full bg-blue-100 text-[#0052FF] flex items-center justify-center font-black text-3xl uppercase mb-4 shadow-inner">
              FA
            </div>
            <h2 className="text-xl font-black text-[#0D1B3E]">Fatima Al Lawati</h2>
            <div className="flex items-center gap-1.5 mt-2 px-3 py-1 bg-amber-50 rounded-full border border-amber-200">
              <Sparkles className="h-3 w-3 text-amber-500" />
              <span className="text-[10px] font-bold text-amber-700 uppercase tracking-wider">VIP Member</span>
            </div>
            <p className="text-xs text-slate-500 mt-4 font-medium">fatima.lawati@email.com</p>
            <p className="text-xs text-slate-500 mt-1 font-medium">+968 9912 3456</p>
          </div>

          <div className="bg-white border border-[#E2E8F0] rounded-[24px] shadow-sm overflow-hidden">
            <div className="p-4 border-b border-[#E2E8F0] bg-slate-50/50">
              <h3 className="text-xs font-bold text-[#0D1B3E] uppercase tracking-wider">Policy Summary</h3>
            </div>
            <div className="divide-y divide-[#E2E8F0]">
              <div className="p-4 flex justify-between items-center">
                <span className="text-sm font-medium text-slate-600">Active Policies</span>
                <span className="text-sm font-black text-[#0D1B3E]">3</span>
              </div>
              <div className="p-4 flex justify-between items-center">
                <span className="text-sm font-medium text-slate-600">Open Claims</span>
                <span className="text-sm font-black text-[#0D1B3E]">2</span>
              </div>
              <div className="p-4 flex justify-between items-center">
                <span className="text-sm font-medium text-slate-600">Total Cover</span>
                <span className="text-sm font-black text-[#0052FF]">OMR 2.5M</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Personal Info */}
          <div className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-base font-bold text-[#0D1B3E] flex items-center gap-2">
                <User className="h-5 w-5 text-blue-500" /> Personal Information
              </h3>
              <button className="text-xs font-bold text-[#0052FF] hover:underline">Edit</button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Full Name</label>
                <p className="text-sm font-medium text-[#0D1B3E] mt-1">Fatima Al Lawati</p>
              </div>
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Date of Birth</label>
                <p className="text-sm font-medium text-[#0D1B3E] mt-1">12 Nov 1985</p>
              </div>
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">National ID</label>
                <p className="text-sm font-medium text-[#0D1B3E] mt-1">1029384756</p>
              </div>
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Preferred Language</label>
                <p className="text-sm font-medium text-[#0D1B3E] mt-1">English</p>
              </div>
            </div>
          </div>

          {/* Contact & Address */}
          <div className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-base font-bold text-[#0D1B3E] flex items-center gap-2">
                <MapPin className="h-5 w-5 text-emerald-500" /> Contact & Address
              </h3>
              <button className="text-xs font-bold text-[#0052FF] hover:underline">Edit</button>
            </div>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <Mail className="h-4 w-4 text-slate-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-[#0D1B3E]">fatima.lawati@email.com</p>
                  <p className="text-[10px] text-slate-500">Primary Email</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Phone className="h-4 w-4 text-slate-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-[#0D1B3E]">+968 9912 3456</p>
                  <p className="text-[10px] text-slate-500">Primary Mobile</p>
                </div>
              </div>
              <div className="flex items-start gap-3 pt-4 border-t border-slate-100">
                <MapPin className="h-4 w-4 text-slate-400 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-[#0D1B3E]">Villa 42, Way 1502, Al Qurum</p>
                  <p className="text-sm font-medium text-[#0D1B3E]">Muscat, Oman</p>
                  <p className="text-[10px] text-slate-500 mt-1">Residential Address</p>
                </div>
              </div>
            </div>
          </div>

          {/* Security */}
          <div className="bg-white border border-[#E2E8F0] rounded-[24px] p-6 shadow-sm">
            <h3 className="text-base font-bold text-[#0D1B3E] flex items-center gap-2 mb-6">
              <Shield className="h-5 w-5 text-purple-500" /> Security
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 border border-[#E2E8F0] rounded-xl hover:border-blue-200 transition-colors cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 bg-slate-50 rounded-lg flex items-center justify-center"><Lock className="h-5 w-5 text-slate-600" /></div>
                  <div>
                    <p className="text-sm font-bold text-[#0D1B3E]">Password</p>
                    <p className="text-xs text-slate-500">Last changed 6 months ago</p>
                  </div>
                </div>
                <button className="text-xs font-bold text-[#0052FF]">Update</button>
              </div>
              <div className="flex justify-between items-center p-4 border border-[#E2E8F0] rounded-xl hover:border-blue-200 transition-colors cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 bg-emerald-50 rounded-lg flex items-center justify-center"><Shield className="h-5 w-5 text-emerald-600" /></div>
                  <div>
                    <p className="text-sm font-bold text-[#0D1B3E]">Two-Factor Authentication</p>
                    <p className="text-xs text-emerald-600 font-medium">Enabled</p>
                  </div>
                </div>
                <button className="text-xs font-bold text-slate-400 hover:text-[#0D1B3E]">Manage</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

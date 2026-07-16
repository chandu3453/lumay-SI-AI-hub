"use client";

import { CreditCard, Download, Clock, DollarSign, CheckCircle2, AlertCircle } from "lucide-react";

const SYNTHETIC_PAYMENTS = [
  { id: "PAY-001", policy: "Motor Comprehensive", id_ref: "POL-99281-22", amount: "OMR 850", date: "28 May 2026", status: "Paid", method: "Visa •••• 4242" },
  { id: "PAY-002", policy: "Medical Elite", id_ref: "POL-44332-22", amount: "OMR 1,200", date: "31 Dec 2025", status: "Paid", method: "Mastercard •••• 5555" },
  { id: "PAY-003", policy: "Travel Global", id_ref: "POL-77112-22", amount: "OMR 180", date: "01 Sep 2025", status: "Paid", method: "Apple Pay" }
];

export default function CustomerPaymentsPage() {
  return (
    <div className="p-6 sm:p-8 space-y-8 animate-fade-in max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl font-black text-[#0D1B3E]">Payments</h1>
        <p className="text-sm text-slate-500 mt-1">Manage your premiums, billing history, and payment methods.</p>
      </div>

      {/* Top Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-[#0d1b3e] to-[#0038ff] p-6 rounded-[24px] text-white shadow-xl relative overflow-hidden">
          <div className="relative z-10">
            <p className="text-sm font-semibold text-blue-200">Outstanding Premium</p>
            <h2 className="text-4xl font-black mt-2 mb-1">OMR 120</h2>
            <p className="text-xs text-blue-100 flex items-center gap-1.5"><AlertCircle className="h-3.5 w-3.5" /> Due on 25 Jun 2026</p>
            <button className="mt-6 w-full py-2.5 bg-white text-[#0052FF] rounded-xl text-sm font-bold shadow-sm hover:bg-blue-50 transition-colors">
              Pay Premium Now
            </button>
          </div>
          <CreditCard className="absolute -right-6 -bottom-6 h-32 w-32 text-white opacity-10" />
        </div>
        
        <div className="md:col-span-2 bg-white border border-[#E2E8F0] rounded-[24px] shadow-sm p-6">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-base font-bold text-[#0D1B3E]">Payment Methods</h3>
            <button className="text-xs font-bold text-[#0052FF] hover:underline">Add New Card</button>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 rounded-2xl border border-blue-200 bg-blue-50/50">
              <div className="flex items-center gap-4">
                <div className="h-10 w-16 bg-white rounded-lg border border-[#E2E8F0] flex items-center justify-center font-black italic text-blue-900 shadow-sm">VISA</div>
                <div>
                  <p className="text-sm font-bold text-[#0D1B3E]">•••• •••• •••• 4242</p>
                  <p className="text-xs text-slate-500">Expires 12/28 <span className="mx-2 text-slate-300">•</span> Auto Pay Enabled</p>
                </div>
              </div>
              <span className="text-xs font-bold text-[#0052FF] bg-blue-100 px-2.5 py-1 rounded-full">Default</span>
            </div>
          </div>
        </div>
      </div>

      {/* Payment History */}
      <div className="bg-white border border-[#E2E8F0] rounded-[24px] shadow-sm overflow-hidden">
        <div className="p-6 border-b border-[#E2E8F0] flex items-center justify-between bg-slate-50/50">
          <h3 className="text-base font-bold text-[#0D1B3E]">Payment History</h3>
          <button className="flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-[#0D1B3E]">
            <Download className="h-4 w-4" /> Download Statement
          </button>
        </div>
        <div className="p-0">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[#E2E8F0]">
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Transaction ID</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Policy</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Method</th>
                <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8F0]">
              {SYNTHETIC_PAYMENTS.map((payment) => (
                <tr key={payment.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono font-medium text-[#0D1B3E]">{payment.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <p className="text-sm font-bold text-[#0D1B3E]">{payment.policy}</p>
                    <p className="text-[10px] text-slate-500 font-mono mt-0.5">{payment.id_ref}</p>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{payment.date}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-black text-[#0D1B3E]">{payment.amount}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">{payment.method}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <button className="px-3 py-1.5 rounded-lg border border-[#E2E8F0] text-xs font-bold text-slate-600 hover:bg-slate-50 transition-colors inline-flex items-center gap-1.5">
                      <Download className="h-3.5 w-3.5" /> Receipt
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

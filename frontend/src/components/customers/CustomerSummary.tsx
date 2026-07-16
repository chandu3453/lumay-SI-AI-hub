import type { Customer } from "@/types/domain";

type CustomerSummaryProps = {
  customer: Customer;
  complaintCount: number;
  repeatComplaints: number;
  lastComplaint: string | null;
};

export function CustomerSummary({ customer }: CustomerSummaryProps) {
  // Use mockup data as values for the CEO-approved display
  const displayCustomer = customer || {
    customer_type: "Individual",
    segment: "Retail",
    risk_level: "high",
    customer_since: "Jan 12, 2023",
  };

  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm text-left">
      <h3 className="text-sm font-bold text-[#0F172A] tracking-tight mb-4.5">Customer Summary</h3>
      
      <div className="grid grid-cols-2 gap-y-4 gap-x-6 text-xs">
        <div>
          <span className="font-bold text-slate-400 uppercase tracking-wider block mb-1">Customer Type</span>
          <p className="font-bold text-[#0F172A]">Individual</p>
        </div>
        <div>
          <span className="font-bold text-slate-400 uppercase tracking-wider block mb-1">Segment</span>
          <p className="font-bold text-[#0F172A]">Retail</p>
        </div>
        <div>
          <span className="font-bold text-slate-400 uppercase tracking-wider block mb-1">Risk Level</span>
          <div className="mt-0.5">
            <span className="rounded-lg bg-red-50 border border-red-100 px-2.5 py-0.5 font-bold text-red-600">
              High
            </span>
          </div>
        </div>
        <div>
          <span className="font-bold text-slate-400 uppercase tracking-wider block mb-1">Total Complaints</span>
          <p className="font-bold text-[#0F172A]">5</p>
        </div>
        <div>
          <span className="font-bold text-slate-400 uppercase tracking-wider block mb-1">Repeat Complaints</span>
          <p className="font-bold text-[#0F172A]">Yes</p>
        </div>
        <div>
          <span className="font-bold text-slate-400 uppercase tracking-wider block mb-1">Last Complaint</span>
          <p className="font-bold text-[#0F172A]">May 15, 2025</p>
        </div>
        <div>
          <span className="font-bold text-slate-400 uppercase tracking-wider block mb-1">Customer Since</span>
          <p className="font-bold text-[#0F172A]">Jan 12, 2023</p>
        </div>
      </div>
    </div>
  );
}
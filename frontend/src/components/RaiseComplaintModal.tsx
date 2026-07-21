import { useState } from "react";
import { X, Upload, Loader2 } from "lucide-react";
import { api } from "@/lib/http";

interface RaiseComplaintModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  customerId?: string;
}

export default function RaiseComplaintModal({ isOpen, onClose, onSuccess, customerId }: RaiseComplaintModalProps) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    category: "general",
    priority: "medium",
    source: "web_form",
    description: "",
    policy_number: "",
    claim_number: "",
  });

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      // Map frontend category to backend fields
      const isProduct = ["motor", "medical", "travel", "home", "life"].includes(formData.category);
      const backendCategory = isProduct ? "general" : formData.category;
      const backendProduct = isProduct ? formData.category : undefined;

      await api.post("/complaints", {
        customer_id: customerId,
        title: formData.title,
        description: formData.description,
        category: backendCategory,
        product: backendProduct,
        priority: formData.priority,
        source: "portal", // Filed directly through the customer portal form
        channel: formData.source, // What they selected as preferred channel
        policy_number: formData.policy_number || undefined,
        claim_number: formData.claim_number || undefined,
      });
      onSuccess();
      onClose();
    } catch (error) {
      console.error("Failed to raise complaint", error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-3xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto animate-slide-up">
        <div className="flex items-center justify-between p-6 border-b border-[#E2E8F0] sticky top-0 bg-white/95 backdrop-blur z-10">
          <div>
            <h2 className="text-xl font-black text-[#0D1B3E]">Raise a Complaint</h2>
            <p className="text-xs text-slate-500 mt-1">Please provide details so we can resolve your issue quickly.</p>
          </div>
          <button onClick={onClose} className="h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 hover:bg-slate-200 transition-colors">
            <X className="h-4 w-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-5">
            <div className="space-y-2">
              <label className="text-xs font-bold text-[#0D1B3E] uppercase tracking-wider">Complaint Category</label>
              <select name="category" value={formData.category} onChange={handleChange} className="w-full h-11 px-4 bg-slate-50 border border-[#E2E8F0] rounded-xl text-sm focus:outline-none focus:border-[#0052FF] focus:bg-white transition-all font-medium text-slate-700 appearance-none">
                <option value="motor">Motor</option>
                <option value="medical">Medical</option>
                <option value="travel">Travel</option>
                <option value="home">Home</option>
                <option value="life">Life</option>
                <option value="billing">Billing</option>
                <option value="general">General</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <label className="text-xs font-bold text-[#0D1B3E] uppercase tracking-wider">Priority</label>
              <select name="priority" value={formData.priority} onChange={handleChange} className="w-full h-11 px-4 bg-slate-50 border border-[#E2E8F0] rounded-xl text-sm focus:outline-none focus:border-[#0052FF] focus:bg-white transition-all font-medium text-slate-700 appearance-none">
                <option value="low">Normal</option>
                <option value="medium">High</option>
                <option value="high">Urgent</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-5">
            <div className="space-y-2">
              <label className="text-xs font-bold text-[#0D1B3E] uppercase tracking-wider">Related Policy</label>
              <select name="policy_number" value={formData.policy_number} onChange={handleChange} className="w-full h-11 px-4 bg-slate-50 border border-[#E2E8F0] rounded-xl text-sm focus:outline-none focus:border-[#0052FF] focus:bg-white transition-all font-medium text-slate-700 appearance-none">
                <option value="">Select a policy...</option>
                <option value="POL-99281-22">POL-99281-22 (Motor)</option>
                <option value="POL-11234-23">POL-11234-23 (Health)</option>
              </select>
            </div>
            
            <div className="space-y-2">
              <label className="text-xs font-bold text-[#0D1B3E] uppercase tracking-wider">Related Claim (Optional)</label>
              <input type="text" name="claim_number" value={formData.claim_number} onChange={handleChange} placeholder="e.g. CLM-2024-912" className="w-full h-11 px-4 bg-slate-50 border border-[#E2E8F0] rounded-xl text-sm focus:outline-none focus:border-[#0052FF] focus:bg-white transition-all placeholder:text-slate-400 font-medium" />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold text-[#0D1B3E] uppercase tracking-wider">Subject</label>
            <input type="text" name="title" value={formData.title} onChange={handleChange} required placeholder="Brief summary of your complaint" className="w-full h-11 px-4 bg-slate-50 border border-[#E2E8F0] rounded-xl text-sm focus:outline-none focus:border-[#0052FF] focus:bg-white transition-all placeholder:text-slate-400 font-medium" />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold text-[#0D1B3E] uppercase tracking-wider">Description</label>
            <textarea name="description" value={formData.description} onChange={handleChange} required placeholder="Please provide detailed information about your issue..." rows={4} className="w-full p-4 bg-slate-50 border border-[#E2E8F0] rounded-xl text-sm focus:outline-none focus:border-[#0052FF] focus:bg-white transition-all placeholder:text-slate-400 font-medium resize-none" />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold text-[#0D1B3E] uppercase tracking-wider">Preferred Communication</label>
            <div className="flex flex-wrap gap-3">
              {['Chat', 'Voice', 'WhatsApp', 'Email'].map((channel) => (
                <label key={channel} className={`flex-1 min-w-[120px] cursor-pointer border rounded-xl p-3 text-center transition-all ${formData.source === (channel.toLowerCase() === 'chat' ? 'web_form' : channel.toLowerCase()) ? 'border-[#0052FF] bg-blue-50 text-[#0052FF] ring-2 ring-blue-100' : 'border-[#E2E8F0] hover:border-slate-300'}`}>
                  <input 
                    type="radio" 
                    name="source" 
                    value={channel.toLowerCase() === 'chat' ? 'web_form' : channel.toLowerCase()} 
                    checked={formData.source === (channel.toLowerCase() === 'chat' ? 'web_form' : channel.toLowerCase())}
                    onChange={handleChange}
                    className="hidden" 
                  />
                  <span className="text-xs font-bold">{channel}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold text-[#0D1B3E] uppercase tracking-wider">Attachments</label>
            <div className="border-2 border-dashed border-[#E2E8F0] rounded-xl p-6 flex flex-col items-center justify-center text-center cursor-pointer hover:bg-slate-50 transition-colors group">
              <div className="h-10 w-10 bg-slate-100 rounded-full flex items-center justify-center text-slate-400 group-hover:text-[#0052FF] transition-colors mb-3">
                <Upload className="h-5 w-5" />
              </div>
              <p className="text-sm font-bold text-[#0D1B3E]">Click to upload or drag and drop</p>
              <p className="text-[10px] text-slate-400 mt-1">SVG, PNG, JPG or PDF (max. 10MB)</p>
            </div>
          </div>

          <div className="pt-4 flex items-center justify-end gap-3 border-t border-[#E2E8F0]">
            <button type="button" onClick={onClose} disabled={loading} className="px-6 py-2.5 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-100 transition-colors">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="px-6 py-2.5 rounded-xl text-sm font-bold text-white bg-[#0052FF] hover:bg-blue-600 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:shadow-none flex items-center gap-2">
              {loading && <Loader2 className="h-4 w-4 animate-spin" />}
              {loading ? "Submitting..." : "Submit Complaint"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

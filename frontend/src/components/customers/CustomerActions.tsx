import { Eye, Plus, StickyNote } from "lucide-react";

type CustomerActionsProps = {
  onViewComplaints: () => void;
  onCreateComplaint: () => void;
  onAddNote: () => void;
};

export function CustomerActions({ onViewComplaints, onCreateComplaint, onAddNote }: CustomerActionsProps) {
  const btnClass = "flex-1 inline-flex items-center justify-center gap-1.5 h-10 rounded-xl border border-slate-200 bg-white text-xs font-bold text-slate-700 hover:bg-slate-50 transition-all shadow-sm active:scale-[0.98]";

  return (
    <div className="flex items-center gap-3 w-full">
      <button className={btnClass} onClick={onViewComplaints}>
        <Eye className="h-4 w-4 text-[#94A3B8]" />
        <span>View Complaints</span>
      </button>
      <button className={btnClass} onClick={onCreateComplaint}>
        <Plus className="h-4 w-4 text-[#94A3B8]" />
        <span>Create Complaint Case</span>
      </button>
      <button className={btnClass} onClick={onAddNote}>
        <StickyNote className="h-4 w-4 text-[#94A3B8]" />
        <span>Add Note</span>
      </button>
    </div>
  );
}
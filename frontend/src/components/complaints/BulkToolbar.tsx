"use client";

import { Button } from "@/components/ui/button";
import { X, UserPlus, CheckSquare, Download, Archive, Trash2 } from "lucide-react";

type BulkToolbarProps = {
  selectedCount: number;
  onClear: () => void;
  onAssign?: () => void;
  onClose?: () => void;
  onExport?: () => void;
  onArchive?: () => void;
  onDelete?: () => void;
};

export function BulkToolbar({ selectedCount, onClear, onAssign, onClose, onExport, onArchive, onDelete }: BulkToolbarProps) {
  if (selectedCount === 0) return null;

  return (
    <div className="flex items-center gap-3 px-4 py-2.5 bg-primary/5 border border-primary/20 rounded-lg animate-fade-in">
      <span className="text-sm font-medium text-primary">
        {selectedCount} selected
      </span>
      <div className="flex items-center gap-1">
        <Button variant="ghost" size="sm" className="h-7 text-xs gap-1" onClick={onAssign}>
          <UserPlus className="h-3.5 w-3.5" />
          Assign
        </Button>
        <Button variant="ghost" size="sm" className="h-7 text-xs gap-1" onClick={onClose}>
          <CheckSquare className="h-3.5 w-3.5" />
          Close
        </Button>
        <Button variant="ghost" size="sm" className="h-7 text-xs gap-1" onClick={onExport}>
          <Download className="h-3.5 w-3.5" />
          Export
        </Button>
        <Button variant="ghost" size="sm" className="h-7 text-xs gap-1" onClick={onArchive}>
          <Archive className="h-3.5 w-3.5" />
          Archive
        </Button>
        <Button variant="ghost" size="sm" className="h-7 text-xs gap-1 text-destructive" onClick={onDelete}>
          <Trash2 className="h-3.5 w-3.5" />
          Delete
        </Button>
      </div>
      <Button variant="ghost" size="icon" className="h-7 w-7 ml-auto" onClick={onClear}>
        <X className="h-3.5 w-3.5" />
      </Button>
    </div>
  );
}
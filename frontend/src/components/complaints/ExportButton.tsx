"use client";

import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";

type ExportButtonProps = {
  onExport?: () => void;
  isLoading?: boolean;
};

export function ExportButton({ onExport, isLoading }: ExportButtonProps) {
  return (
    <Button variant="outline" size="sm" className="h-9 gap-2" onClick={onExport} disabled={isLoading}>
      <Download className="h-3.5 w-3.5" />
      Export
    </Button>
  );
}
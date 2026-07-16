"use client";

import { Eye, UserPlus, ArrowRightLeft, ArrowUpRight, GitBranch, ClipboardList, Archive, MoreHorizontal } from "lucide-react";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

type ComplaintCaseActionsProps = {
  onViewCase?: () => void;
  onOpenCustomer?: () => void;
  onAssign?: () => void;
  onTransfer?: () => void;
  onEscalate?: () => void;
  onViewWorkflow?: () => void;
  onViewTimeline?: () => void;
  onArchive?: () => void;
};

export function ComplaintCaseActions({
  onViewCase, onOpenCustomer, onAssign, onTransfer, onEscalate, onViewWorkflow, onViewTimeline, onArchive,
}: ComplaintCaseActionsProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuItem onClick={onViewCase}><Eye className="mr-2 h-4 w-4" />View Case</DropdownMenuItem>
        <DropdownMenuItem onClick={onOpenCustomer}><UserPlus className="mr-2 h-4 w-4" />Open Customer</DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={onAssign}><UserPlus className="mr-2 h-4 w-4" />Assign</DropdownMenuItem>
        <DropdownMenuItem onClick={onTransfer}><ArrowRightLeft className="mr-2 h-4 w-4" />Transfer</DropdownMenuItem>
        <DropdownMenuItem onClick={onEscalate}><ArrowUpRight className="mr-2 h-4 w-4" />Escalate</DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={onViewWorkflow}><GitBranch className="mr-2 h-4 w-4" />View Workflow</DropdownMenuItem>
        <DropdownMenuItem onClick={onViewTimeline}><ClipboardList className="mr-2 h-4 w-4" />View Timeline</DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={onArchive}><Archive className="mr-2 h-4 w-4" />Archive</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
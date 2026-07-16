"use client";

import { MoreHorizontal, Eye, User, GitBranch, UserPlus, Bell, ArrowUpRight, Archive } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

type AlertActionsProps = {
  onOpenComplaint?: () => void;
  onViewCustomer?: () => void;
  onViewWorkflow?: () => void;
  onAssignOfficer?: () => void;
  onAcknowledge?: () => void;
  onEscalate?: () => void;
  onArchive?: () => void;
};

export function AlertActions({
  onOpenComplaint, onViewCustomer, onViewWorkflow, onAssignOfficer, onAcknowledge, onEscalate, onArchive,
}: AlertActionsProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuItem onClick={onOpenComplaint}>
          <Eye className="mr-2 h-4 w-4" />
          Open Complaint
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onViewCustomer}>
          <User className="mr-2 h-4 w-4" />
          View Customer
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onViewWorkflow}>
          <GitBranch className="mr-2 h-4 w-4" />
          View Workflow
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={onAssignOfficer}>
          <UserPlus className="mr-2 h-4 w-4" />
          Assign Officer
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onAcknowledge}>
          <Bell className="mr-2 h-4 w-4" />
          Acknowledge Alert
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onEscalate}>
          <ArrowUpRight className="mr-2 h-4 w-4" />
          Escalate
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={onArchive}>
          <Archive className="mr-2 h-4 w-4" />
          Archive
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
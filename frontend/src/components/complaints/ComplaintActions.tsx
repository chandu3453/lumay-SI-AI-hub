"use client";

import { MoreHorizontal, Eye, UserPlus, ArrowRightLeft, ArrowUpRight, GitBranch, User, Archive, Trash2 } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

type ComplaintActionsProps = {
  onOpen?: () => void;
  onAssign?: () => void;
  onTransfer?: () => void;
  onEscalate?: () => void;
  onCreateWorkflow?: () => void;
  onViewCustomer?: () => void;
  onArchive?: () => void;
  onDelete?: () => void;
};

export function ComplaintActions({
  onOpen, onAssign, onTransfer, onEscalate, onCreateWorkflow, onViewCustomer, onArchive, onDelete,
}: ComplaintActionsProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuItem onClick={onOpen}>
          <Eye className="mr-2 h-4 w-4" />
          Open Complaint
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onAssign}>
          <UserPlus className="mr-2 h-4 w-4" />
          Assign
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onTransfer}>
          <ArrowRightLeft className="mr-2 h-4 w-4" />
          Transfer
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onEscalate}>
          <ArrowUpRight className="mr-2 h-4 w-4" />
          Escalate
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={onCreateWorkflow}>
          <GitBranch className="mr-2 h-4 w-4" />
          Create Workflow
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onViewCustomer}>
          <User className="mr-2 h-4 w-4" />
          View Customer
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={onArchive}>
          <Archive className="mr-2 h-4 w-4" />
          Archive
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onDelete} className="text-destructive">
          <Trash2 className="mr-2 h-4 w-4" />
          Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
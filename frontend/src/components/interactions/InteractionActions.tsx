"use client";

import { MoreHorizontal, Eye, UserPlus, AlertTriangle, ArrowUpRight, Archive } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

type InteractionActionsProps = {
  onOpen?: () => void;
  onAssign?: () => void;
  onCreateComplaint?: () => void;
  onEscalate?: () => void;
  onArchive?: () => void;
};

export function InteractionActions({
  onOpen,
  onAssign,
  onCreateComplaint,
  onEscalate,
  onArchive,
}: InteractionActionsProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-44">
        <DropdownMenuItem onClick={onOpen}>
          <Eye className="mr-2 h-4 w-4" />
          Open
        </DropdownMenuItem>
        <DropdownMenuItem onClick={onAssign}>
          <UserPlus className="mr-2 h-4 w-4" />
          Assign
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={onCreateComplaint}>
          <AlertTriangle className="mr-2 h-4 w-4" />
          Create Complaint
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
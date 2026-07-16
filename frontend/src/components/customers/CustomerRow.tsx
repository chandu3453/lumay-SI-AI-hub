"use client";

import { ChevronRight } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import type { Customer } from "@/types/domain";

const riskVariant: Record<string, "success" | "warning" | "destructive" | "neutral" | "default"> = {
  low: "success", medium: "warning", high: "destructive", critical: "destructive",
};

function getInitials(name: string): string {
  return name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2);
}

type CustomerRowProps = {
  item: Customer;
  isSelected: boolean;
  onSelect: (item: Customer) => void;
};

export function CustomerRow({ item, isSelected, onSelect }: CustomerRowProps) {
  return (
    <tr
      onClick={() => onSelect(item)}
      className={`transition-colors hover:bg-muted/20 animate-fade-up cursor-pointer ${isSelected ? "bg-primary/5" : ""}`}
    >
      <td className="px-4 py-3 text-sm w-[48px]">
        <Avatar className="h-8 w-8">
          <AvatarFallback className="text-xs bg-primary/10 text-primary">{getInitials(item.full_name)}</AvatarFallback>
        </Avatar>
      </td>
      <td className="px-4 py-3 text-sm w-[170px]">
        <p className="text-sm font-medium truncate max-w-[160px]">{item.full_name}</p>
        <p className="text-xs text-muted-foreground truncate max-w-[160px]">{item.customer_number ?? `#${item.id.slice(0, 8)}`}</p>
      </td>
      <td className="px-4 py-3 text-sm w-[150px]">
        <p className="text-xs text-muted-foreground truncate max-w-[140px]">{item.email ?? "—"}</p>
        <p className="text-xs text-muted-foreground truncate max-w-[140px]">{item.mobile_number ?? "—"}</p>
      </td>
      <td className="px-4 py-3 text-sm w-[100px]">
        {item.risk_level ? <Badge variant={riskVariant[item.risk_level] ?? "neutral"} className="capitalize">{item.risk_level}</Badge> : <span className="text-sm text-muted-foreground">—</span>}
      </td>
      <td className="px-4 py-3 text-sm w-[90px] text-center">
        <span className="text-sm font-medium">{item.complaint_count ?? 0}</span>
      </td>
      <td className="px-4 py-3 text-sm w-[130px]">
        <span className="text-sm text-muted-foreground truncate max-w-[120px] block">{item.last_interaction ?? "—"}</span>
      </td>
      <td className="px-4 py-3 text-sm w-[40px]">
        <ChevronRight className="h-4 w-4 text-muted-foreground" />
      </td>
    </tr>
  );
}
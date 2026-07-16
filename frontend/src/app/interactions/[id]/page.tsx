"use client";

import { useParams, useRouter } from "next/navigation";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { AICopilot } from "@/features/ai-copilot/ai-copilot";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useComplaintDetail } from "@/features/complaints/hooks/use-complaint-detail";
import { InsuranceBadge } from "@/components/insurance/InsuranceBadge";
import { ArrowLeft, Phone, Mail, MessageCircle, Globe, Radio, Clock, User, ChevronRight, FileText } from "lucide-react";
import Link from "next/link";

const channelIcons: Record<string, React.ReactNode> = {
  voice: <Phone className="h-4 w-4" />, whatsapp: <MessageCircle className="h-4 w-4" />,
  email: <Mail className="h-4 w-4" />, web_chat: <Globe className="h-4 w-4" />,
  smart_call: <Radio className="h-4 w-4" />, crm: <FileText className="h-4 w-4" />,
  survey: <FileText className="h-4 w-4" />, manual: <FileText className="h-4 w-4" />,
};

export default function InteractionDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const router = useRouter();
  const { data: c, isLoading } = useComplaintDetail(id);

  if (isLoading) return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in">
        <Skeleton className="h-16 w-full rounded-xl" />
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
      <AICopilot />
    </DashboardShell>
  );

  const interaction = c?.interactions?.find((ix) => ix.id === id) ?? c?.interactions?.[0];

  return (
    <DashboardShell>
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center gap-3">
          <button onClick={() => router.back()} className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors">
            <ArrowLeft className="h-4 w-4" /> Back
          </button>
          <span className="text-muted-foreground">/</span>
          <span className="text-sm font-medium text-[#0F172A]">Interaction</span>
        </div>

        {interaction ? (
          <div className="grid grid-cols-[1fr_320px] gap-6">
            <div className="space-y-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-3">
                  <div>
                    <CardTitle className="text-sm font-semibold text-[#0F172A]">{interaction.subject}</CardTitle>
                    <p className="text-xs text-muted-foreground mt-0.5">ID: {interaction.id}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {channelIcons[interaction.channel] && (
                      <Badge variant="outline" className="flex items-center gap-1.5 capitalize">
                        {channelIcons[interaction.channel]}{interaction.channel.replace("_", " ")}
                      </Badge>
                    )}
                    <Badge variant={interaction.direction === "inbound" ? "default" : "secondary"}>
                      {interaction.direction}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <p className="text-sm text-[#0F172A] leading-relaxed">{interaction.summary}</p>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground pt-2 border-t border-border">
                    <span className="flex items-center gap-1.5"><Clock className="h-3.5 w-3.5" />{interaction.timestamp}</span>
                    <span className="flex items-center gap-1.5"><User className="h-3.5 w-3.5" />{interaction.agent}</span>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="space-y-4">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-semibold text-[#0F172A]">Related Complaint</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {c ? (
                    <>
                      <Link href={`/complaint-cases/${c.id}`} className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-accent transition-colors">
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-[#0F172A] truncate">{c.complaint_number}</p>
                          <p className="text-xs text-muted-foreground truncate">{c.title}</p>
                        </div>
                        <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0" />
                      </Link>
                      <div className="flex items-center gap-2">
                        <InsuranceBadge line={c.insurance_line} />
                        {c.severity && <Badge variant="outline" className="capitalize">{c.severity}</Badge>}
                        {c.status && <Badge variant="secondary" className="capitalize">{c.status}</Badge>}
                      </div>
                    </>
                  ) : (
                    <p className="text-sm text-muted-foreground">No related complaint found</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center py-20">
            <p className="text-sm text-muted-foreground">Interaction not found</p>
          </div>
        )}
      </div>
      <AICopilot />
    </DashboardShell>
  );
}

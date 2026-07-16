import {
  Folder,
  Clock,
  Smile,
  Timer,
  MessageCircle,
  AlertTriangle,
} from "lucide-react";
import { ReportCard } from "./report-card";

const templates = [
  {
    icon: <Folder className="h-5 w-5 text-blue-600" />,
    iconBg: "bg-blue-50 border border-blue-100",
    title: "Complaint Overview",
    description: "Summary of all complaints including total volume, status breakdown, resolution rates and MoM trends.",
  },
  {
    icon: <Clock className="h-5 w-5 text-amber-600" />,
    iconBg: "bg-amber-50 border border-amber-100",
    title: "SLA Performance",
    description: "SLA compliance rates, breach analysis, response and resolution time metrics against contractual targets.",
  },
  {
    icon: <Smile className="h-5 w-5 text-green-600" />,
    iconBg: "bg-green-50 border border-green-100",
    title: "Sentiment Analysis",
    description: "Customer sentiment distribution across channels, NPS trends and emotional trajectory analysis.",
  },
  {
    icon: <Timer className="h-5 w-5 text-purple-600" />,
    iconBg: "bg-purple-50 border border-purple-100",
    title: "Theme & Root Cause",
    description: "Most frequent complaint categories, emerging issue patterns and root cause breakdown.",
  },
  {
    icon: <MessageCircle className="h-5 w-5 text-cyan-600" />,
    iconBg: "bg-cyan-50 border border-cyan-100",
    title: "Channel Performance",
    description: "Complaint volume, resolution efficiency and sentiment metrics across all communication channels.",
  },
  {
    icon: <AlertTriangle className="h-5 w-5 text-red-600" />,
    iconBg: "bg-red-50 border border-red-100",
    title: "Escalation & Risk",
    description: "Escalation patterns, high-risk case trends, regulatory flags and SLA breach correlation.",
  },
];

export function ReportTemplates() {
  return (
    <div className="text-left">
      <h2 className="text-sm font-extrabold text-[#0F172A] tracking-tight mb-4">Report Templates</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-5">
        {templates.map((t) => (
          <ReportCard
            key={t.title}
            icon={t.icon}
            iconBg={t.iconBg}
            title={t.title}
            description={t.description}
            onGenerate={() => {}}
          />
        ))}
      </div>
    </div>
  );
}
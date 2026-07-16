import {
  Tags,
  Clock,
  GitBranch,
  Users,
  Radio,
  Sliders,
  Bell,
  FileText,
  Database,
  PenSquare,
  Brain,
  Shield,
  ChevronRight,
} from "lucide-react";

type ConfigCardItem = {
  id: string;
  icon: React.ReactNode;
  iconBg: string;
  iconColor: string;
  title: string;
  subtitle: string;
  linkText: string;
};

const CONFIG_CARDS: ConfigCardItem[] = [
  {
    id: "1",
    icon: <Tags className="h-5 w-5" />,
    iconBg: "bg-purple-50 border border-purple-100",
    iconColor: "text-purple-600",
    title: "Categories & Taxonomy",
    subtitle: "Manage complaint themes, sub-themes, products and issue classification.",
    linkText: "56 Categories",
  },
  {
    id: "2",
    icon: <Clock className="h-5 w-5" />,
    iconBg: "bg-amber-50 border border-amber-100",
    iconColor: "text-amber-600",
    title: "SLA & Deadlines",
    subtitle: "Configure SLA targets, business hours, escalation rules and reminders.",
    linkText: "18 SLA Policies",
  },
  {
    id: "3",
    icon: <GitBranch className="h-5 w-5" />,
    iconBg: "bg-green-50 border border-green-100",
    iconColor: "text-green-600",
    title: "Routing & Escalation",
    subtitle: "Set assignment rules, escalation matrix and auto-routing conditions.",
    linkText: "14 Routing Rules",
  },
  {
    id: "4",
    icon: <Users className="h-5 w-5" />,
    iconBg: "bg-blue-50 border border-blue-100",
    iconColor: "text-blue-600",
    title: "Users & Roles",
    subtitle: "Manage users, roles, permissions and access control.",
    linkText: "128 Users • 18 Roles",
  },
  {
    id: "5",
    icon: <Radio className="h-5 w-5" />,
    iconBg: "bg-red-50 border border-red-100",
    iconColor: "text-red-600",
    title: "Channels & Sources",
    subtitle: "Configure data sources, channel connectors and ingestion settings.",
    linkText: "9 Channels",
  },
  {
    id: "6",
    icon: <Sliders className="h-5 w-5" />,
    iconBg: "bg-cyan-50 border border-cyan-100",
    iconColor: "text-cyan-600",
    title: "System Settings",
    subtitle: "Configure global preferences, thresholds and AI model settings.",
    linkText: "32 Settings",
  },
  {
    id: "7",
    icon: <Bell className="h-5 w-5" />,
    iconBg: "bg-amber-50 border border-amber-100",
    iconColor: "text-amber-600",
    title: "Notification Settings",
    subtitle: "Configure alerts, notifications, templates and delivery rules.",
    linkText: "24 Notification Rules",
  },
  {
    id: "8",
    icon: <FileText className="h-5 w-5" />,
    iconBg: "bg-purple-50 border border-purple-100",
    iconColor: "text-purple-600",
    title: "Templates & Responses",
    subtitle: "Manage email/SMS templates and standard response libraries.",
    linkText: "42 Templates",
  },
  {
    id: "9",
    icon: <Database className="h-5 w-5" />,
    iconBg: "bg-blue-50 border border-blue-100",
    iconColor: "text-blue-600",
    title: "Data Retention",
    subtitle: "Set data retention policies, archival rules and purge schedules.",
    linkText: "7 Retention Policies",
  },
  {
    id: "10",
    icon: <PenSquare className="h-5 w-5" />,
    iconBg: "bg-green-50 border border-green-100",
    iconColor: "text-green-600",
    title: "Custom Fields",
    subtitle: "Create and manage custom fields for cases and customers.",
    linkText: "23 Custom Fields",
  },
  {
    id: "11",
    icon: <Brain className="h-5 w-5" />,
    iconBg: "bg-purple-50 border border-purple-100",
    iconColor: "text-purple-600",
    title: "AI & Detection Settings",
    subtitle: "Configure complaint detection, sentiment, severity and risk thresholds.",
    linkText: "15 AI Rules",
  },
  {
    id: "12",
    icon: <Shield className="h-5 w-5" />,
    iconBg: "bg-amber-50 border border-amber-100",
    iconColor: "text-amber-600",
    title: "Security & Compliance",
    subtitle: "Manage audit settings, data privacy and compliance controls.",
    linkText: "6 Policies",
  },
];

export function ConfigurationGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5 text-left">
      {CONFIG_CARDS.map((card) => (
        <div key={card.id} className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm hover:shadow-md hover:border-slate-300 transition-all flex flex-col justify-between h-[210px] w-full">
          <div>
            {/* Circular badge container */}
            <div className={`h-11 w-11 rounded-2xl flex items-center justify-center shrink-0 border ${card.iconBg} ${card.iconColor}`}>
              {card.icon}
            </div>
            
            {/* Text Title */}
            <h4 className="text-sm font-extrabold text-[#0F172A] mt-3.5 tracking-tight">{card.title}</h4>
            <p className="text-[11px] font-semibold text-slate-400 leading-relaxed mt-1.5">{card.subtitle}</p>
          </div>

          {/* Link button at bottom */}
          <div className="flex items-center justify-between mt-4">
            <span className="text-xs font-bold text-[#0052FF] hover:underline cursor-pointer">
              {card.linkText}
            </span>
            <ChevronRight className="h-4 w-4 text-[#94A3B8]" />
          </div>
        </div>
      ))}
    </div>
  );
}
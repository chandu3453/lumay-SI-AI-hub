import { useMemo } from "react";
import Link from "next/link";
import { Tag } from "lucide-react";
import { ROUTES } from "@/lib/constants";
import { useThemeDistribution } from "@/features/analytics/use-analytics";

type ThemeRow = { category: string; count: number; percent: number };

export function ComplaintThemes() {
  const { data } = useThemeDistribution(30);

  const themes = useMemo<ThemeRow[]>(() => {
    const distribution = (data?.distribution ?? []) as { label: string; count: number }[];
    const top = [...distribution].sort((a, b) => b.count - a.count).slice(0, 5);
    const max = top[0]?.count || 1;
    return top.map((t) => ({ category: t.label, count: t.count, percent: Math.round((t.count / max) * 100) }));
  }, [data]);

  return (
    <div className="rounded-2xl border border-[#E2E8F0] bg-white p-6 shadow-sm flex flex-col h-96">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-sm font-bold text-[#0F172A] tracking-tight">Top Complaint Themes</h3>
        <Link
          href={ROUTES.COMPLAINTS}
          className="text-xs font-bold text-[#0052FF] hover:underline"
        >
          View all
        </Link>
      </div>

      {/* Progress Bars List */}
      <div className="flex-1 flex flex-col justify-between py-1.5">
        {themes.length === 0 ? (
          <p className="text-xs font-semibold text-slate-400 text-center py-8">
            No theme data available yet.
          </p>
        ) : (
          themes.map((theme) => (
            <div key={theme.category} className="space-y-1.5">
              <div className="flex items-center justify-between text-xs font-bold">
                <div className="flex items-center gap-2">
                  <Tag className="h-3.5 w-3.5 text-[#64748B]" />
                  <span className="text-[#0F172A]">{theme.category}</span>
                </div>
                <span className="text-[#64748B]">{theme.count}</span>
              </div>
              <div className="h-1.5 rounded-full bg-[#F1F5F9] overflow-hidden">
                <div
                  className="h-full rounded-full bg-[#0052FF] transition-all duration-500"
                  style={{ width: `${theme.percent}%` }}
                />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
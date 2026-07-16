type ComplaintThemesProps = {
  themes: { theme: string; count: number; percentage: number }[];
  isLoading: boolean;
};

const MOCK_THEMES = [
  { theme: "Claim Delays", count: 3, percentage: 100 },
  { theme: "Service Quality", count: 1, percentage: 33 },
  { theme: "Payments & Refunds", count: 1, percentage: 33 },
];

export function ComplaintThemes({ isLoading }: ComplaintThemesProps) {
  return (
    <div className="bg-white border border-[#E2E8F0] rounded-2xl p-5 shadow-sm text-left flex flex-col h-52 justify-between">
      <h3 className="text-xs font-bold text-[#0F172A] tracking-tight mb-3">Top Complaint Themes</h3>
      
      <div className="flex-1 flex flex-col justify-around py-1">
        {MOCK_THEMES.map((theme) => (
          <div key={theme.theme} className="space-y-1">
            <div className="flex items-center justify-between text-xs font-bold">
              <span className="text-[#0F172A]">{theme.theme}</span>
              <span className="text-slate-400">{theme.count}</span>
            </div>
            <div className="h-1 rounded-full bg-[#F1F5F9] overflow-hidden">
              <div
                className="h-full rounded-full bg-red-500 transition-all duration-500"
                style={{ width: `${theme.percentage}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
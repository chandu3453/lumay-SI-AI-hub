"use client";

import { useState, useRef, useEffect } from "react";
import { Search, Clock, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { ROUTES } from "@/lib/constants";

const STORAGE_KEY = "recent-searches";

function loadRecentSearches(): string[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch {
    return [];
  }
}

function saveRecentSearches(searches: string[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(searches));
}

export function GlobalSearch() {
  const [query, setQuery] = useState("");
  const [recentSearches, setRecentSearches] = useState<string[]>(loadRecentSearches);
  const [focused, setFocused] = useState(false);
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setFocused(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function navigateTo(term: string) {
    const trimmed = term.trim();
    if (!trimmed) return;
    const updated = [trimmed, ...recentSearches.filter((s) => s !== trimmed)].slice(0, 5);
    setRecentSearches(updated);
    saveRecentSearches(updated);
    setQuery("");
    setFocused(false);
    router.push(`${ROUTES.SEARCH}?q=${encodeURIComponent(trimmed)}`);
  }

  function removeRecent(term: string) {
    const updated = recentSearches.filter((s) => s !== term);
    setRecentSearches(updated);
    saveRecentSearches(updated);
  }

  const showDropdown = focused && !query && recentSearches.length > 0;

  return (
    <div className="relative flex-1 max-w-sm" ref={containerRef}>
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#94A3B8]" />
      <input
        type="text"
        placeholder="Search complaints, customers, workflows..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => setFocused(true)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            navigateTo(query);
          }
        }}
        className="flex h-9 w-full rounded-lg border border-[#E2E8F0] bg-[#F8FAFC] pl-9 pr-3 text-sm text-[#0F172A] placeholder:text-[#94A3B8] outline-none transition-colors focus:border-[#2563EB] focus:bg-white focus:ring-1 focus:ring-[#2563EB]"
      />
      {showDropdown && (
        <div className="absolute top-full left-0 right-0 mt-1 rounded-lg border border-[#E2E8F0] bg-white shadow-lg z-50 py-1">
          <p className="px-3 py-1.5 text-xs font-medium text-[#64748B] uppercase tracking-wider">Recent Searches</p>
          {recentSearches.map((term) => (
            <div
              key={term}
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-[#0F172A] hover:bg-[#F1F5F9] cursor-pointer group"
              onClick={() => navigateTo(term)}
            >
              <Clock className="h-3.5 w-3.5 text-[#94A3B8] shrink-0" />
              <span className="flex-1 truncate">{term}</span>
              <button
                onClick={(e) => { e.stopPropagation(); removeRecent(term); }}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 rounded hover:bg-[#E2E8F0]"
              >
                <X className="h-3 w-3 text-[#94A3B8]" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
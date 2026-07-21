"use client";

import { useEffect, useState } from "react";

export type CustomerSession = { id: string; email: string; name: string };

/** Reads the same `customer-session` storage key the customer layout/login/
 * dashboard already use — the single source of truth for "who is the
 * logged-in customer" across the customer portal (no backend session yet,
 * see `frontend/src/lib/http.ts`'s customer-route token skip). */
export function useCustomerSession(): CustomerSession | null {
  const [session, setSession] = useState<CustomerSession | null>(null);

  useEffect(() => {
    const raw = sessionStorage.getItem("customer-session") || localStorage.getItem("customer-session");
    if (raw) {
      try {
        setSession(JSON.parse(raw));
      } catch {
        setSession(null);
      }
    }
  }, []);

  return session;
}
